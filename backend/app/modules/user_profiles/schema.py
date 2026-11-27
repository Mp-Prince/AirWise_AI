"""User profile Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class UserProfileBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    date_of_birth: Optional[datetime] = Field(None, description="User's date of birth")
    gender: Optional[str] = Field(None, max_length=20, description="User's gender")
    height_cm: Optional[int] = Field(None, ge=30, le=300, description="Height in centimeters")
    weight_kg: Optional[float] = Field(None, ge=1.0, le=500.0, description="Weight in kilograms")
    health_conditions: List[str] = Field(default_factory=list, description="List of health conditions")
    sensitivities: List[str] = Field(default_factory=list, description="List of sensitivities")
    preferred_units: str = Field(default="metric", max_length=20, description="Preferred units (metric/imperial)")
    language: str = Field(default="en", max_length=10, description="Preferred language")
    timezone: str = Field(default="UTC", max_length=50, description="User's timezone")


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, max_length=20)
    height_cm: Optional[int] = Field(None, ge=30, le=300)
    weight_kg: Optional[float] = Field(None, ge=1.0, le=500.0)
    health_conditions: Optional[List[str]] = None
    sensitivities: Optional[List[str]] = None
    preferred_units: Optional[str] = Field(None, max_length=20)
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)


class UserProfileResponse(UserProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True