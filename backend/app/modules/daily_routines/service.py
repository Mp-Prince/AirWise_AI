"""Daily routine service with deterministic AQI safety bands (Phase 6)."""
from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.air_quality_readings.service import AirQualityService
from app.modules.daily_routines.models import DailyRoutineModel
from app.modules.daily_routines.repository import DailyRoutineRepository
from app.modules.daily_routines.schema import (
    DailyRoutineCreate,
    DailyRoutineListResponse,
    DailyRoutineResponse,
    DailyRoutineUpdate,
    SafetyBandType,
)
from app.modules.locations.service import LocationService
from app.modules.user_profiles.service import UserProfileService

OUTDOOR_ROUTINE_TYPES = {"commute", "exercise", "outdoor_work"}


def compute_safety_band(
    routine_type: str,
    aqi_value: Optional[int],
    is_sensitive: bool = False,
) -> tuple[SafetyBandType, str]:
    """Deterministic safety classification based on AQI and outdoor exposure."""
    if routine_type not in OUTDOOR_ROUTINE_TYPES:
        if aqi_value is None:
            return "safe", "Indoor activity (live AQI unavailable)"
        return "safe", f"Indoor activity (local AQI {aqi_value})"

    if aqi_value is None:
        return "unknown", "Live AQI unavailable — check local air quality before going out"

    caution_threshold = 51 if is_sensitive else 101
    avoid_threshold = 151 if is_sensitive else 201

    if aqi_value >= avoid_threshold:
        return "avoid", f"AQI {aqi_value}: move outdoors activity indoors or reschedule"
    if aqi_value >= caution_threshold:
        return "caution", f"AQI {aqi_value}: reduce intensity or shorten outdoor duration"
    return "safe", f"AQI {aqi_value}: favourable conditions for outdoor activity"


class DailyRoutineService:
    """Business logic for daily planner events and routines."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = DailyRoutineRepository(session)

    async def _get_user_aqi_context(
        self, user_id: UUID
    ) -> tuple[Optional[int], Optional[str], bool]:
        profile = await UserProfileService(self.session).get_by_user_id(user_id)
        is_sensitive = bool(
            profile
            and any(
                item.lower() != "none"
                for item in (profile.health_conditions or []) + (profile.sensitivities or [])
            )
        )

        loc = await LocationService(self.session).get_default_location(user_id)
        if not loc:
            locs = await LocationService(self.session).get_by_user(user_id)
            loc = locs[0] if locs else None
        if not loc:
            return None, None, is_sensitive

        latest_aqi = await AirQualityService(self.session).get_latest_reading(loc.id)
        if not latest_aqi:
            return None, None, is_sensitive
        return latest_aqi.aqi_value, latest_aqi.aqi_standard, is_sensitive

    def _to_response(
        self,
        routine: DailyRoutineModel,
        aqi_value: Optional[int],
        is_sensitive: bool,
    ) -> DailyRoutineResponse:
        band, note = compute_safety_band(routine.routine_type, aqi_value, is_sensitive)
        return DailyRoutineResponse(
            id=routine.id,
            user_id=routine.user_id,
            name=routine.name,
            description=routine.description,
            routine_type=routine.routine_type,
            routine_date=routine.routine_date,
            start_time=routine.start_time,
            end_time=routine.end_time,
            days_of_week=list(routine.days_of_week or []),
            location_id=routine.location_id,
            status=routine.status,
            reminder_minutes=routine.reminder_minutes,
            source_recommendation_id=routine.source_recommendation_id,
            is_active=routine.is_active,
            safety_band=band,
            safety_note=note,
            created_at=routine.created_at,
            updated_at=routine.updated_at,
        )

    async def list_routines(
        self,
        user_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        routine_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> DailyRoutineListResponse:
        items = await self.repo.list_for_user(
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            routine_type=routine_type,
            status=status,
        )
        # Filter recurring items when a single day is queried
        if date_from and date_to and date_from == date_to:
            weekday = date_from.weekday()
            items = [
                r
                for r in items
                if r.routine_date == date_from
                or (r.routine_date is None and (not r.days_of_week or weekday in r.days_of_week))
            ]

        aqi_val, aqi_std, is_sensitive = await self._get_user_aqi_context(user_id)
        responses = [self._to_response(r, aqi_val, is_sensitive) for r in items]
        return DailyRoutineListResponse(
            routines=responses,
            total=len(responses),
            aqi_value=aqi_val,
            aqi_standard=aqi_std,
        )

    async def create_routine(
        self, user_id: UUID, data: DailyRoutineCreate
    ) -> DailyRoutineResponse:
        now = datetime.now(timezone.utc)
        routine = DailyRoutineModel(
            user_id=user_id,
            name=data.name.strip(),
            description=data.description,
            routine_type=data.routine_type,
            routine_date=data.routine_date,
            start_time=data.start_time,
            end_time=data.end_time,
            days_of_week=data.days_of_week,
            location_id=data.location_id,
            status=data.status,
            reminder_minutes=data.reminder_minutes,
            source_recommendation_id=data.source_recommendation_id,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        await self.repo.add(routine)
        aqi_val, _, is_sensitive = await self._get_user_aqi_context(user_id)
        return self._to_response(routine, aqi_val, is_sensitive)

    async def update_routine(
        self, routine_id: UUID, user_id: UUID, data: DailyRoutineUpdate
    ) -> Optional[DailyRoutineResponse]:
        routine = await self.repo.get_by_id_for_user(routine_id, user_id)
        if not routine:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(routine, field, value)
        if routine.end_time <= routine.start_time:
            raise ValueError("end_time must be after start_time")

        routine.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        aqi_val, _, is_sensitive = await self._get_user_aqi_context(user_id)
        return self._to_response(routine, aqi_val, is_sensitive)

    async def update_status(
        self, routine_id: UUID, user_id: UUID, status: str
    ) -> Optional[DailyRoutineResponse]:
        return await self.update_routine(
            routine_id, user_id, DailyRoutineUpdate(status=status)
        )

    async def delete_routine(self, routine_id: UUID, user_id: UUID) -> bool:
        routine = await self.repo.get_by_id_for_user(routine_id, user_id)
        if not routine:
            return False
        await self.repo.delete(routine)
        return True
