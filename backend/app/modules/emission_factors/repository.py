"""Emission factor repository for database access (Phase 7)."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.emission_factors.models import EmissionFactorModel


class EmissionFactorRepository:
    """Database access layer for emission_factors."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(self) -> list[EmissionFactorModel]:
        result = await self.session.execute(
            select(EmissionFactorModel).order_by(EmissionFactorModel.activity.asc())
        )
        return list(result.scalars().all())

    async def get_by_activity(self, activity: str) -> Optional[EmissionFactorModel]:
        result = await self.session.execute(
            select(EmissionFactorModel).where(EmissionFactorModel.activity == activity)
        )
        return result.scalar_one_or_none()

    async def add_many(self, factors: list[EmissionFactorModel]) -> None:
        self.session.add_all(factors)
        await self.session.flush()
