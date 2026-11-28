"""Daily routine / planner Pydantic schemas (Phase 6)."""
from datetime import date, datetime, time
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

RoutineCategory = Literal[
    "commute", "exercise", "outdoor_work", "indoor_air", "energy", "waste", "other"
]
RoutineStatusType = Literal["planned", "completed", "skipped"]
SafetyBandType = Literal["safe", "caution", "avoid", "unknown"]


class DailyRoutineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=160, description="Event or routine title")
    description: Optional[str] = Field(None, max_length=1000)
    routine_type: RoutineCategory = Field(default="other")
    routine_date: Optional[date] = Field(None, description="Specific calendar date (YYYY-MM-DD)")
    start_time: time = Field(..., description="Start time (HH:MM)")
    end_time: time = Field(..., description="End time (HH:MM)")
    days_of_week: list[int] = Field(
        default_factory=list,
        description="Optional recurring weekdays (0=Mon .. 6=Sun)",
    )
    location_id: Optional[UUID] = None
    reminder_minutes: Optional[int] = Field(None, ge=0, le=1440)

    @model_validator(mode="after")
    def validate_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class DailyRoutineCreate(DailyRoutineBase):
    status: RoutineStatusType = "planned"
    source_recommendation_id: Optional[UUID] = None


class DailyRoutineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=160)
    description: Optional[str] = Field(None, max_length=1000)
    routine_type: Optional[RoutineCategory] = None
    routine_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    days_of_week: Optional[list[int]] = None
    location_id: Optional[UUID] = None
    status: Optional[RoutineStatusType] = None
    reminder_minutes: Optional[int] = Field(None, ge=0, le=1440)
    is_active: Optional[bool] = None


class DailyRoutineStatusUpdate(BaseModel):
    status: RoutineStatusType


class DailyRoutineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: Optional[str] = None
    routine_type: str
    routine_date: Optional[date] = None
    start_time: time
    end_time: time
    days_of_week: list[int] = []
    location_id: Optional[UUID] = None
    status: str
    reminder_minutes: Optional[int] = None
    source_recommendation_id: Optional[UUID] = None
    is_active: bool
    safety_band: SafetyBandType = "unknown"
    safety_note: str = "Live AQI unavailable"
    created_at: datetime
    updated_at: datetime


class DailyRoutineListResponse(BaseModel):
    routines: list[DailyRoutineResponse]
    total: int
    aqi_value: Optional[int] = None
    aqi_standard: Optional[str] = None
