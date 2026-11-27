"""Knowledge document routes (Phase 4)."""
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.modules.knowledge_documents.models import KnowledgeDocumentModel
from app.modules.knowledge_documents.schema import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
    KnowledgeDocumentResponse,
    KnowledgeDocumentListResponse,
    DocumentIngestRequest,
    DocumentIngestResponse,
)
from app.modules.knowledge_documents.service import KnowledgeDocumentService
from app.modules.users.routes import get_current_active_user
from app.modules.users.models import UserModel

router = APIRouter(tags=["knowledge-documents"])


@router.get("", response_model=KnowledgeDocumentListResponse)
async def list_knowledge_documents(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
):
    """List knowledge documents with pagination."""
    service = KnowledgeDocumentService(session)
    return await service.list_documents(page, page_size, source_type, is_active)


@router.get("/{doc_id}", response_model=KnowledgeDocumentResponse)
async def get_knowledge_document(
    doc_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Get a knowledge document by ID."""
    service = KnowledgeDocumentService(session)
    doc = await service.get_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get chunk count
    from app.modules.document_chunks.models import DocumentChunkModel
    from sqlalchemy import select, func
    chunk_count_result = await session.execute(
        select(func.count(DocumentChunkModel.id)).where(DocumentChunkModel.document_id == doc_id)
    )
    chunk_count = chunk_count_result.scalar() or 0

    return KnowledgeDocumentResponse(
        id=doc.id,
        title=doc.title,
        source_url=doc.source_url,
        source_type=doc.source_type,
        content_hash=doc.content_hash,
        full_text=doc.full_text,
        metadata_json=doc.metadata_json,
        created_at=doc.created_at.isoformat() if doc.created_at else "",
        updated_at=doc.updated_at.isoformat() if doc.updated_at else "",
        is_active=getattr(doc, 'is_active', True),
        chunk_count=chunk_count,
    )


@router.post("", response_model=KnowledgeDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_document(
    doc_data: KnowledgeDocumentCreate,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Create a knowledge document manually."""
    service = KnowledgeDocumentService(session)
    doc = await service.create(doc_data)
    await session.commit()

    return KnowledgeDocumentResponse(
        id=doc.id,
        title=doc.title,
        source_url=doc.source_url,
        source_type=doc.source_type,
        content_hash=doc.content_hash,
        full_text=doc.full_text,
        metadata_json=doc.metadata_json,
        created_at=doc.created_at.isoformat() if doc.created_at else "",
        updated_at=doc.updated_at.isoformat() if doc.updated_at else "",
        is_active=getattr(doc, 'is_active', True),
        chunk_count=0,
    )


@router.patch("/{doc_id}", response_model=KnowledgeDocumentResponse)
async def update_knowledge_document(
    doc_id: UUID,
    doc_data: KnowledgeDocumentUpdate,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Update a knowledge document."""
    service = KnowledgeDocumentService(session)
    doc = await service.update(doc_id, doc_data)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await session.commit()

    return KnowledgeDocumentResponse(
        id=doc.id,
        title=doc.title,
        source_url=doc.source_url,
        source_type=doc.source_type,
        content_hash=doc.content_hash,
        full_text=doc.full_text,
        metadata_json=doc.metadata_json,
        created_at=doc.created_at.isoformat() if doc.created_at else "",
        updated_at=doc.updated_at.isoformat() if doc.updated_at else "",
        is_active=getattr(doc, 'is_active', True),
        chunk_count=0,
    )


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_document(
    doc_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Delete a knowledge document."""
    service = KnowledgeDocumentService(session)
    success = await service.delete(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    await session.commit()


@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_document(
    request: DocumentIngestRequest,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Ingest a document from various sources (PDF, web, manual)."""
    service = KnowledgeDocumentService(session)
    result = await service.ingest_document(request)
    await session.commit()
    return result


@router.post("/ingest/pdf", response_model=DocumentIngestResponse)
async def ingest_pdf(
    file: Annotated[UploadFile, File(description="PDF file to ingest")],
    title: Annotated[str, Form()],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    source_url: Annotated[Optional[str], Form()] = None,
    metadata_json: Annotated[str, Form()] = "{}",
):
    """Ingest a PDF file."""
    import base64
    import json

    file_content = await file.read()
    file_b64 = base64.b64encode(file_content).decode()

    metadata = json.loads(metadata_json) if metadata_json else {}

    request = DocumentIngestRequest(
        title=title,
        source_url=source_url,
        source_type="pdf",
        file_content=file_b64,
        metadata_json=metadata,
    )

    service = KnowledgeDocumentService(session)
    result = await service.ingest_document(request)
    await session.commit()
    return result


@router.post("/ingest/web", response_model=DocumentIngestResponse)
async def ingest_web(
    url: Annotated[str, Form(description="URL to fetch and ingest")],
    title: Annotated[str, Form()],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    metadata_json: Annotated[str, Form()] = "{}",
):
    """Ingest content from a web URL."""
    import json

    metadata = json.loads(metadata_json) if metadata_json else {}

    request = DocumentIngestRequest(
        title=title,
        source_url=url,
        source_type="web",
        metadata_json=metadata,
    )

    service = KnowledgeDocumentService(session)
    result = await service.ingest_document(request)
    await session.commit()
    return result