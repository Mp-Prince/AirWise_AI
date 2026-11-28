"""Impact record Pydantic schemas (Phase 7)."""
from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TransportImpactRequest(BaseModel):
    """Input for calculating or logging a transport mode shift or electricity saving."""

    activity_category: Literal["transport", "electricity"] = "transport"
    baseline_mode: str = Field(default="petrol_car", description="Replaced activity key")
    alternative_mode: str = Field(default="metro_rail", description="Chosen lower-emission activity key")
    quantity: float = Field(..., gt=0, le=50000, description="Distance in km or energy saved in kWh")
    passengers: int = Field(default=1, ge=1, le=60, description="Shared occupancy divisor for carpooling")
    description: Optional[str] = Field(None, max_length=500)
    recorded_at: Optional[datetime] = None


class ImpactCalculationPreview(BaseModel):
    method_version: str
    unit: str = "kgCO2e"
    quantity: float
    quantity_unit: str
    baseline_co2e_kg: float
    alternative_co2e_kg: float
    co2e_saved_kg: float
    is_estimated: bool = True
    factor_snapshot: dict
    note: str


class ImpactRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    action_id: Optional[UUID] = None
    emission_factor_id: Optional[UUID] = None
    co2e_kg: float
    baseline_co2e_kg: Optional[float] = None
    alternative_co2e_kg: Optional[float] = None
    method_version: str
    factor_snapshot: dict = {}
    is_estimated: bool = True
    description: Optional[str] = None
    recorded_at: datetime
    created_at: datetime


class ImpactRecordListResponse(BaseModel):
    records: list[ImpactRecordResponse]
    total: int


class ImpactTrendPoint(BaseModel):
    date: date
    co2e_kg: float
    activities: int


class ImpactModeBreakdown(BaseModel):
    label: str
    co2e_kg: float
    count: int


class ImpactSummaryResponse(BaseModel):
    total_co2e_avoided_kg: float
    total_baseline_co2e_kg: float
    total_alternative_co2e_kg: float
    total_activities: int
    active_days_streak: int
    is_estimated: bool = True
    disclaimer: str
    trend: list[ImpactTrendPoint]
    breakdown: list[ImpactModeBreakdown]
