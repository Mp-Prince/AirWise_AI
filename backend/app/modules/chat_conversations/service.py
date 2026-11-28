"""Chat conversation service (Phase 5)."""
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat_conversations.models import ChatConversationModel
from app.modules.chat_conversations.repository import ChatConversationRepository


class ChatConversationService:
    """Business logic for user chat conversations."""

    def __init__(self, session: AsyncSession):
        self.repo = ChatConversationRepository(session)

    async def get_for_user(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[ChatConversationModel]:
        return await self.repo.get_by_id_for_user(conversation_id, user_id)

    async def list_for_user(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> list[ChatConversationModel]:
        return await self.repo.list_for_user(user_id, limit=limit)

    async def create_from_prompt(
        self, user_id: uuid.UUID, first_message: str
    ) -> ChatConversationModel:
        clean = " ".join(first_message.strip().split())
        title = clean[:80] + ("..." if len(clean) > 80 else "")
        return await self.repo.create(user_id, title=title or "New conversation")

    async def touch(self, conv: ChatConversationModel) -> None:
        await self.repo.touch(conv)

    async def delete_for_user(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        conv = await self.repo.get_by_id_for_user(conversation_id, user_id)
        if not conv:
            return False
        await self.repo.delete(conv)
        return True
