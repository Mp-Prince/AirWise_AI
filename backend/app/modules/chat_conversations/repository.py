"""Chat conversation repository for database access (Phase 5)."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat_conversations.models import ChatConversationModel


class ChatConversationRepository:
    """Database operations for chat_conversations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_for_user(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[ChatConversationModel]:
        result = await self.session.execute(
            select(ChatConversationModel).where(
                ChatConversationModel.id == conversation_id,
                ChatConversationModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> list[ChatConversationModel]:
        result = await self.session.execute(
            select(ChatConversationModel)
            .where(ChatConversationModel.user_id == user_id)
            .order_by(ChatConversationModel.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(
        self, user_id: uuid.UUID, title: Optional[str] = None
    ) -> ChatConversationModel:
        now = datetime.now(timezone.utc)
        conv = ChatConversationModel(
            user_id=user_id,
            title=(title[:200] if title else None),
            created_at=now,
            updated_at=now,
        )
        self.session.add(conv)
        await self.session.flush()
        return conv

    async def touch(self, conv: ChatConversationModel) -> None:
        conv.updated_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def delete(self, conv: ChatConversationModel) -> None:
        await self.session.delete(conv)
        await self.session.flush()
