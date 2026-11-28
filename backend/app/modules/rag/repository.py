"""RAG repository for audit logs and knowledge base statistics (Phase 4)."""
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.document_chunks.repository import DocumentChunkRepository
from app.modules.knowledge_documents.repository import KnowledgeDocumentRepository
from app.modules.rag.models import KnowledgeAuditLogModel


class RAGRepository:
    """Database access layer for RAG audit logging and aggregated stats."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.doc_repo = KnowledgeDocumentRepository(session)
        self.chunk_repo = DocumentChunkRepository(session)

    async def log_query(
        self,
        user_id: Optional[UUID],
        query: str,
        documents_retrieved: int,
        processing_time_ms: int,
        model: str,
        is_successful: bool = True,
    ) -> KnowledgeAuditLogModel:
        entry = KnowledgeAuditLogModel(
            user_id=str(user_id) if user_id else None,
            query=query[:2000],
            documents_retrieved=documents_retrieved,
            processing_time_ms=processing_time_ms,
            model=model,
            is_successful=is_successful,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def get_stats(self) -> dict:
        total_docs, active_docs = await self.doc_repo.count_totals()
        total_chunks = await self.chunk_repo.count_all()
        return {
            "total_documents": total_docs,
            "active_documents": active_docs,
            "total_chunks": total_chunks,
        }
