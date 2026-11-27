"""Location Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class LocationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Location name")
    lat: float = Field(..., ge=-90, le=90, description="Latitude",
                       validation_alias="latitude", serialization_alias="lat")
    lon: float = Field(..., ge=-180, le=180, description="Longitude",
                       validation_alias="longitude", serialization_alias="lon")
    city: Optional[str] = Field(None, max_length=100, description="City name")
    state: Optional[str] = Field(None, max_length=100, description="State/province name")
    country: Optional[str] = Field(None, max_length=100, description="Country name")
    is_default: bool = Field(default=False, description="Whether this is the user's default location")

    class Config:
        populate_by_name = True


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    lat: Optional[float] = Field(None, ge=-90, le=90,
                                  validation_alias="latitude", serialization_alias="lat")
    lon: Optional[float] = Field(None, ge=-180, le=180,
                                  validation_alias="longitude", serialization_alias="lon")
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    is_default: Optional[bool] = None

    class Config:
        populate_by_name = True


class LocationResponse(LocationBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class LocationListResponse(BaseModel):
    locations: list[LocationResponse]
    total: int


class LocationWithEnvironmentalData(LocationResponse):
    """Location with latest AQI and weather data."""
    latest_aqi: Optional[dict] = None
    latest_weather: Optional[dict] = None