"""Air quality reading Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class AirQualityReadingBase(BaseModel):
    location_id: UUID = Field(..., description="Location ID")
    provider: str = Field(..., max_length=50, description="Data provider name")
    aqi_value: int = Field(..., ge=0, le=500, description="AQI value")
    aqi_standard: str = Field(default="US_AQI", max_length=20, description="AQI standard used")
    pm25: Optional[float] = Field(None, ge=0, description="PM2.5 concentration (µg/m³)")
    pm10: Optional[float] = Field(None, ge=0, description="PM10 concentration (µg/m³)")
    o3: Optional[float] = Field(None, ge=0, description="Ozone concentration (µg/m³)")
    no2: Optional[float] = Field(None, ge=0, description="Nitrogen dioxide concentration (µg/m³)")
    so2: Optional[float] = Field(None, ge=0, description="Sulfur dioxide concentration (µg/m³)")
    co: Optional[float] = Field(None, ge=0, description="Carbon monoxide concentration (mg/m³)")
    measured_at: datetime = Field(..., description="Measurement timestamp (timezone-aware)")
    is_estimated: bool = Field(default=False, description="Whether the reading is estimated")


class AirQualityReadingCreate(AirQualityReadingBase):
    pass


class AirQualityReadingResponse(AirQualityReadingBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AirQualityReadingListResponse(BaseModel):
    readings: list[AirQualityReadingResponse]
    total: int
    location_id: UUID
    provider: Optional[str] = None


class AQIColorInfo(BaseModel):
    """AQI category with color and health advisory."""
    aqi_value: int
    category: str
    color: str
    health_advisory: str


def get_aqi_category(aqi_value: int, standard: str = "US_AQI") -> AQIColorInfo:
    """Get AQI category, color, and health advisory based on value and standard."""
    if standard == "US_AQI":
        if aqi_value <= 50:
            return AQIColorInfo(
                aqi_value=aqi_value,
                category="Good",
                color="#00E400",
                health_advisory="Air quality is satisfactory, and air pollution poses little or no risk."
            )
        elif aqi_value <= 100:
            return AQIColorInfo(
                aqi_value=aqi_value,
                category="Moderate",
                color="#FFFF00",
                health_advisory="Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution."
            )
        elif aqi_value <= 150:
            return AQIColorInfo(
                aqi_value=aqi_value,
                category="Unhealthy for Sensitive Groups",
                color="#FF7E00",
                health_advisory="Members of sensitive groups may experience health effects. The general public is less likely to be affected."
            )
        elif aqi_value <= 200:
            return AQIColorInfo(
                aqi_value=aqi_value,
                category="Unhealthy",
                color="#FF0000",
                health_advisory="Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects."
            )
        elif aqi_value <= 300:
            return AQIColorInfo(
                aqi_value=aqi_value,
                category="Very Unhealthy",
                color="#8F3F97",
                health_advisory="Health alert: The risk of health effects is increased for everyone."
            )
        else:
            return AQIColorInfo(
                aqi_value=aqi_value,
                category="Hazardous",
                color="#7E0023",
                health_advisory="Health warning of emergency conditions: everyone is more likely to be affected."
            )
    else:  # CPCB India standard
        if aqi_value <= 50:
            return AQIColorInfo(
                aqi_value=aqi_value,
                category="Good",
                color="#00E400",
                health_advisory="Minimal impact"
            )
        elif aqi_value <= 100:
            return AQIColorInfo(
                aqi_value=aqi_value,
                category="Satisfactory",
                color="#FFFF00",
                health_advisory="Minor breathing discomfort to sensitive people"
            )
        elif aqi_value <= 200:
            return AQIColorInfo(
                aqi_value=aqi_value,
                category="Moderate",
                color="#FF7E00",
                health_advisory="Breathing discomfort to people with lung, heart disease, children and older adults"
            )
        elif aqi_value <= 300:
            return AQIColorInfo(
                aqi_value=aqi_value,
                category="Poor",
                color="#FF0000",
                health_advisory="Breathing discomfort to most people on prolonged exposure"
            )
        elif aqi_value <= 400:
            return AQIColorInfo(
                aqi_value=aqi_value,
                category="Very Poor",
                color="#8F3F97",
                health_advisory="Respiratory illness on prolonged exposure"
            )
        else:
            return AQIColorInfo(
                aqi_value=aqi_value,
                category="Severe",
                color="#7E0023",
                health_advisory="Affects healthy people and seriously impacts those with existing diseases"
            )