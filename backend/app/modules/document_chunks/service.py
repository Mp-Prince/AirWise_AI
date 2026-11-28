"""Document chunk service with semantic retrieval (Phase 4)."""
import time
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.embedding_provider import (
    EMBEDDING_DIM,
    generate_embedding,
    generate_embeddings_batch,
)
from app.modules.document_chunks.models import DocumentChunkModel
from app.modules.document_chunks.repository import DocumentChunkRepository
from app.modules.document_chunks.schema import (
    DocumentChunkCreate,
    DocumentChunkWithScore,
    RetrievalRequest,
    RetrievalResponse,
)


class DocumentChunkService:
    """Business logic for document chunk operations and semantic retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = DocumentChunkRepository(session)

    async def get_by_id(self, chunk_id: uuid.UUID) -> Optional[DocumentChunkModel]:
        return await self.repo.get_by_id(chunk_id)

    async def create(self, chunk_data: DocumentChunkCreate) -> DocumentChunkModel:
        return await self.repo.create(chunk_data)

    async def get_chunks_for_document(self, document_id: uuid.UUID) -> list[DocumentChunkModel]:
        return await self.repo.get_by_document(document_id)

    async def delete_chunks_for_document(self, document_id: uuid.UUID) -> int:
        return await self.repo.delete_by_document(document_id)

    async def semantic_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        similarity_threshold: float = 0.5,
        source_types: Optional[list[str]] = None,
        document_ids: Optional[list[uuid.UUID]] = None,
    ) -> list[DocumentChunkWithScore]:
        return await self.repo.semantic_search(
            query_embedding=query_embedding,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            source_types=source_types,
            document_ids=document_ids,
        )

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        """Embed query and perform semantic retrieval."""
        start_time = time.time()
        total_chunks = await self.repo.count_all()
        if total_chunks == 0:
            return RetrievalResponse(
                query=request.query,
                results=[],
                total_searched=0,
                retrieval_time_ms=(time.time() - start_time) * 1000,
            )

        query_embedding = await generate_embedding(request.query)
        results = await self.repo.semantic_search(
            query_embedding=query_embedding,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            source_types=request.source_types,
            document_ids=request.document_ids,
        )
        retrieval_time_ms = (time.time() - start_time) * 1000

        return RetrievalResponse(
            query=request.query,
            results=results,
            total_searched=len(results),
            retrieval_time_ms=retrieval_time_ms,
        )

    async def update_embeddings_for_document(self, document_id: uuid.UUID) -> int:
        """Regenerate embeddings for all chunks of a document."""
        chunks = await self.repo.get_by_document(document_id)
        if not chunks:
            return 0
        embeddings = await generate_embeddings_batch([chunk.content for chunk in chunks])
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
        await self.session.flush()
        return len(chunks)
