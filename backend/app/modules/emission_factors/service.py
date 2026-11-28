"""Emission factor service with curated India & international references (Phase 7)."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.emission_factors.models import EmissionFactorModel
from app.modules.emission_factors.repository import EmissionFactorRepository
from app.modules.emission_factors.schema import EmissionFactorListResponse, EmissionFactorResponse

DEFAULT_EMISSION_FACTORS = [
    {
        "activity": "petrol_car",
        "co2e_kg_per_unit": 0.1710,
        "unit": "kgCO2e/km",
        "source": "UK DESNZ / DEFRA 2024 Conversion Factors (Average petrol car)",
        "region": "Global / India proxy",
    },
    {
        "activity": "diesel_car",
        "co2e_kg_per_unit": 0.1680,
        "unit": "kgCO2e/km",
        "source": "UK DESNZ / DEFRA 2024 Conversion Factors (Average diesel car)",
        "region": "Global / India proxy",
    },
    {
        "activity": "petrol_two_wheeler",
        "co2e_kg_per_unit": 0.0680,
        "unit": "kgCO2e/km",
        "source": "India GHG Program / MoEFCC Transport Factor (Average petrol 2-wheeler)",
        "region": "India",
    },
    {
        "activity": "auto_rickshaw_cng",
        "co2e_kg_per_unit": 0.0620,
        "unit": "kgCO2e/km",
        "source": "India GHG Program / CPCB Urban 3-wheeler CNG estimate",
        "region": "India",
    },
    {
        "activity": "city_bus",
        "co2e_kg_per_unit": 0.0490,
        "unit": "kgCO2e/pkm",
        "source": "India GHG Program / Urban Public Bus passenger-km average",
        "region": "India",
    },
    {
        "activity": "metro_rail",
        "co2e_kg_per_unit": 0.0280,
        "unit": "kgCO2e/pkm",
        "source": "CEA India Grid & Urban Metro Rail passenger-km average",
        "region": "India",
    },
    {
        "activity": "electric_car",
        "co2e_kg_per_unit": 0.0530,
        "unit": "kgCO2e/km",
        "source": "CEA India Grid CO2 Baseline (~0.716 kgCO2e/kWh, ~0.074-0.15 kWh/km proxy)",
        "region": "India",
    },
    {
        "activity": "bicycle",
        "co2e_kg_per_unit": 0.0000,
        "unit": "kgCO2e/km",
        "source": "Zero operational tailpipe and fuel-cycle emissions",
        "region": "Global",
    },
    {
        "activity": "walking",
        "co2e_kg_per_unit": 0.0000,
        "unit": "kgCO2e/km",
        "source": "Zero operational tailpipe and fuel-cycle emissions",
        "region": "Global",
    },
    {
        "activity": "grid_electricity_in",
        "co2e_kg_per_unit": 0.7160,
        "unit": "kgCO2e/kWh",
        "source": "Central Electricity Authority (CEA) India CO2 Baseline Database v19",
        "region": "India",
    },
]


class EmissionFactorService:
    """Service for seeding and querying published emission factors."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = EmissionFactorRepository(session)

    async def ensure_defaults_seeded(self) -> list[EmissionFactorModel]:
        existing = await self.repo.list_all()
        existing_map = {f.activity for f in existing}
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)

        to_create = [
            EmissionFactorModel(
                activity=item["activity"],
                co2e_kg_per_unit=item["co2e_kg_per_unit"],
                unit=item["unit"],
                source=item["source"],
                region=item["region"],
                valid_from=now,
            )
            for item in DEFAULT_EMISSION_FACTORS
            if item["activity"] not in existing_map
        ]
        if to_create:
            await self.repo.add_many(to_create)
            return await self.repo.list_all()
        return existing

    async def list_factors(self) -> EmissionFactorListResponse:
        factors = await self.ensure_defaults_seeded()
        return EmissionFactorListResponse(
            factors=[EmissionFactorResponse.model_validate(f) for f in factors],
            total=len(factors),
        )

    async def get_by_activity(self, activity: str) -> Optional[EmissionFactorModel]:
        await self.ensure_defaults_seeded()
        return await self.repo.get_by_activity(activity)
