"""Air quality data service with OpenAQ v3 integration and caching."""
from datetime import datetime, timezone
import logging
import math
from typing import Optional
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.air_quality_readings.models import AirQualityReadingModel
from app.modules.air_quality_readings.schema import AirQualityReadingCreate, get_aqi_category
from app.modules.locations.models import LocationModel
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# OpenAQ v3 API base URL (v2 was retired)
OPENAQ_BASE_URL = "https://api.openaq.org/v3"
OPENAQ_MAX_RADIUS_METERS = 25000

# Pollutant mapping from OpenAQ v3 parameter names to our schema
POLLUTANT_MAP = {
    "pm25": "pm25",
    "pm10": "pm10",
    "o3": "o3",
    "no2": "no2",
    "so2": "so2",
    "co": "co",
}


class AirQualityService:
    """Service for managing air quality data with external provider integration."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_latest_reading(
        self,
        location_id: UUID,
        provider: Optional[str] = None,
    ) -> Optional[AirQualityReadingModel]:
        """Get the most recent air quality reading for a location."""
        query = select(AirQualityReadingModel).where(
            AirQualityReadingModel.location_id == location_id
        )
        if provider:
            query = query.where(AirQualityReadingModel.provider == provider)
        query = query.order_by(AirQualityReadingModel.measured_at.desc()).limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_readings(
        self,
        location_id: UUID,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        provider: Optional[str] = None,
        limit: int = 100,
    ) -> list[AirQualityReadingModel]:
        """Get air quality readings for a location within a time range."""
        query = select(AirQualityReadingModel).where(
            AirQualityReadingModel.location_id == location_id
        )
        if start_time:
            query = query.where(AirQualityReadingModel.measured_at >= start_time)
        if end_time:
            query = query.where(AirQualityReadingModel.measured_at <= end_time)
        if provider:
            query = query.where(AirQualityReadingModel.provider == provider)
        query = query.order_by(AirQualityReadingModel.measured_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_reading(self, reading_data: AirQualityReadingCreate) -> AirQualityReadingModel:
        """Create a new air quality reading."""
        reading = AirQualityReadingModel(**reading_data.model_dump())
        self.session.add(reading)
        await self.session.flush()
        return reading

    async def create_readings_bulk(
        self, readings_data: list[AirQualityReadingCreate]
    ) -> list[AirQualityReadingModel]:
        """Create multiple air quality readings in bulk."""
        readings = [AirQualityReadingModel(**data.model_dump()) for data in readings_data]
        self.session.add_all(readings)
        await self.session.flush()
        return readings

    @staticmethod
    def _normalize_value(param: str, value: float, unit: Optional[str]) -> Optional[float]:
        """Normalize pollutant concentration units to schema units (µg/m³, except CO in mg/m³)."""
        if value is None or value < 0:
            return None
        unit_norm = (unit or "").strip().lower()
        if param == "co":
            if unit_norm in {"µg/m³", "ug/m3", "µg/m3", "ug/m³"}:
                return round(value / 1000.0, 4)
            return round(value, 4)
        # PM2.5, PM10, O3, NO2, SO2 -> µg/m³
        if unit_norm in {"mg/m³", "mg/m3"}:
            return round(value * 1000.0, 2)
        return round(value, 2)

    async def fetch_from_openaq(
        self,
        latitude: float,
        longitude: float,
        radius_km: int = 25,
        limit: int = 10,
    ) -> list[AirQualityReadingCreate]:
        """Fetch latest air quality readings from OpenAQ v3 near coordinates."""
        settings = get_settings()
        if not settings.OPENAQ_API_KEY:
            raise ValueError("OpenAQ API key not configured")

        headers = {"X-API-Key": settings.OPENAQ_API_KEY}
        radius_m = min(max(int(radius_km * 1000), 1000), OPENAQ_MAX_RADIUS_METERS)
        params = {
            "coordinates": f"{latitude:.4f},{longitude:.4f}",
            "radius": radius_m,
            "limit": min(limit, 20),
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            loc_resp = await client.get(
                f"{OPENAQ_BASE_URL}/locations",
                params=params,
                headers=headers,
            )
            loc_resp.raise_for_status()
            locations = loc_resp.json().get("results", [])

            if not locations:
                return []

            # Prefer closest locations that have sensors for PM2.5 or PM10
            def _rank_location(loc: dict) -> tuple[int, float]:
                sensor_params = {
                    (s.get("parameter") or {}).get("name", "").lower()
                    for s in loc.get("sensors", [])
                }
                has_pm = 0 if ("pm25" in sensor_params or "pm10" in sensor_params) else 1
                distance = loc.get("distance")
                return (has_pm, float(distance) if distance is not None else float("inf"))

            locations.sort(key=_rank_location)

            readings: list[AirQualityReadingCreate] = []
            for loc in locations[:5]:
                loc_id = loc.get("id")
                if not loc_id:
                    continue

                sensor_map = {
                    s["id"]: (s.get("parameter") or {})
                    for s in loc.get("sensors", [])
                    if s.get("id") is not None
                }
                if not sensor_map:
                    continue

                latest_resp = await client.get(
                    f"{OPENAQ_BASE_URL}/locations/{loc_id}/latest",
                    headers=headers,
                )
                if latest_resp.status_code == 404:
                    continue
                latest_resp.raise_for_status()
                latest_results = latest_resp.json().get("results", [])

                measurements: dict[str, dict] = {}
                for meas in latest_results:
                    sensor_id = meas.get("sensorsId")
                    param_info = sensor_map.get(sensor_id)
                    if not param_info:
                        continue

                    raw_param = (param_info.get("name") or "").lower()
                    mapped_param = POLLUTANT_MAP.get(raw_param)
                    if not mapped_param:
                        continue

                    norm_val = self._normalize_value(
                        mapped_param,
                        meas.get("value"),
                        param_info.get("units"),
                    )
                    if norm_val is None:
                        continue

                    dt_obj = meas.get("datetime") or {}
                    dt_str = dt_obj.get("utc") or dt_obj.get("local")
                    if not dt_str:
                        continue

                    parsed_dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                    prev = measurements.get(mapped_param)
                    if prev is None or parsed_dt > prev["measured_at"]:
                        measurements[mapped_param] = {
                            "value": norm_val,
                            "measured_at": parsed_dt,
                        }

                if not measurements:
                    continue

                # Never invent an AQI if neither PM2.5 nor PM10 is available
                pm25_value = measurements.get("pm25", {}).get("value")
                pm10_value = measurements.get("pm10", {}).get("value")
                if pm25_value is not None:
                    aqi_value = self._pm25_to_aqi(pm25_value)
                elif pm10_value is not None:
                    aqi_value = self._pm10_to_aqi(pm10_value)
                else:
                    continue

                measured_at = max(m["measured_at"] for m in measurements.values())
                readings.append(
                    AirQualityReadingCreate(
                        location_id=UUID(int=0),  # Set by sync_location_data
                        provider="OpenAQ",
                        aqi_value=aqi_value,
                        aqi_standard="US_AQI",
                        pm25=pm25_value,
                        pm10=pm10_value,
                        o3=measurements.get("o3", {}).get("value"),
                        no2=measurements.get("no2", {}).get("value"),
                        so2=measurements.get("so2", {}).get("value"),
                        co=measurements.get("co", {}).get("value"),
                        measured_at=measured_at,
                        is_estimated=False,
                    )
                )
                # Use the closest valid monitoring station
                break

        return readings

    def _pm25_to_aqi(self, pm25: float) -> int:
        """Convert PM2.5 concentration (µg/m³) to US AQI using EPA breakpoints."""
        # EPA specifies truncating PM2.5 to 1 decimal place before lookup
        truncated = math.floor(max(pm25, 0.0) * 10) / 10.0
        breakpoints = [
            (0.0, 12.0, 0, 50),
            (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300),
            (250.5, 350.4, 301, 400),
            (350.5, 500.4, 401, 500),
        ]

        for c_low, c_high, i_low, i_high in breakpoints:
            if c_low <= truncated <= c_high:
                aqi = ((i_high - i_low) / (c_high - c_low)) * (truncated - c_low) + i_low
                return int(round(aqi))

        return 500

    def _pm10_to_aqi(self, pm10: float) -> int:
        """Convert PM10 concentration (µg/m³) to US AQI using EPA breakpoints."""
        truncated = int(math.floor(max(pm10, 0.0)))
        breakpoints = [
            (0, 54, 0, 50),
            (55, 154, 51, 100),
            (155, 254, 101, 150),
            (255, 354, 151, 200),
            (355, 424, 201, 300),
            (425, 504, 301, 400),
            (505, 604, 401, 500),
        ]

        for c_low, c_high, i_low, i_high in breakpoints:
            if c_low <= truncated <= c_high:
                aqi = ((i_high - i_low) / (c_high - c_low)) * (truncated - c_low) + i_low
                return int(round(aqi))

        return 500

    async def sync_location_data(
        self,
        location_id: UUID,
        radius_km: int = 25,
    ) -> int:
        """Sync air quality data for a location from OpenAQ v3."""
        result = await self.session.execute(
            select(LocationModel).where(LocationModel.id == location_id)
        )
        location = result.scalar_one_or_none()
        if not location:
            raise ValueError(f"Location {location_id} not found")

        readings = await self.fetch_from_openaq(
            float(location.latitude),
            float(location.longitude),
            radius_km=radius_km,
        )

        new_readings: list[AirQualityReadingCreate] = []
        for reading in readings:
            reading.location_id = location_id
            existing = await self.session.execute(
                select(AirQualityReadingModel.id).where(
                    AirQualityReadingModel.location_id == location_id,
                    AirQualityReadingModel.provider == reading.provider,
                    AirQualityReadingModel.measured_at == reading.measured_at,
                ).limit(1)
            )
            if existing.scalar_one_or_none() is None:
                new_readings.append(reading)

        if new_readings:
            await self.create_readings_bulk(new_readings)

        return len(new_readings)

    def get_aqi_info(self, aqi_value: int, standard: str = "US_AQI"):
        """Get AQI category, color, and health advisory."""
        return get_aqi_category(aqi_value, standard)


async def scheduled_aqi_sync():
    """Background task to sync AQI data for all default locations."""
    pass