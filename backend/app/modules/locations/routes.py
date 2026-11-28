"""Location routes (Phase 3)."""
import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.modules.locations.models import LocationModel
from app.modules.locations.schema import (
    LocationCreate,
    LocationListResponse,
    LocationResponse,
    LocationUpdate,
    LocationWithEnvironmentalData,
)
from app.modules.locations.service import LocationService
from app.modules.users.routes import get_current_active_user
from app.modules.users.models import UserModel
from app.modules.air_quality_readings.schema import AirQualityReadingResponse
from app.modules.air_quality_readings.service import AirQualityService
from app.modules.weather_readings.schema import WeatherReadingResponse
from app.modules.weather_readings.service import WeatherService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["locations"])


@router.get("", response_model=LocationListResponse)
async def list_locations(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    default_only: bool = Query(False, description="Return only default location"),
):
    """List all locations for the current user."""
    service = LocationService(session)
    locations = await service.get_by_user(current_user.id, include_default_only=default_only)
    return LocationListResponse(locations=locations, total=len(locations))


@router.get("/default", response_model=LocationResponse)
async def get_default_location(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Get the current user's default location."""
    service = LocationService(session)
    location = await service.get_default_location(current_user.id)
    if not location:
        raise HTTPException(status_code=404, detail="No default location set")
    return location


@router.get("/search")
async def search_locations(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=20, description="Maximum results"),
):
    """Search locations (saved + geocoding)."""
    service = LocationService(session)
    results = await service.search_locations(q, current_user.id, limit)
    return {"results": results}


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Create a new location for the current user and sync initial environmental data."""
    service = LocationService(session)
    location = await service.create(current_user.id, location_data)
    await session.commit()
    await session.refresh(location)

    # Best-effort initial sync so dashboard has readings immediately after onboarding
    try:
        await AirQualityService(session).sync_location_data(location.id)
        await session.commit()
    except Exception as exc:
        await session.rollback()
        logger.warning("Initial AQI sync failed for location %s: %s", location.id, exc)

    try:
        await WeatherService(session).sync_location_data(location.id)
        await session.commit()
    except Exception as exc:
        await session.rollback()
        logger.warning("Initial weather sync failed for location %s: %s", location.id, exc)

    return location


@router.get("/{location_id}", response_model=LocationWithEnvironmentalData)
async def get_location(
    location_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Get a location with latest environmental data."""
    service = LocationService(session)
    location = await service.get_by_id(location_id)
    if not location or location.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Location not found")

    aqi_service = AirQualityService(session)
    weather_service = WeatherService(session)

    latest_aqi = await aqi_service.get_latest_reading(location_id)
    latest_weather = await weather_service.get_latest_reading(location_id)

    loc_data = LocationResponse.model_validate(location).model_dump()
    return LocationWithEnvironmentalData(
        **loc_data,
        latest_aqi=(
            AirQualityReadingResponse.model_validate(latest_aqi).model_dump()
            if latest_aqi
            else None
        ),
        latest_weather=(
            WeatherReadingResponse.model_validate(latest_weather).model_dump()
            if latest_weather
            else None
        ),
    )


@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: UUID,
    location_data: LocationUpdate,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Update a location."""
    service = LocationService(session)
    location = await service.update(location_id, current_user.id, location_data)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    await session.commit()
    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Delete a location."""
    service = LocationService(session)
    success = await service.delete(location_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Location not found")
    await session.commit()


@router.post("/{location_id}/set-default", response_model=LocationResponse)
async def set_default_location(
    location_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Set a location as the user's default."""
    service = LocationService(session)
    location = await service.set_default(location_id, current_user.id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    await session.commit()
    return location