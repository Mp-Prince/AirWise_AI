"""Recommendation repository for database access (Phase 6)."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.recommendations.models import RecommendationModel


class RecommendationRepository:
    """Database access layer for recommendations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_for_user(
        self, rec_id: UUID, user_id: UUID
    ) -> Optional[RecommendationModel]:
        result = await self.session.execute(
            select(RecommendationModel).where(
                RecommendationModel.id == rec_id,
                RecommendationModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: UUID,
        category: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[RecommendationModel]:
        query = select(RecommendationModel).where(RecommendationModel.user_id == user_id)
        if category:
            query = query.where(RecommendationModel.category == category)
        if status:
            query = query.where(RecommendationModel.status == status)
        query = query.order_by(RecommendationModel.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_many(self, recs: list[RecommendationModel]) -> None:
        self.session.add_all(recs)
        await self.session.flush()
