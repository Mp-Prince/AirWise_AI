"""Chat message schemas (Phase 5)."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ChatMessageCreate(BaseModel):
    conversation_id: UUID
    role: str
    content: str
    cited_chunk_ids: list[UUID] = []


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    cited_chunk_ids: list[UUID] = []
    created_at: datetime
