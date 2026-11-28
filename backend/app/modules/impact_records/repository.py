"""Impact record repository for database access (Phase 7)."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.impact_records.models import ImpactRecordModel


class ImpactRecordRepository:
    """Database access layer for impact_records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_for_user(
        self, record_id: UUID, user_id: UUID
    ) -> Optional[ImpactRecordModel]:
        result = await self.session.execute(
            select(ImpactRecordModel).where(
                ImpactRecordModel.id == record_id,
                ImpactRecordModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: UUID,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None,
        limit: int = 200,
    ) -> list[ImpactRecordModel]:
        query = select(ImpactRecordModel).where(ImpactRecordModel.user_id == user_id)
        if start_dt:
            query = query.where(ImpactRecordModel.recorded_at >= start_dt)
        if end_dt:
            query = query.where(ImpactRecordModel.recorded_at <= end_dt)
        query = query.order_by(ImpactRecordModel.recorded_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add(self, record: ImpactRecordModel) -> ImpactRecordModel:
        self.session.add(record)
        await self.session.flush()
        return record

    async def delete(self, record: ImpactRecordModel) -> None:
        await self.session.delete(record)
        await self.session.flush()
