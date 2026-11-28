"""Emission factor Pydantic schemas (Phase 7)."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EmissionFactorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    activity: str
    co2e_kg_per_unit: float
    unit: str
    source: str
    region: Optional[str] = None
    valid_from: datetime
    valid_to: Optional[datetime] = None


class EmissionFactorListResponse(BaseModel):
    factors: list[EmissionFactorResponse]
    total: int
