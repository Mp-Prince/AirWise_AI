"""RAG API module (Phase 4)."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.modules.knowledge_documents.service import KnowledgeDocumentService
from app.modules.rag.schema import RAGRequest, RAGResponse
from app.modules.rag.service import RAGService
from app.modules.users.models import UserModel
from app.modules.users.routes import get_current_active_user

router = APIRouter(tags=["rag"])


@router.post("/query", response_model=RAGResponse)
async def rag_query(
    request: RAGRequest,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """RAG-powered query: retrieve relevant chunks and return citations."""
    rag_service = RAGService(session)
    try:
        response = await rag_service.query_with_citations(request, user_id=current_user.id)
        await session.commit()
        return response
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/documents", response_model=list[dict])
async def list_knowledge_documents(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """List all knowledge documents available for RAG."""
    service = KnowledgeDocumentService(session)
    result = await service.list_documents(page=1, page_size=100)
    return [
        {
            "id": str(doc.id),
            "title": doc.title,
            "source_type": doc.source_type,
            "source_url": doc.source_url,
            "is_active": doc.is_active,
            "chunk_count": doc.chunk_count,
            "created_at": doc.created_at,
        }
        for doc in result.documents
    ]


@router.get("/stats", response_model=dict)
async def get_rag_stats(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Get RAG knowledge base statistics."""
    rag_service = RAGService(session)
    return await rag_service.get_stats()
