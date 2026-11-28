"""Daily routine repository for database access (Phase 6)."""
from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.daily_routines.models import DailyRoutineModel


class DailyRoutineRepository:
    """Database access layer for daily_routines."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_for_user(
        self, routine_id: UUID, user_id: UUID
    ) -> Optional[DailyRoutineModel]:
        result = await self.session.execute(
            select(DailyRoutineModel).where(
                DailyRoutineModel.id == routine_id,
                DailyRoutineModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        routine_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[DailyRoutineModel]:
        query = select(DailyRoutineModel).where(
            DailyRoutineModel.user_id == user_id,
            DailyRoutineModel.is_active.is_(True),
        )
        if date_from and date_to:
            query = query.where(
                or_(
                    DailyRoutineModel.routine_date.between(date_from, date_to),
                    DailyRoutineModel.routine_date.is_(None),
                )
            )
        elif date_from:
            query = query.where(
                or_(
                    DailyRoutineModel.routine_date >= date_from,
                    DailyRoutineModel.routine_date.is_(None),
                )
            )
        elif date_to:
            query = query.where(
                or_(
                    DailyRoutineModel.routine_date <= date_to,
                    DailyRoutineModel.routine_date.is_(None),
                )
            )

        if routine_type:
            query = query.where(DailyRoutineModel.routine_type == routine_type)
        if status:
            query = query.where(DailyRoutineModel.status == status)

        query = query.order_by(
            DailyRoutineModel.routine_date.asc().nullslast(),
            DailyRoutineModel.start_time.asc(),
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add(self, routine: DailyRoutineModel) -> DailyRoutineModel:
        self.session.add(routine)
        await self.session.flush()
        return routine

    async def delete(self, routine: DailyRoutineModel) -> None:
        await self.session.delete(routine)
        await self.session.flush()
