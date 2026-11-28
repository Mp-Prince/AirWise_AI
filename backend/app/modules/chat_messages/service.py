"""Chat message service (Phase 5)."""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat_messages.models import ChatMessageModel
from app.modules.chat_messages.repository import ChatMessageRepository


class ChatMessageService:
    """Business logic for chat messages."""

    def __init__(self, session: AsyncSession):
        self.repo = ChatMessageRepository(session)

    async def add_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        cited_chunk_ids: list[uuid.UUID] | None = None,
    ) -> ChatMessageModel:
        return await self.repo.create(
            conversation_id=conversation_id,
            role=role,
            content=content,
            cited_chunk_ids=cited_chunk_ids,
        )

    async def get_history(
        self, conversation_id: uuid.UUID, limit: int = 100
    ) -> list[ChatMessageModel]:
        return await self.repo.list_for_conversation(conversation_id, limit=limit)
