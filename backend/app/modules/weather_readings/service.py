"""Weather data service with OpenWeatherMap primary and Open-Meteo fallback."""
from datetime import datetime, timezone
import logging
from typing import Optional
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.weather_readings.models import WeatherReadingModel
from app.modules.weather_readings.schema import WeatherReadingCreate, get_weather_description, get_uv_advisory
from app.modules.locations.models import LocationModel
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# External Weather API endpoints
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
OPENMETEO_BASE_URL = "https://api.open-meteo.com/v1"

# Weather code mapping (WMO codes used by OpenWeatherMap)
WMO_CODES = {
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


class WeatherService:
    """Service for managing weather data with external provider integration."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_latest_reading(
        self,
        location_id: UUID,
        provider: Optional[str] = None,
    ) -> Optional[WeatherReadingModel]:
        """Get the most recent weather reading for a location."""
        query = select(WeatherReadingModel).where(
            WeatherReadingModel.location_id == location_id
        )
        if provider:
            query = query.where(WeatherReadingModel.provider == provider)
        query = query.order_by(WeatherReadingModel.measured_at.desc()).limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_readings(
        self,
        location_id: UUID,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        provider: Optional[str] = None,
        limit: int = 100,
    ) -> list[WeatherReadingModel]:
        """Get weather readings for a location within a time range."""
        query = select(WeatherReadingModel).where(
            WeatherReadingModel.location_id == location_id
        )
        if start_time:
            query = query.where(WeatherReadingModel.measured_at >= start_time)
        if end_time:
            query = query.where(WeatherReadingModel.measured_at <= end_time)
        if provider:
            query = query.where(WeatherReadingModel.provider == provider)
        query = query.order_by(WeatherReadingModel.measured_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_reading(self, reading_data: WeatherReadingCreate) -> WeatherReadingModel:
        """Create a new weather reading."""
        reading = WeatherReadingModel(**reading_data.model_dump())
        self.session.add(reading)
        await self.session.flush()
        return reading

    async def create_readings_bulk(
        self, readings_data: list[WeatherReadingCreate]
    ) -> list[WeatherReadingModel]:
        """Create multiple weather readings in bulk."""
        readings = [WeatherReadingModel(**data.model_dump()) for data in readings_data]
        self.session.add_all(readings)
        await self.session.flush()
        return readings

    async def fetch_from_openweather(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[WeatherReadingCreate]:
        """Fetch current weather data from OpenWeatherMap for a location."""
        settings = get_settings()
        if not settings.OPENWEATHERMAP_API_KEY:
            raise ValueError("OpenWeatherMap API key not configured (use OPENWEATHERMAP_API_KEY)")

        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": settings.OPENWEATHERMAP_API_KEY,
            "units": "metric",
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{OPENWEATHER_BASE_URL}/weather",
                params=params,
            )
            response.raise_for_status()
            data = response.json()

        return self._parse_openweather_response(data)

    async def fetch_from_openmeteo(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[WeatherReadingCreate]:
        """Fetch current weather data from Open-Meteo (free fallback, includes UV & WMO codes)."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,relative_humidity_2m,pressure_msl,"
                "wind_speed_10m,wind_direction_10m,precipitation,"
                "cloud_cover,weather_code"
            ),
            "hourly": "uv_index",
            "forecast_days": 1,
            "timezone": "UTC",
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(f"{OPENMETEO_BASE_URL}/forecast", params=params)
            response.raise_for_status()
            data = response.json()

        current = data.get("current", {})
        if not current:
            return None

        time_str = current.get("time")
        measured_at = (
            datetime.fromisoformat(time_str).replace(tzinfo=timezone.utc)
            if time_str
            else datetime.now(timezone.utc)
        )

        # Match closest hourly UV index if available
        uv_index = None
        hourly = data.get("hourly", {})
        hourly_times = hourly.get("time") or []
        hourly_uv = hourly.get("uv_index") or []
        if time_str and hourly_times and hourly_uv:
            hour_prefix = time_str[:13]  # YYYY-MM-DDTHH
            for idx, ht in enumerate(hourly_times):
                if ht.startswith(hour_prefix) and idx < len(hourly_uv):
                    uv_index = hourly_uv[idx]
                    break

        # Open-Meteo wind_speed_10m defaults to km/h -> convert to m/s
        wind_kmh = current.get("wind_speed_10m")
        wind_ms = round(wind_kmh / 3.6, 1) if wind_kmh is not None else None

        return WeatherReadingCreate(
            location_id=UUID(int=0),
            provider="Open-Meteo",
            temperature_c=current.get("temperature_2m"),
            humidity_pct=current.get("relative_humidity_2m"),
            pressure_hpa=current.get("pressure_msl"),
            wind_speed_ms=wind_ms,
            wind_direction_deg=current.get("wind_direction_10m"),
            precipitation_mm=current.get("precipitation"),
            uv_index=uv_index,
            cloud_cover_pct=current.get("cloud_cover"),
            visibility_km=None,
            weather_code=current.get("weather_code"),
            measured_at=measured_at,
            is_estimated=False,
        )

    def _parse_openweather_response(self, data: dict) -> WeatherReadingCreate:
        """Parse OpenWeatherMap API response into our schema."""
        main = data.get("main", {})
        wind = data.get("wind", {})
        weather = data.get("weather", [{}])[0]
        clouds = data.get("clouds", {})

        # Extract measurement time (use current time if not available)
        dt = data.get("dt")
        if dt:
            measured_at = datetime.fromtimestamp(dt, tz=timezone.utc)
        else:
            measured_at = datetime.now(timezone.utc)

        # Get weather code - OpenWeatherMap uses its own codes, map to WMO
        weather_id = weather.get("id", 0)
        wmo_code = self._map_owm_to_wmo(weather_id)

        rain_mm = (data.get("rain") or {}).get("1h")
        snow_mm = (data.get("snow") or {}).get("1h")
        precip = rain_mm if rain_mm is not None else snow_mm

        visibility_m = data.get("visibility")
        visibility_km = round(visibility_m / 1000.0, 1) if visibility_m is not None else None

        wind_deg = wind.get("deg")
        if wind_deg is not None:
            wind_deg = int(round(wind_deg)) % 361

        return WeatherReadingCreate(
            location_id=UUID(int=0),  # Will be set by caller
            provider="OpenWeatherMap",
            temperature_c=main.get("temp"),
            humidity_pct=main.get("humidity"),
            pressure_hpa=main.get("pressure"),
            wind_speed_ms=wind.get("speed"),
            wind_direction_deg=wind_deg,
            precipitation_mm=precip,
            uv_index=None,  # Not in OWM /weather endpoint
            cloud_cover_pct=clouds.get("all"),
            visibility_km=visibility_km,
            weather_code=wmo_code,
            measured_at=measured_at,
            is_estimated=False,
        )

    def _map_owm_to_wmo(self, owm_code: int) -> int:
        """Map OpenWeatherMap weather codes to WMO codes."""
        # OpenWeatherMap code ranges:
        # 2xx: Thunderstorm
        # 3xx: Drizzle
        # 5xx: Rain
        # 6xx: Snow
        # 7xx: Atmosphere (fog, mist, etc.)
        # 800: Clear
        # 80x: Clouds
        if 200 <= owm_code < 300:
            return 95  # Thunderstorm
        elif 300 <= owm_code < 400:
            return 53  # Drizzle
        elif 500 <= owm_code < 600:
            if owm_code in [500, 501]:
                return 61  # Light/moderate rain
            elif owm_code in [502, 503, 504]:
                return 65  # Heavy rain
            elif owm_code == 511:
                return 67  # Freezing rain
            return 63  # Moderate rain
        elif 600 <= owm_code < 700:
            if owm_code in [600, 601]:
                return 71  # Light snow
            elif owm_code in [602]:
                return 75  # Heavy snow
            return 73  # Moderate snow
        elif 700 <= owm_code < 800:
            if owm_code in [701, 741]:
                return 45  # Fog/mist
            return 48  # Other atmosphere
        elif owm_code == 800:
            return 0  # Clear sky
        elif 801 <= owm_code < 900:
            if owm_code == 801:
                return 1  # Few clouds
            elif owm_code == 802:
                return 2  # Scattered clouds
            elif owm_code == 803:
                return 3  # Broken clouds
            return 3  # Overcast
        return 0  # Default to clear

    async def sync_location_data(self, location_id: UUID) -> bool:
        """Sync weather data for a location (OpenWeatherMap primary, Open-Meteo fallback)."""
        result = await self.session.execute(
            select(LocationModel).where(LocationModel.id == location_id)
        )
        location = result.scalar_one_or_none()
        if not location:
            raise ValueError(f"Location {location_id} not found")

        lat = float(location.latitude)
        lon = float(location.longitude)
        reading: Optional[WeatherReadingCreate] = None

        try:
            reading = await self.fetch_from_openweather(lat, lon)
        except Exception as exc:
            logger.warning("OpenWeatherMap failed for (%s, %s), falling back to Open-Meteo: %s", lat, lon, exc)
            reading = await self.fetch_from_openmeteo(lat, lon)

        if not reading:
            return False

        reading.location_id = location_id
        existing = await self.session.execute(
            select(WeatherReadingModel.id).where(
                WeatherReadingModel.location_id == location_id,
                WeatherReadingModel.provider == reading.provider,
                WeatherReadingModel.measured_at == reading.measured_at,
            ).limit(1)
        )
        if existing.scalar_one_or_none() is None:
            await self.create_reading(reading)
        return True

    def get_weather_info(self, weather_code: Optional[int], uv_index: Optional[float]) -> dict:
        """Get weather description and UV advisory."""
        return {
            "description": get_weather_description(weather_code),
            "uv_advisory": get_uv_advisory(uv_index),
        }


async def scheduled_weather_sync():
    """Background task to sync weather data for all default locations."""
    # This would be called by a scheduler (e.g., APScheduler)
    # For now, it's a placeholder for future implementation
    pass