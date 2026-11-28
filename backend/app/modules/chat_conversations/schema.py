"""Chat conversation schemas (Phase 5)."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ConversationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ChatMessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    cited_chunk_ids: list[UUID] = []
    created_at: datetime


class ConversationDetail(ConversationSummary):
    messages: list[ChatMessageSchema] = []


class ConversationListResponse(BaseModel):
    conversations: list[ConversationSummary]
    total: int
