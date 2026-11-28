"""Recommendation rules & personalized suggestion service (Phase 6)."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.air_quality_readings.service import AirQualityService
from app.modules.daily_routines.schema import DailyRoutineCreate
from app.modules.daily_routines.service import DailyRoutineService
from app.modules.locations.service import LocationService
from app.modules.rag.service import RAGService
from app.modules.recommendations.models import (
    RecommendationCategory,
    RecommendationModel,
    RecommendationStatus,
)
from app.modules.recommendations.repository import RecommendationRepository
from app.modules.recommendations.schema import (
    AddToPlannerRequest,
    RecommendationListResponse,
    RecommendationResponse,
)
from app.modules.user_actions.models import ActionType, UserActionModel
from app.modules.user_profiles.service import UserProfileService
from app.modules.weather_readings.service import WeatherService


def build_deterministic_rules(
    aqi_value: Optional[int],
    aqi_standard: Optional[str],
    location_name: Optional[str],
    sensitivities: list[str],
    health_conditions: list[str],
    temperature_c: Optional[float] = None,
) -> list[dict]:
    """Deterministic safety and sustainable action rules driven by real context."""
    rules: list[dict] = []
    sensitive_flags = [
        item
        for item in (health_conditions + sensitivities)
        if item and item.lower() != "none"
    ]
    is_sensitive = len(sensitive_flags) > 0
    loc_label = location_name or "your saved location"

    if aqi_value is None:
        rules.append(
            {
                "category": RecommendationCategory.HEALTH,
                "title": "Sync local air quality before planning outdoor exercise",
                "description": (
                    "No live AQI reading is stored yet for your location. Sync your location "
                    "on the Dashboard before scheduling vigorous outdoor workouts."
                ),
                "reasoning": "Missing air quality data must not be treated as safe or zero.",
            }
        )
    elif aqi_value >= (151 if is_sensitive else 201):
        rules.append(
            {
                "category": RecommendationCategory.HEALTH,
                "title": "Move outdoor workouts indoors today",
                "description": (
                    f"AQI in {loc_label} is {aqi_value} ({aqi_standard}). Avoid strenuous "
                    "outdoor exertion, keep windows closed, and wear a well-fitted N95/FFP2 "
                    "mask if outdoor travel is unavoidable."
                ),
                "reasoning": (
                    f"Triggered by elevated AQI {aqi_value}"
                    + (f" and your sensitivity profile ({', '.join(sensitive_flags)})" if is_sensitive else "")
                    + "."
                ),
            }
        )
    elif aqi_value >= (51 if is_sensitive else 101):
        rules.append(
            {
                "category": RecommendationCategory.HEALTH,
                "title": "Keep outdoor activities moderate and monitor symptoms",
                "description": (
                    f"AQI in {loc_label} is {aqi_value} ({aqi_standard}). Prefer shorter "
                    "outdoor sessions away from busy traffic corridors."
                ),
                "reasoning": (
                    f"Triggered by moderate/caution AQI {aqi_value}"
                    + (f" with profile factors: {', '.join(sensitive_flags)}" if is_sensitive else "")
                    + "."
                ),
            }
        )
    else:
        rules.append(
            {
                "category": RecommendationCategory.LIFESTYLE,
                "title": "Good air window for outdoor walking or cycling",
                "description": (
                    f"Current AQI in {loc_label} is {aqi_value} ({aqi_standard}). Take "
                    "advantage of cleaner air for walking, cycling, or ventilating indoor rooms."
                ),
                "reasoning": f"Triggered by favourable AQI {aqi_value}.",
            }
        )

    if temperature_c is not None and temperature_c >= 34:
        rules.append(
            {
                "category": RecommendationCategory.HEALTH,
                "title": "Schedule outdoor errands before 10:00 AM or after sunset",
                "description": (
                    f"Current temperature is {temperature_c:.1f}°C. Shifting outdoor tasks to "
                    "cooler hours reduces heat stress and peak midday ozone exposure."
                ),
                "reasoning": f"Triggered by high ambient temperature ({temperature_c:.1f}°C).",
            }
        )

    rules.append(
        {
            "category": RecommendationCategory.ECO,
            "title": "Replace one short solo vehicle trip with metro, bus, or walking",
            "description": (
                "Shifting short daily trips to public transit or active travel lowers "
                "tailpipe PM2.5 and estimated CO2e emissions."
            ),
            "reasoning": "Sustainable transport option tailored for everyday commute routines.",
        }
    )

    rules.append(
        {
            "category": RecommendationCategory.LIFESTYLE,
            "title": "Ventilate indoors during cleaner air hours",
            "description": (
                "Cross-ventilate rooms when outdoor AQI is low and avoid burning incense, "
                "candles, or solid waste indoors to keep indoor PM2.5 low."
            ),
            "reasoning": "Indoor source control helps protect respiratory health.",
        }
    )

    return rules


class RecommendationService:
    """Business logic for personalized recommendations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = RecommendationRepository(session)

    async def _get_context(self, user_id: UUID) -> dict:
        profile = await UserProfileService(self.session).get_by_user_id(user_id)
        sensitivities = list(profile.sensitivities or []) if profile else []
        health_conditions = list(profile.health_conditions or []) if profile else []

        loc = await LocationService(self.session).get_default_location(user_id)
        if not loc:
            locs = await LocationService(self.session).get_by_user(user_id)
            loc = locs[0] if locs else None

        aqi_val: Optional[int] = None
        aqi_std: Optional[str] = None
        temp_c: Optional[float] = None
        if loc:
            latest_aqi = await AirQualityService(self.session).get_latest_reading(loc.id)
            if latest_aqi:
                aqi_val = latest_aqi.aqi_value
                aqi_std = latest_aqi.aqi_standard
            latest_weather = await WeatherService(self.session).get_latest_reading(loc.id)
            if latest_weather and latest_weather.temperature_c is not None:
                temp_c = float(latest_weather.temperature_c)

        return {
            "location_name": (loc.city or loc.name) if loc else None,
            "aqi_value": aqi_val,
            "aqi_standard": aqi_std,
            "temperature_c": temp_c,
            "sensitivities": sensitivities,
            "health_conditions": health_conditions,
        }

    async def list_recommendations(
        self,
        user_id: UUID,
        category: Optional[str] = None,
        status: Optional[str] = None,
        auto_generate_if_empty: bool = True,
    ) -> RecommendationListResponse:
        ctx = await self._get_context(user_id)
        items = await self.repo.list_for_user(user_id, category=category, status=status)

        if auto_generate_if_empty and not items and not category and status in (None, RecommendationStatus.PENDING):
            await self.generate_for_user(user_id, ctx=ctx)
            items = await self.repo.list_for_user(user_id, category=category, status=status)

        return RecommendationListResponse(
            recommendations=[RecommendationResponse.model_validate(r) for r in items],
            total=len(items),
            aqi_value=ctx["aqi_value"],
            aqi_standard=ctx["aqi_standard"],
        )

    async def get_today(self, user_id: UUID) -> RecommendationListResponse:
        return await self.list_recommendations(
            user_id=user_id,
            status=RecommendationStatus.PENDING,
            auto_generate_if_empty=True,
        )

    async def generate_for_user(
        self, user_id: UUID, ctx: Optional[dict] = None
    ) -> list[RecommendationResponse]:
        ctx = ctx or await self._get_context(user_id)
        candidates = build_deterministic_rules(
            aqi_value=ctx["aqi_value"],
            aqi_standard=ctx["aqi_standard"],
            location_name=ctx["location_name"],
            sensitivities=ctx["sensitivities"],
            health_conditions=ctx["health_conditions"],
            temperature_c=ctx["temperature_c"],
        )

        # Attach supporting RAG document IDs when available (non-fatal)
        source_doc_ids: list[UUID] = []
        try:
            chunks = await RAGService(self.session).retrieve_context(
                "air quality health precautions PM2.5 sustainable commute", top_k=3
            )
            source_doc_ids = list(dict.fromkeys(c.document_id for c in chunks))
        except Exception:
            source_doc_ids = []

        existing_pending = await self.repo.list_for_user(
            user_id, status=RecommendationStatus.PENDING
        )
        existing_titles = {r.title for r in existing_pending}

        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=24)
        new_models: list[RecommendationModel] = []
        for item in candidates:
            if item["title"] in existing_titles:
                continue
            new_models.append(
                RecommendationModel(
                    user_id=user_id,
                    category=item["category"],
                    title=item["title"],
                    description=item["description"],
                    reasoning=item["reasoning"],
                    source_document_ids=source_doc_ids,
                    status=RecommendationStatus.PENDING,
                    expires_at=expires,
                    created_at=now,
                    updated_at=now,
                )
            )

        if new_models:
            await self.repo.add_many(new_models)

        return [RecommendationResponse.model_validate(m) for m in new_models]

    async def update_status(
        self, rec_id: UUID, user_id: UUID, new_status: str
    ) -> Optional[RecommendationResponse]:
        rec = await self.repo.get_by_id_for_user(rec_id, user_id)
        if not rec:
            return None

        rec.status = new_status
        rec.updated_at = datetime.now(timezone.utc)

        action_type = (
            ActionType.ACCEPTED_RECOMMENDATION
            if new_status == RecommendationStatus.ACCEPTED
            else ActionType.DISMISSED_RECOMMENDATION
        )
        self.session.add(
            UserActionModel(
                user_id=user_id,
                action_type=action_type,
                reference_id=rec.id,
                metadata_json={"title": rec.title, "category": rec.category},
            )
        )
        await self.session.flush()
        return RecommendationResponse.model_validate(rec)

    async def add_to_planner(
        self, rec_id: UUID, user_id: UUID, payload: AddToPlannerRequest
    ) -> Optional[dict]:
        rec = await self.repo.get_by_id_for_user(rec_id, user_id)
        if not rec:
            return None

        routine = await DailyRoutineService(self.session).create_routine(
            user_id,
            DailyRoutineCreate(
                name=rec.title[:160],
                description=rec.description,
                routine_type=payload.routine_type,
                routine_date=payload.routine_date,
                start_time=payload.start_time,
                end_time=payload.end_time,
                reminder_minutes=payload.reminder_minutes,
                source_recommendation_id=rec.id,
            ),
        )
        updated_rec = await self.update_status(
            rec.id, user_id, RecommendationStatus.ACCEPTED
        )
        return {"recommendation": updated_rec, "routine": routine}
