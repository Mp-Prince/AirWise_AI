"""Environmental impact calculation & tracking service (Phase 7).

Provides reproducible CO2e avoidance estimates with stored factor snapshots,
method version, explicit boundaries/assumptions, and zero unsupported PM2.5 claims.
"""
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.emission_factors.service import EmissionFactorService
from app.modules.impact_records.models import ImpactRecordModel
from app.modules.impact_records.repository import ImpactRecordRepository
from app.modules.impact_records.schema import (
    ImpactCalculationPreview,
    ImpactModeBreakdown,
    ImpactRecordListResponse,
    ImpactRecordResponse,
    ImpactSummaryResponse,
    ImpactTrendPoint,
    TransportImpactRequest,
)
from app.modules.user_actions.models import UserActionModel

METHOD_VERSION_TRANSPORT = "airwise_transport_v1"
METHOD_VERSION_ELECTRICITY = "airwise_electricity_v1"
IMPACT_DISCLAIMER = (
    "All values are estimated CO2e savings based on published average emission factors. "
    "No personal PM2.5 reduction or direct medical benefit is claimed."
)


def calculate_co2e_impact(
    quantity: float,
    baseline_per_unit: float,
    alternative_per_unit: float,
    passengers: int = 1,
    activity_category: str = "transport",
) -> tuple[float, float, float]:
    """Pure, reproducible CO2e calculation returning (baseline, alternative, saved)."""
    baseline_co2e = round(quantity * baseline_per_unit, 4)
    if activity_category == "electricity":
        # Direct kWh saved: baseline represents avoided grid electricity
        alternative_co2e = 0.0
    else:
        divisor = max(1, passengers)
        alternative_co2e = round((quantity * alternative_per_unit) / divisor, 4)
    saved_co2e = round(max(0.0, baseline_co2e - alternative_co2e), 4)
    return baseline_co2e, alternative_co2e, saved_co2e


def compute_active_streak(recorded_dates: set[date], reference_date: Optional[date] = None) -> int:
    """Count consecutive days with at least one logged activity ending today or yesterday."""
    if not recorded_dates:
        return 0
    today = reference_date or datetime.now(timezone.utc).date()
    cursor = today if today in recorded_dates else today - timedelta(days=1)
    if cursor not in recorded_dates:
        return 0
    streak = 0
    while cursor in recorded_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


