"""Recommendation Pydantic schemas (Phase 6)."""
from datetime import date, datetime, time
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

RecCategory = Literal["health", "lifestyle", "eco"]
RecStatus = Literal["pending", "accepted", "dismissed", "expired"]


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    category: str
    title: str
    description: str
    reasoning: Optional[str] = None
    source_document_ids: list[UUID] = []
    status: str
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class RecommendationListResponse(BaseModel):
    recommendations: list[RecommendationResponse]
    total: int
    aqi_value: Optional[int] = None
    aqi_standard: Optional[str] = None


class AddToPlannerRequest(BaseModel):
    routine_date: date = Field(..., description="Target date (YYYY-MM-DD)")
    start_time: time = Field(default=time(8, 0))
    end_time: time = Field(default=time(8, 30))
    routine_type: Literal[
        "commute", "exercise", "outdoor_work", "indoor_air", "energy", "waste", "other"
    ] = "other"
    reminder_minutes: Optional[int] = Field(default=15, ge=0, le=1440)
