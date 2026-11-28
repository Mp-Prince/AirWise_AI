"""Knowledge document repository for database access (Phase 4)."""
import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.document_chunks.models import DocumentChunkModel
from app.modules.knowledge_documents.models import KnowledgeDocumentModel


class KnowledgeDocumentRepository:
    """Database access layer for knowledge_documents."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, doc_id: uuid.UUID) -> Optional[KnowledgeDocumentModel]:
        result = await self.session.execute(
            select(KnowledgeDocumentModel)
            .where(KnowledgeDocumentModel.id == doc_id)
            .options(selectinload(KnowledgeDocumentModel.chunks))
        )
        return result.scalars().first()

    async def get_by_content_hash(self, content_hash: str) -> Optional[KnowledgeDocumentModel]:
        result = await self.session.execute(
            select(KnowledgeDocumentModel).where(
                KnowledgeDocumentModel.content_hash == content_hash
            )
        )
        return result.scalars().first()

    async def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        source_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[list[KnowledgeDocumentModel], int]:
        query = select(KnowledgeDocumentModel)
        count_query = select(func.count(KnowledgeDocumentModel.id))

        if source_type:
            query = query.where(KnowledgeDocumentModel.source_type == source_type)
            count_query = count_query.where(KnowledgeDocumentModel.source_type == source_type)

        if is_active is not None:
            query = query.where(KnowledgeDocumentModel.is_active == is_active)
            count_query = count_query.where(KnowledgeDocumentModel.is_active == is_active)

        query = (
            query.order_by(KnowledgeDocumentModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        docs_result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)
        return list(docs_result.scalars().all()), (count_result.scalar() or 0)

    async def get_chunk_counts(self, document_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
        if not document_ids:
            return {}
        result = await self.session.execute(
            select(DocumentChunkModel.document_id, func.count(DocumentChunkModel.id))
            .where(DocumentChunkModel.document_id.in_(document_ids))
            .group_by(DocumentChunkModel.document_id)
        )
        return {row[0]: row[1] for row in result.all()}

    async def count_totals(self) -> tuple[int, int]:
        """Return (total_documents, active_documents)."""
        total_res = await self.session.execute(select(func.count(KnowledgeDocumentModel.id)))
        active_res = await self.session.execute(
            select(func.count(KnowledgeDocumentModel.id)).where(
                KnowledgeDocumentModel.is_active.is_(True)
            )
        )
        return (total_res.scalar() or 0), (active_res.scalar() or 0)

    async def add(self, doc: KnowledgeDocumentModel) -> KnowledgeDocumentModel:
        self.session.add(doc)
        await self.session.flush()
        return doc

    async def delete(self, doc: KnowledgeDocumentModel) -> None:
        await self.session.delete(doc)
        await self.session.flush()