class ImpactService:
    """Service for reproducible impact calculations, activity logging, and summaries."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ImpactRecordRepository(session)
        self.factor_service = EmissionFactorService(session)

    async def preview_calculation(
        self, payload: TransportImpactRequest
    ) -> ImpactCalculationPreview:
        if payload.activity_category == "electricity":
            factor = await self.factor_service.get_by_activity("grid_electricity_in")
            if not factor:
                raise ValueError("Grid electricity emission factor not found")
            rate = float(factor.co2e_kg_per_unit)
            baseline_kg, alt_kg, saved_kg = calculate_co2e_impact(
                quantity=payload.quantity,
                baseline_per_unit=rate,
                alternative_per_unit=0.0,
                activity_category="electricity",
            )
            snapshot = {
                "activity_category": "electricity",
                "baseline_activity": factor.activity,
                "baseline_factor_kg_per_unit": rate,
                "unit": factor.unit,
                "source": factor.source,
                "region": factor.region,
                "quantity": payload.quantity,
                "quantity_unit": "kWh",
                "boundary": "Grid electricity consumption avoided (Scope 2 grid average)",
                "assumptions": [
                    "Assumes kWh avoided directly reduces grid electricity demand at CEA average emission factor.",
                    "Does not claim direct ambient PM2.5 or health risk reduction.",
                ],
            }
            return ImpactCalculationPreview(
                method_version=METHOD_VERSION_ELECTRICITY,
                quantity=payload.quantity,
                quantity_unit="kWh",
                baseline_co2e_kg=baseline_kg,
                alternative_co2e_kg=alt_kg,
                co2e_saved_kg=saved_kg,
                is_estimated=True,
                factor_snapshot=snapshot,
                note=IMPACT_DISCLAIMER,
            )

        base_factor = await self.factor_service.get_by_activity(payload.baseline_mode)
        alt_factor = await self.factor_service.get_by_activity(payload.alternative_mode)
        if not base_factor or not alt_factor:
            raise ValueError("Selected baseline or alternative transport emission factor not found")

        base_rate = float(base_factor.co2e_kg_per_unit)
        alt_rate = float(alt_factor.co2e_kg_per_unit)
        baseline_kg, alt_kg, saved_kg = calculate_co2e_impact(
            quantity=payload.quantity,
            baseline_per_unit=base_rate,
            alternative_per_unit=alt_rate,
            passengers=payload.passengers,
            activity_category="transport",
        )

        snapshot = {
            "activity_category": "transport",
            "baseline_mode": base_factor.activity,
            "baseline_factor_kg_per_unit": base_rate,
            "baseline_unit": base_factor.unit,
            "baseline_source": base_factor.source,
            "alternative_mode": alt_factor.activity,
            "alternative_factor_kg_per_unit": alt_rate,
            "alternative_unit": alt_factor.unit,
            "alternative_source": alt_factor.source,
            "region": alt_factor.region or base_factor.region,
            "quantity": payload.quantity,
            "quantity_unit": "km",
            "passengers": payload.passengers,
            "boundary": "Operational tailpipe / grid electricity transport emissions",
            "assumptions": [
                f"Distance {payload.quantity} km shifted from {base_factor.activity} to {alt_factor.activity}.",
                f"Alternative occupancy divisor = {payload.passengers} passenger(s).",
                "Estimated CO2e only; excludes lifecycle vehicle manufacturing and makes no PM2.5/health claim.",
            ],
        }
        return ImpactCalculationPreview(
            method_version=METHOD_VERSION_TRANSPORT,
            quantity=payload.quantity,
            quantity_unit="km",
            baseline_co2e_kg=baseline_kg,
            alternative_co2e_kg=alt_kg,
            co2e_saved_kg=saved_kg,
            is_estimated=True,
            factor_snapshot=snapshot,
            note=IMPACT_DISCLAIMER,
        )

    async def log_activity(
        self, user_id: UUID, payload: TransportImpactRequest
    ) -> ImpactRecordResponse:
        preview = await self.preview_calculation(payload)
        factor_key = (
            "grid_electricity_in"
            if payload.activity_category == "electricity"
            else payload.alternative_mode
        )
        factor = await self.factor_service.get_by_activity(factor_key)
        now = payload.recorded_at or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        action = UserActionModel(
            user_id=user_id,
            action_type=f"logged_{payload.activity_category}",
            reference_id=factor.id if factor else None,
            metadata_json={
                "baseline_mode": payload.baseline_mode,
                "alternative_mode": payload.alternative_mode,
                "quantity": payload.quantity,
                "passengers": payload.passengers,
                "method_version": preview.method_version,
            },
            created_at=now,
        )
        self.session.add(action)
        await self.session.flush()

        desc = payload.description or (
            f"Saved {payload.quantity} kWh electricity"
            if payload.activity_category == "electricity"
            else f"Shifted {payload.quantity} km from {payload.baseline_mode.replace('_', ' ')} to {payload.alternative_mode.replace('_', ' ')}"
        )

        record = ImpactRecordModel(
            user_id=user_id,
            action_id=action.id,
            emission_factor_id=factor.id if factor else None,
            co2e_kg=preview.co2e_saved_kg,
            baseline_co2e_kg=preview.baseline_co2e_kg,
            alternative_co2e_kg=preview.alternative_co2e_kg,
            method_version=preview.method_version,
            factor_snapshot=preview.factor_snapshot,
            is_estimated=True,
            description=desc[:500],
            recorded_at=now,
            created_at=datetime.now(timezone.utc),
        )
        await self.repo.add(record)
        return ImpactRecordResponse.model_validate(record)

    def _resolve_range(
        self,
        date_from: Optional[date],
        date_to: Optional[date],
        period: Optional[str],
    ) -> tuple[Optional[datetime], Optional[datetime]]:
        today = datetime.now(timezone.utc).date()
        if period and not date_from and not date_to:
            if period == "today":
                date_from = today
                date_to = today
            elif period == "week":
                date_from = today - timedelta(days=6)
                date_to = today
            elif period in {"30d", "month"}:
                date_from = today - timedelta(days=29)
                date_to = today

        start_dt = (
            datetime.combine(date_from, time.min, tzinfo=timezone.utc)
            if date_from
            else None
        )
        end_dt = (
            datetime.combine(date_to, time.max, tzinfo=timezone.utc)
            if date_to
            else None
        )
        return start_dt, end_dt

    async def list_records(
        self,
        user_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        period: Optional[str] = None,
    ) -> ImpactRecordListResponse:
        start_dt, end_dt = self._resolve_range(date_from, date_to, period)
        records = await self.repo.list_for_user(user_id, start_dt=start_dt, end_dt=end_dt)
        return ImpactRecordListResponse(
            records=[ImpactRecordResponse.model_validate(r) for r in records],
            total=len(records),
        )

    async def get_record(
        self, record_id: UUID, user_id: UUID
    ) -> Optional[ImpactRecordResponse]:
        rec = await self.repo.get_by_id_for_user(record_id, user_id)
        return ImpactRecordResponse.model_validate(rec) if rec else None

    async def delete_record(self, record_id: UUID, user_id: UUID) -> bool:
        rec = await self.repo.get_by_id_for_user(record_id, user_id)
        if not rec:
            return False
        await self.repo.delete(rec)
        return True

    async def get_summary(
        self,
        user_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        period: Optional[str] = "30d",
    ) -> ImpactSummaryResponse:
        start_dt, end_dt = self._resolve_range(date_from, date_to, period)
        records = await self.repo.list_for_user(user_id, start_dt=start_dt, end_dt=end_dt)
        all_records = await self.repo.list_for_user(user_id, limit=365)

        total_saved = 0.0
        total_base = 0.0
        total_alt = 0.0
        daily_map: dict[date, dict] = defaultdict(lambda: {"co2e": 0.0, "count": 0})
        mode_map: dict[str, dict] = defaultdict(lambda: {"co2e": 0.0, "count": 0})

        for r in records:
            saved = float(r.co2e_kg or 0)
            base = float(r.baseline_co2e_kg or saved)
            alt = float(r.alternative_co2e_kg or 0)
            total_saved += saved
            total_base += base
            total_alt += alt

            rec_day = r.recorded_at.date()
            daily_map[rec_day]["co2e"] += saved
            daily_map[rec_day]["count"] += 1

            snap = r.factor_snapshot or {}
            label = (
                "Electricity saved"
                if snap.get("activity_category") == "electricity"
                else (snap.get("alternative_mode") or "other").replace("_", " ").title()
            )
            mode_map[label]["co2e"] += saved
            mode_map[label]["count"] += 1

        trend = [
            ImpactTrendPoint(
                date=d,
                co2e_kg=round(vals["co2e"], 4),
                activities=vals["count"],
            )
            for d, vals in sorted(daily_map.items())
        ]
        breakdown = [
            ImpactModeBreakdown(
                label=label,
                co2e_kg=round(vals["co2e"], 4),
                count=vals["count"],
            )
            for label, vals in sorted(
                mode_map.items(), key=lambda kv: kv[1]["co2e"], reverse=True
            )
        ]

        recorded_dates = {r.recorded_at.date() for r in all_records}
        return ImpactSummaryResponse(
            total_co2e_avoided_kg=round(total_saved, 4),
            total_baseline_co2e_kg=round(total_base, 4),
            total_alternative_co2e_kg=round(total_alt, 4),
            total_activities=len(records),
            active_days_streak=compute_active_streak(recorded_dates),
            is_estimated=True,
            disclaimer=IMPACT_DISCLAIMER,
            trend=trend,
            breakdown=breakdown,
        )
