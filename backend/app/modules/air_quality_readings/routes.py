"""Air quality reading routes (Phase 3)."""
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.modules.air_quality_readings.models import AirQualityReadingModel
from app.modules.air_quality_readings.schema import (
    AirQualityReadingCreate,
    AirQualityReadingListResponse,
    AirQualityReadingResponse,
)
from app.modules.air_quality_readings.service import AirQualityService
from app.modules.locations.models import LocationModel
from app.modules.users.routes import get_current_active_user
from app.modules.users.models import UserModel

router = APIRouter(prefix="/air-quality", tags=["air-quality"])


@router.get("/locations/{location_id}/latest", response_model=AirQualityReadingResponse)
async def get_latest_aqi(
    location_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    provider: Optional[str] = Query(None, description="Filter by provider"),
):
    """Get the latest air quality reading for a location."""
    # Verify location belongs to user
    location_result = await session.execute(
        # Using a simple query to check ownership
        # In production, this would be a proper relationship
        LocationModel.__table__.select().where(
            LocationModel.id == location_id,
            LocationModel.user_id == current_user.id,
        )
    )
    location = location_result.mappings().first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    service = AirQualityService(session)
    reading = await service.get_latest_reading(location_id, provider)
    if not reading:
        raise HTTPException(status_code=404, detail="No air quality data available for this location")

    return reading


@router.get("/locations/{location_id}", response_model=AirQualityReadingListResponse)
async def get_aqi_history(
    location_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    start_time: Optional[datetime] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[datetime] = Query(None, description="End time (ISO format)"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of readings"),
):
    """Get air quality history for a location."""
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

    service = AirQualityService(session)
    readings = await service.get_readings(
        location_id,
        start_time=start_time,
        end_time=end_time,
        provider=provider,
        limit=limit,
    )

    return AirQualityReadingListResponse(
        readings=readings,
        total=len(readings),
        location_id=location_id,
        provider=provider,
    )


@router.post("/locations/{location_id}/sync", status_code=status.HTTP_202_ACCEPTED)
async def sync_aqi_data(
    location_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    radius_km: int = Query(25, ge=1, le=100, description="Search radius in km"),
):
    """Trigger air quality data sync from OpenAQ for a location."""
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

    service = AirQualityService(session)
    try:
        count = await service.sync_location_data(location_id, radius_km)
        await session.commit()
        return {"message": f"Synced {count} air quality readings", "count": count}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to sync from provider: {str(e)}")


@router.get("/locations/{location_id}/current-aqi-info")
async def get_current_aqi_info(
    location_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    provider: Optional[str] = Query(None, description="Filter by provider"),
):
    """Get current AQI with category, color, and health advisory."""
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

    service = AirQualityService(session)
    reading = await service.get_latest_reading(location_id, provider)
    if not reading:
        raise HTTPException(status_code=404, detail="No air quality data available for this location")

    aqi_info = service.get_aqi_info(reading.aqi_value, reading.aqi_standard)

    return {
        "reading": reading,
        "aqi_info": aqi_info.model_dump(),
        "data_age_minutes": int((datetime.now(reading.measured_at.tzinfo) - reading.measured_at).total_seconds() / 60),
        "is_stale": (datetime.now(reading.measured_at.tzinfo) - reading.measured_at).total_seconds() > 3600,  # > 1 hour
    }