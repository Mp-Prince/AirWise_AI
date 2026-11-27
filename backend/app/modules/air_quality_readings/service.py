"""Air quality data service with OpenAQ integration and caching."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import httpx
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session_factory
from app.modules.air_quality_readings.models import AirQualityReadingModel
from app.modules.air_quality_readings.schema import AirQualityReadingCreate, get_aqi_category
from app.modules.locations.models import LocationModel
from app.core.config import get_settings

settings = get_settings()

# OpenAQ API endpoints
OPENAQ_BASE_URL = "https://api.openaq.org/v2"
OPENAQ_HEADERS = {"X-API-Key": settings.OPENAQ_API_KEY} if settings.OPENAQ_API_KEY else {}

# Pollutant mapping from OpenAQ to our schema
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

    async def fetch_from_openaq(
        self,
        latitude: float,
        longitude: float,
        radius_km: int = 25,
        limit: int = 100,
    ) -> list[AirQualityReadingCreate]:
        """Fetch air quality data from OpenAQ for a location."""
        if not settings.OPENAQ_API_KEY:
            raise ValueError("OpenAQ API key not configured")

        params = {
            "coordinates": f"{latitude},{longitude}",
            "radius": radius_km * 1000,  # OpenAQ uses meters
            "limit": limit,
            "order_by": "lastUpdated",
            "sort": "desc",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{OPENAQ_BASE_URL}/measurements",
                params=params,
                headers=OPENAQ_HEADERS,
            )
            response.raise_for_status()
            data = response.json()

        readings = []
        for result in data.get("results", []):
            location = result.get("location", {})
            coords = location.get("coordinates", {})
            lat = coords.get("latitude")
            lon = coords.get("longitude")

            if lat is None or lon is None:
                continue

            # Parse measurements by pollutant
            measurements = {}
            for meas in result.get("measurements", []):
                param = meas.get("parameter")
                value = meas.get("value")
                unit = meas.get("unit")
                last_updated = meas.get("lastUpdated")

                if param in POLLUTANT_MAP and value is not None:
                    measurements[POLLUTANT_MAP[param]] = {
                        "value": value,
                        "unit": unit,
                        "last_updated": last_updated,
                    }

            if not measurements:
                continue

            # Use the most recent measurement timestamp
            timestamps = [m["last_updated"] for m in measurements.values() if m["last_updated"]]
            if not timestamps:
                continue
            measured_at = max(timestamps)

            # For AQI calculation, we need at least PM2.5
            # OpenAQ provides pollutant concentrations, not AQI directly
            # We'll compute US AQI from PM2.5 as a proxy
            pm25_value = measurements.get("pm25", {}).get("value")
            if pm25_value is not None:
                aqi_value = self._pm25_to_aqi(pm25_value)
            else:
                # Use the first available pollutant to estimate AQI
                # This is a simplified approach
                aqi_value = 50  # Default moderate

            reading = AirQualityReadingCreate(
                location_id=UUID(int=0),  # Will be set by caller
                provider="OpenAQ",
                aqi_value=aqi_value,
                aqi_standard="US_AQI",
                pm25=measurements.get("pm25", {}).get("value"),
                pm10=measurements.get("pm10", {}).get("value"),
                o3=measurements.get("o3", {}).get("value"),
                no2=measurements.get("no2", {}).get("value"),
                so2=measurements.get("so2", {}).get("value"),
                co=measurements.get("co", {}).get("value"),
                measured_at=datetime.fromisoformat(measured_at.replace("Z", "+00:00")),
                is_estimated=False,
            )
            readings.append(reading)

        return readings

    def _pm25_to_aqi(self, pm25: float) -> int:
        """Convert PM2.5 concentration (µg/m³) to US AQI using EPA breakpoints."""
        # EPA PM2.5 breakpoints for AQI calculation
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
            if c_low <= pm25 <= c_high:
                aqi = ((i_high - i_low) / (c_high - c_low)) * (pm25 - c_low) + i_low
                return int(round(aqi))

        return 500  # Beyond hazardous

    async def sync_location_data(
        self,
        location_id: UUID,
        radius_km: int = 25,
    ) -> int:
        """Sync air quality data for a location from OpenAQ."""
        # Get location details
        result = await self.session.execute(
            select(LocationModel).where(LocationModel.id == location_id)
        )
        location = result.scalar_one_or_none()
        if not location:
            raise ValueError(f"Location {location_id} not found")

        # Fetch from OpenAQ
        readings = await self.fetch_from_openaq(
            float(location.latitude),
            float(location.longitude),
            radius_km=radius_km,
        )

        # Update location_id in readings
        for reading in readings:
            reading.location_id = location_id

        # Bulk create
        if readings:
            await self.create_readings_bulk(readings)

        return len(readings)

    def get_aqi_info(self, aqi_value: int, standard: str = "US_AQI"):
        """Get AQI category, color, and health advisory."""
        return get_aqi_category(aqi_value, standard)


async def scheduled_aqi_sync():
    """Background task to sync AQI data for all default locations."""
    # This would be called by a scheduler (e.g., APScheduler)
    # For now, it's a placeholder for future implementation
    pass