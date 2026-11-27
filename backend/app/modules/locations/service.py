"""Location service with geocoding integration."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

import httpx
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session_factory
from app.modules.locations.models import LocationModel
from app.modules.locations.schema import LocationCreate, LocationUpdate
from app.core.config import get_settings

settings = get_settings()

# Geocoding API endpoints (using OpenStreetMap Nominatim as free option)
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
GEOCODING_HEADERS = {
    "User-Agent": "AirWise AI / 1.0 (airwise@example.com)",
}

# Geoapify geocoding (optional, for when Nominatim is rate limited)
GEOAPIFY_BASE_URL = "https://api.geoapify.com/v1/geocode"


class LocationService:
    """Service for managing user locations with geocoding."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, location_id: UUID) -> Optional[LocationModel]:
        """Get location by ID."""
        result = await self.session.execute(
            select(LocationModel).where(LocationModel.id == location_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: UUID,
        include_default_only: bool = False,
    ) -> list[LocationModel]:
        """Get all locations for a user."""
        query = select(LocationModel).where(LocationModel.user_id == user_id)
        if include_default_only:
            query = query.where(LocationModel.is_default == True)
        query = query.order_by(LocationModel.is_default.desc(), LocationModel.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_default_location(self, user_id: UUID) -> Optional[LocationModel]:
        """Get user's default location."""
        result = await self.session.execute(
            select(LocationModel).where(
                LocationModel.user_id == user_id,
                LocationModel.is_default == True,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: UUID, location_data: LocationCreate) -> LocationModel:
        """Create a new location for a user."""
        # If this is the first location or explicitly set as default, make it default
        existing_count_result = await self.session.execute(
            select(func.count(LocationModel.id)).where(LocationModel.user_id == user_id)
        )
        existing_count = existing_count_result.scalar() or 0

        is_default = location_data.is_default or existing_count == 0

        # If setting as default, unset other defaults
        if is_default:
            await self._unset_default_for_user(user_id)

        # Map schema fields (lat/lon) to model fields (latitude/longitude)
        create_data = location_data.model_dump()
        location = LocationModel(
            user_id=user_id,
            latitude=create_data.get("lat"),
            longitude=create_data.get("lon"),
            name=create_data.get("name"),
            city=create_data.get("city"),
            state=create_data.get("state"),
            country=create_data.get("country"),
            is_default=is_default,
        )
        self.session.add(location)
        await self.session.flush()
        return location

    async def update(
        self,
        location_id: UUID,
        user_id: UUID,
        location_data: LocationUpdate,
    ) -> Optional[LocationModel]:
        """Update a location."""
        location = await self.get_by_id(location_id)
        if not location or location.user_id != user_id:
            return None

        # If setting as default, unset other defaults
        if location_data.is_default is True:
            await self._unset_default_for_user(user_id)

        # Map schema fields (lat/lon) to model fields (latitude/longitude)
        update_data = location_data.model_dump(exclude_unset=True)
        field_mapping = {
            "lat": "latitude",
            "lon": "longitude",
        }
        for field, value in update_data.items():
            model_field = field_mapping.get(field, field)
            setattr(location, model_field, value)

        location.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return location

    async def delete(self, location_id: UUID, user_id: UUID) -> bool:
        """Delete a location."""
        location = await self.get_by_id(location_id)
        if not location or location.user_id != user_id:
            return False

        was_default = location.is_default
        await self.session.delete(location)
        await self.session.flush()

        # If deleted was default, make another location default
        if was_default:
            remaining = await self.get_by_user(user_id)
            if remaining:
                remaining[0].is_default = True
                await self.session.flush()

        return True

    async def set_default(self, location_id: UUID, user_id: UUID) -> Optional[LocationModel]:
        """Set a location as the user's default."""
        location = await self.get_by_id(location_id)
        if not location or location.user_id != user_id:
            return None

        await self._unset_default_for_user(user_id)
        location.is_default = True
        location.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return location

    async def _unset_default_for_user(self, user_id: UUID):
        """Unset default flag for all user locations."""
        result = await self.session.execute(
            select(LocationModel).where(
                LocationModel.user_id == user_id,
                LocationModel.is_default == True,
            )
        )
        for loc in result.scalars().all():
            loc.is_default = False
            loc.updated_at = datetime.now(timezone.utc)

    async def geocode_address(
        self,
        address: str,
        limit: int = 5,
    ) -> list[dict]:
        """Geocode an address to coordinates using Nominatim."""
        params = {
            "q": address,
            "format": "json",
            "limit": limit,
            "addressdetails": 1,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{NOMINATIM_BASE_URL}/search",
                params=params,
                headers=GEOCODING_HEADERS,
            )
            response.raise_for_status()
            return response.json()

    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[dict]:
        """Reverse geocode coordinates to address using Nominatim."""
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "addressdetails": 1,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{NOMINATIM_BASE_URL}/reverse",
                params=params,
                headers=GEOCODING_HEADERS,
            )
            response.raise_for_status()
            return response.json()

    async def geocode_address_geoapify(
        self,
        address: str,
        limit: int = 5,
    ) -> list[dict]:
        """Geocode an address to coordinates using Geoapify (fallback for Nominatim rate limits)."""
        if not settings.GEOCODING_API_KEY:
            return []

        params = {
            "text": address,
            "limit": limit,
            "apiKey": settings.GEOCODING_API_KEY,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{GEOAPIFY_BASE_URL}/search",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("features", [])

    async def search_locations(
        self,
        query: str,
        user_id: UUID,
        limit: int = 10,
    ) -> list[dict]:
        """Search locations by query (combines user locations and geocoding)."""
        # First, search user's saved locations
        user_locations = await self.get_by_user(user_id)
        user_results = [
            {
                "id": str(loc.id),
                "name": loc.name,
                "lat": float(loc.latitude),
                "lon": float(loc.longitude),
                "city": loc.city,
                "state": loc.state,
                "country": loc.country,
                "is_saved": True,
                "is_default": loc.is_default,
                "display_name": f"{loc.name}" + (f", {loc.city}" if loc.city else "") + (f", {loc.state}" if loc.state else ""),
            }
            for loc in user_locations
            if query.lower() in loc.name.lower()
            or (loc.city and query.lower() in loc.city.lower())
            or (loc.state and query.lower() in loc.state.lower())
        ]

        # Then, geocode for new locations (try Nominatim first, fallback to Geoapify)
        geocode_results = []
        try:
            geocode_results = await self.geocode_address(query, limit=limit)
        except Exception:
            # Fallback to Geoapify if Nominatim fails (e.g., rate limited)
            try:
                geoapify_features = await self.geocode_address_geoapify(query, limit=limit)
                geocode_results = [
                    {
                        "lat": f["geometry"]["coordinates"][1],
                        "lon": f["geometry"]["coordinates"][0],
                        "display_name": f["properties"].get("formatted", ""),
                        "address": {
                            "city": f["properties"].get("city"),
                            "state": f["properties"].get("state"),
                            "country": f["properties"].get("country"),
                        },
                    }
                    for f in geoapify_features
                ]
            except Exception:
                geocode_results = []

        geocode_formatted = [
            {
                "id": None,
                "name": r.get("display_name", "").split(",")[0],
                "lat": float(r["lat"]),
                "lon": float(r["lon"]),
                "city": r.get("address", {}).get("city")
                    or r.get("address", {}).get("town")
                    or r.get("address", {}).get("village"),
                "state": r.get("address", {}).get("state"),
                "country": r.get("address", {}).get("country"),
                "is_saved": False,
                "is_default": False,
                "display_name": r.get("display_name"),
            }
            for r in geocode_results
        ]

        # Combine and deduplicate
        all_results = user_results + geocode_formatted
        seen = set()
        unique_results = []
        for r in all_results:
            key = (round(r["lat"], 4), round(r["lon"], 4))
            if key not in seen:
                seen.add(key)
                unique_results.append(r)
                if len(unique_results) >= limit:
                    break

        return unique_results