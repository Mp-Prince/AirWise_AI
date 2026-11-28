"""Document chunk repository for database access (Phase 4)."""
import uuid
from typing import Optional

from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.document_chunks.models import DocumentChunkModel
from app.modules.document_chunks.schema import DocumentChunkCreate, DocumentChunkWithScore
from app.modules.knowledge_documents.models import KnowledgeDocumentModel


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class DocumentChunkRepository:
    """Database access layer for document chunks and vector/cosine similarity search."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._pgvector_ready: Optional[bool] = None

    async def is_pgvector_ready(self) -> bool:
        """Check that pgvector extension is installed AND embedding column uses vector type."""
        if self._pgvector_ready is not None:
            return self._pgvector_ready

        try:
            ext_res = await self.session.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            )
            col_res = await self.session.execute(
                text(
                    "SELECT udt_name FROM information_schema.columns "
                    "WHERE table_name = 'document_chunks' AND column_name = 'embedding'"
                )
            )
            self._pgvector_ready = (
                ext_res.scalar() is not None and col_res.scalar() == "vector"
            )
        except Exception:
            self._pgvector_ready = False

        return self._pgvector_ready

    async def get_by_id(self, chunk_id: uuid.UUID) -> Optional[DocumentChunkModel]:
        result = await self.session.execute(
            select(DocumentChunkModel).where(DocumentChunkModel.id == chunk_id)
        )
        return result.scalars().first()

    async def create(self, chunk_data: DocumentChunkCreate) -> DocumentChunkModel:
        chunk = DocumentChunkModel(**chunk_data.model_dump())
        self.session.add(chunk)
        await self.session.flush()
        return chunk

    async def add_many(self, chunks: list[DocumentChunkModel]) -> None:
        self.session.add_all(chunks)
        await self.session.flush()

    async def get_by_document(self, document_id: uuid.UUID) -> list[DocumentChunkModel]:
        result = await self.session.execute(
            select(DocumentChunkModel)
            .where(DocumentChunkModel.document_id == document_id)
            .order_by(DocumentChunkModel.chunk_index)
        )
        return list(result.scalars().all())

    async def count_all(self) -> int:
        result = await self.session.execute(select(func.count(DocumentChunkModel.id)))
        return result.scalar() or 0

    async def count_by_document(self, document_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count(DocumentChunkModel.id)).where(
                DocumentChunkModel.document_id == document_id
            )
        )
        return result.scalar() or 0

    async def delete_by_document(self, document_id: uuid.UUID) -> int:
        result = await self.session.execute(
            delete(DocumentChunkModel).where(DocumentChunkModel.document_id == document_id)
        )
        return result.rowcount or 0

    async def semantic_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        similarity_threshold: float = 0.5,
        source_types: Optional[list[str]] = None,
        document_ids: Optional[list[uuid.UUID]] = None,
    ) -> list[DocumentChunkWithScore]:
        """Search active documents using pgvector if ready, else Python cosine similarity."""
        if await self.is_pgvector_ready():
            return await self._semantic_search_pgvector(
                query_embedding, top_k, similarity_threshold, source_types, document_ids
            )
        return await self._semantic_search_python(
            query_embedding, top_k, similarity_threshold, source_types, document_ids
        )

    async def _semantic_search_pgvector(
        self,
        query_embedding: list[float],
        top_k: int,
        similarity_threshold: float,
        source_types: Optional[list[str]],
        document_ids: Optional[list[uuid.UUID]],
    ) -> list[DocumentChunkWithScore]:
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        sql = """
            SELECT
                dc.id,
                dc.document_id,
                dc.chunk_index,
                dc.page_number,
                dc.content,
                dc.token_count,
                (1 - (dc.embedding <=> :embedding::vector)) AS similarity_score,
                kd.title AS document_title,
                kd.source_url AS document_source_url,
                kd.source_type AS document_source_type
            FROM document_chunks dc
            JOIN knowledge_documents kd ON dc.document_id = kd.id
            WHERE kd.is_active = TRUE
              AND (1 - (dc.embedding <=> :embedding::vector)) >= :threshold
        """
        params: dict = {"embedding": embedding_str, "threshold": similarity_threshold}

        if source_types:
            placeholders = ",".join(f":source_type_{i}" for i in range(len(source_types)))
            sql += f" AND kd.source_type IN ({placeholders})"
            for i, st in enumerate(source_types):
                params[f"source_type_{i}"] = st

        if document_ids:
            placeholders = ",".join(f":doc_id_{i}" for i in range(len(document_ids)))
            sql += f" AND dc.document_id IN ({placeholders})"
            for i, did in enumerate(document_ids):
                params[f"doc_id_{i}"] = str(did)

        sql += " ORDER BY similarity_score DESC LIMIT :top_k"
        params["top_k"] = top_k

        result = await self.session.execute(text(sql), params)
        return [
            DocumentChunkWithScore(
                id=row["id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                page_number=row["page_number"],
                content=row["content"],
                token_count=row["token_count"],
                similarity_score=row["similarity_score"],
                document_title=row["document_title"],
                document_source_url=row["document_source_url"],
                document_source_type=row["document_source_type"],
            )
            for row in result.mappings()
        ]

    async def _semantic_search_python(
        self,
        query_embedding: list[float],
        top_k: int,
        similarity_threshold: float,
        source_types: Optional[list[str]],
        document_ids: Optional[list[uuid.UUID]],
    ) -> list[DocumentChunkWithScore]:
        query = (
            select(
                DocumentChunkModel.id,
                DocumentChunkModel.document_id,
                DocumentChunkModel.chunk_index,
                DocumentChunkModel.page_number,
                DocumentChunkModel.content,
                DocumentChunkModel.token_count,
                DocumentChunkModel.embedding,
                KnowledgeDocumentModel.title.label("document_title"),
                KnowledgeDocumentModel.source_url.label("document_source_url"),
                KnowledgeDocumentModel.source_type.label("document_source_type"),
            )
            .join(
                KnowledgeDocumentModel,
                DocumentChunkModel.document_id == KnowledgeDocumentModel.id,
            )
            .where(
                DocumentChunkModel.embedding.is_not(None),
                KnowledgeDocumentModel.is_active.is_(True),
            )
        )

        if source_types:
            query = query.where(KnowledgeDocumentModel.source_type.in_(source_types))
        if document_ids:
            query = query.where(DocumentChunkModel.document_id.in_(document_ids))

        result = await self.session.execute(query)

        scored_chunks: list[tuple[float, DocumentChunkWithScore]] = []
        for row in result.mappings():
            embedding = row["embedding"]
            if not embedding:
                continue
            similarity = cosine_similarity(query_embedding, embedding)
            if similarity >= similarity_threshold:
                scored_chunks.append(
                    (
                        similarity,
                        DocumentChunkWithScore(
                            id=row["id"],
                            document_id=row["document_id"],
                            chunk_index=row["chunk_index"],
                            page_number=row["page_number"],
                            content=row["content"],
                            token_count=row["token_count"],
                            similarity_score=similarity,
                            document_title=row["document_title"],
                            document_source_url=row["document_source_url"],
                            document_source_type=row["document_source_type"],
                        ),
                    )
                )

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored_chunks[:top_k]]
