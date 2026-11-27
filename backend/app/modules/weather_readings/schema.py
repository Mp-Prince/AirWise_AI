"""Weather reading Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class WeatherReadingBase(BaseModel):
    location_id: UUID = Field(..., description="Location ID")
    provider: str = Field(..., max_length=50, description="Data provider name")
    temperature_c: Optional[float] = Field(None, ge=-100, le=100, description="Temperature in Celsius")
    humidity_pct: Optional[int] = Field(None, ge=0, le=100, description="Humidity percentage")
    pressure_hpa: Optional[float] = Field(None, ge=0, le=2000, description="Atmospheric pressure in hPa")
    wind_speed_ms: Optional[float] = Field(None, ge=0, le=200, description="Wind speed in m/s")
    wind_direction_deg: Optional[int] = Field(None, ge=0, le=360, description="Wind direction in degrees")
    precipitation_mm: Optional[float] = Field(None, ge=0, description="Precipitation in mm")
    uv_index: Optional[float] = Field(None, ge=0, le=20, description="UV index")
    cloud_cover_pct: Optional[int] = Field(None, ge=0, le=100, description="Cloud cover percentage")
    visibility_km: Optional[float] = Field(None, ge=0, le=100, description="Visibility in km")
    weather_code: Optional[int] = Field(None, description="Weather condition code (WMO)")
    measured_at: datetime = Field(..., description="Measurement timestamp (timezone-aware)")
    is_estimated: bool = Field(default=False, description="Whether the reading is estimated")


class WeatherReadingCreate(WeatherReadingBase):
    pass


class WeatherReadingResponse(WeatherReadingBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class WeatherReadingListResponse(BaseModel):
    readings: list[WeatherReadingResponse]
    total: int
    location_id: UUID
    provider: Optional[str] = None


# Weather code descriptions (WMO codes)
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_weather_description(code: Optional[int]) -> str:
    """Get human-readable weather description from WMO code."""
    if code is None:
        return "Unknown"
    return WEATHER_CODES.get(code, f"Unknown code: {code}")


def get_uv_advisory(uv_index: Optional[float]) -> str:
    """Get UV exposure advisory based on UV index."""
    if uv_index is None:
        return "UV data unavailable"
    if uv_index <= 2:
        return "Low - No protection needed"
    elif uv_index <= 5:
        return "Moderate - Protection required during midday"
    elif uv_index <= 7:
        return "High - Protection essential"
    elif uv_index <= 10:
        return "Very High - Extra protection needed"
    else:
        return "Extreme - Avoid sun exposure"