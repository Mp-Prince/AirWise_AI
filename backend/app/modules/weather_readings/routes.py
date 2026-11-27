"""Weather reading routes (Phase 3)."""
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.modules.weather_readings.models import WeatherReadingModel
from app.modules.weather_readings.schema import (
    WeatherReadingCreate,
    WeatherReadingListResponse,
    WeatherReadingResponse,
)
from app.modules.weather_readings.service import WeatherService
from app.modules.locations.models import LocationModel
from app.modules.users.routes import get_current_active_user
from app.modules.users.models import UserModel

router = APIRouter(tags=["weather"])


@router.get("/locations/{location_id}/latest", response_model=WeatherReadingResponse)
async def get_latest_weather(
    location_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    provider: Optional[str] = Query(None, description="Filter by provider"),
):
    """Get the latest weather reading for a location."""
    # Verify location belongs to user
    location_result = await session.execute(
        LocationModel.__table__.select().where(
            LocationModel.id == location_id,
            LocationModel.user_id == current_user.id,
        )
    )
    location = location_result.mappings().first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    service = WeatherService(session)
    reading = await service.get_latest_reading(location_id, provider)
    if not reading:
        raise HTTPException(status_code=404, detail="No weather data available for this location")

    return reading


@router.get("/locations/{location_id}", response_model=WeatherReadingListResponse)
async def get_weather_history(
    location_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    start_time: Optional[datetime] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[datetime] = Query(None, description="End time (ISO format)"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of readings"),
):
    """Get weather history for a location."""
    # Verify location belongs to user
    location_result = await session.execute(
        LocationModel.__table__.select().where(
            LocationModel.id == location_id,
            LocationModel.user_id == current_user.id,
        )
    )
    location = location_result.mappings().first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    service = WeatherService(session)
    readings = await service.get_readings(
        location_id,
        start_time=start_time,
        end_time=end_time,
        provider=provider,
        limit=limit,
    )

    return WeatherReadingListResponse(
        readings=readings,
        total=len(readings),
        location_id=location_id,
        provider=provider,
    )


@router.post("/locations/{location_id}/sync", status_code=status.HTTP_202_ACCEPTED)
async def sync_weather_data(
    location_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Trigger weather data sync from OpenWeatherMap for a location."""
    # Verify location belongs to user
    location_result = await session.execute(
        LocationModel.__table__.select().where(
            LocationModel.id == location_id,
            LocationModel.user_id == current_user.id,
        )
    )
    location = location_result.mappings().first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    service = WeatherService(session)
    try:
        success = await service.sync_location_data(location_id)
        await session.commit()
        if success:
            return {"message": "Weather data synced successfully"}
        else:
            raise HTTPException(status_code=502, detail="Failed to fetch weather data from provider")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to sync from provider: {str(e)}")


@router.get("/locations/{location_id}/current-weather-info")
async def get_current_weather_info(
    location_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    provider: Optional[str] = Query(None, description="Filter by provider"),
):
    """Get current weather with description and UV advisory."""
    # Verify location belongs to user
    location_result = await session.execute(
        LocationModel.__table__.select().where(
            LocationModel.id == location_id,
            LocationModel.user_id == current_user.id,
        )
    )
    location = location_result.mappings().first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    service = WeatherService(session)
    reading = await service.get_latest_reading(location_id, provider)
    if not reading:
        raise HTTPException(status_code=404, detail="No weather data available for this location")

    weather_info = service.get_weather_info(reading.weather_code, reading.uv_index)

    return {
        "reading": reading,
        "weather_info": weather_info,
        "data_age_minutes": int((datetime.now(reading.measured_at.tzinfo) - reading.measured_at).total_seconds() / 60),
        "is_stale": (datetime.now(reading.measured_at.tzinfo) - reading.measured_at).total_seconds() > 3600,  # > 1 hour
    }