"""Chat message repository for database access (Phase 5)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat_messages.models import ChatMessageModel


class ChatMessageRepository:
    """Database operations for chat_messages."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        cited_chunk_ids: list[uuid.UUID] | None = None,
    ) -> ChatMessageModel:
        msg = ChatMessageModel(
            conversation_id=conversation_id,
            role=role,
            content=content,
            cited_chunk_ids=cited_chunk_ids or [],
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(msg)
        await self.session.flush()
        return msg

    async def list_for_conversation(
        self, conversation_id: uuid.UUID, limit: int = 100
    ) -> list[ChatMessageModel]:
        result = await self.session.execute(
            select(ChatMessageModel)
            .where(ChatMessageModel.conversation_id == conversation_id)
            .order_by(ChatMessageModel.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
