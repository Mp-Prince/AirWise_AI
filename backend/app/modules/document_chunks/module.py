"""Document chunk API module (Phase 4)."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.modules.document_chunks.schema import (
    DocumentChunkResponse,
    RetrievalRequest,
    RetrievalResponse,
)
from app.modules.document_chunks.service import DocumentChunkService
from app.modules.users.models import UserModel
from app.modules.users.routes import get_current_active_user

router = APIRouter(tags=["document-chunks"])


@router.get("/document/{document_id}", response_model=list[DocumentChunkResponse])
async def get_document_chunks(
    document_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Get all chunks for a document."""
    service = DocumentChunkService(session)
    chunks = await service.get_chunks_for_document(document_id)

    return [
        DocumentChunkResponse(
            id=chunk.id,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            page_number=chunk.page_number,
            content=chunk.content,
            token_count=chunk.token_count,
            created_at=chunk.created_at.isoformat() if chunk.created_at else "",
        )
        for chunk in chunks
    ]


@router.post("/retrieve", response_model=RetrievalResponse)
async def retrieve_chunks(
    request: RetrievalRequest,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Perform semantic retrieval on document chunks."""
    service = DocumentChunkService(session)
    try:
        return await service.retrieve(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
