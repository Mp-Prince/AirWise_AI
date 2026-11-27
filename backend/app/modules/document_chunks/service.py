"""Document chunk service with semantic retrieval (Phase 4).

Supports both pgvector (when PostgreSQL extension is available) and
Python-based cosine similarity fallback for JSON-stored embeddings.
"""
import time
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.orm import selectinload

from app.modules.document_chunks.models import DocumentChunkModel
from app.modules.knowledge_documents.models import KnowledgeDocumentModel
from app.modules.document_chunks.schema import (
    DocumentChunkCreate,
    DocumentChunkResponse,
    DocumentChunkWithScore,
    RetrievalRequest,
    RetrievalResponse,
)

# Embedding dimension for all-MiniLM-L6-v2
EMBEDDING_DIM = 384


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


class DocumentChunkService:
    """Service for document chunk operations and semantic retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._pgvector_available: Optional[bool] = None

    async def _check_pgvector_available(self) -> bool:
        """Check if pgvector extension is available in PostgreSQL."""
        if self._pgvector_available is not None:
            return self._pgvector_available

        try:
            result = await self.session.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            )
            self._pgvector_available = result.scalar() is not None
        except Exception:
            self._pgvector_available = False

        return self._pgvector_available

    async def get_by_id(self, chunk_id: uuid.UUID) -> Optional[DocumentChunkModel]:
        """Get chunk by ID."""
        result = await self.session.execute(
            select(DocumentChunkModel).where(DocumentChunkModel.id == chunk_id)
        )
        return result.scalars().first()

    async def create(self, chunk_data: DocumentChunkCreate) -> DocumentChunkModel:
        """Create a document chunk."""
        chunk = DocumentChunkModel(**chunk_data.model_dump())
        self.session.add(chunk)
        await self.session.flush()
        return chunk

    async def get_chunks_for_document(self, document_id: uuid.UUID) -> list[DocumentChunkModel]:
        """Get all chunks for a document ordered by index."""
        result = await self.session.execute(
            select(DocumentChunkModel)
            .where(DocumentChunkModel.document_id == document_id)
            .order_by(DocumentChunkModel.chunk_index)
        )
        return result.scalars().all()

    async def delete_chunks_for_document(self, document_id: uuid.UUID) -> int:
        """Delete all chunks for a document."""
        from sqlalchemy import delete
        result = await self.session.execute(
            delete(DocumentChunkModel).where(DocumentChunkModel.document_id == document_id)
        )
        return result.rowcount

    async def semantic_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        similarity_threshold: float = 0.5,
        source_types: Optional[list[str]] = None,
        document_ids: Optional[list[uuid.UUID]] = None,
    ) -> list[DocumentChunkWithScore]:
        """Perform semantic search using pgvector (if available) or Python cosine similarity fallback."""
        pgvector_available = await self._check_pgvector_available()

        if pgvector_available:
            return await self._semantic_search_pgvector(
                query_embedding, top_k, similarity_threshold, source_types, document_ids
            )
        else:
            return await self._semantic_search_python(
                query_embedding, top_k, similarity_threshold, source_types, document_ids
            )

    async def _semantic_search_pgvector(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        similarity_threshold: float = 0.5,
        source_types: Optional[list[str]] = None,
        document_ids: Optional[list[uuid.UUID]] = None,
    ) -> list[DocumentChunkWithScore]:
        """Perform semantic search using pgvector cosine similarity."""
        # Convert embedding to pgvector format
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        # Base query with joins to get document metadata
        query = text("""
            SELECT
                dc.id,
                dc.document_id,
                dc.chunk_index,
                dc.content,
                dc.token_count,
                (1 - (dc.embedding <=> :embedding::vector)) as similarity_score,
                kd.title as document_title,
                kd.source_url as document_source_url,
                kd.source_type as document_source_type
            FROM document_chunks dc
            JOIN knowledge_documents kd ON dc.document_id = kd.id
            WHERE (1 - (dc.embedding <=> :embedding::vector)) >= :threshold
        """)

        params = {
            "embedding": embedding_str,
            "threshold": similarity_threshold,
        }

        # Add source type filter
        if source_types:
            placeholders = ",".join([f":source_type_{i}" for i in range(len(source_types))])
            query = text(str(query) + f" AND kd.source_type IN ({placeholders})")
            for i, st in enumerate(source_types):
                params[f"source_type_{i}"] = st

        # Add document ID filter
        if document_ids:
            placeholders = ",".join([f":doc_id_{i}" for i in range(len(document_ids))])
            query = text(str(query) + f" AND dc.document_id IN ({placeholders})")
            for i, did in enumerate(document_ids):
                params[f"doc_id_{i}"] = str(did)

        # Order by similarity (highest first) and limit
        query = text(str(query) + " ORDER BY similarity_score DESC LIMIT :top_k")
        params["top_k"] = top_k

        result = await self.session.execute(query, params)

        chunks = []
        for row in result.mappings():
            chunks.append(DocumentChunkWithScore(
                id=row["id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                content=row["content"],
                token_count=row["token_count"],
                similarity_score=row["similarity_score"],
                document_title=row["document_title"],
                document_source_url=row["document_source_url"],
                document_source_type=row["document_source_type"],
            ))

        return chunks

    async def _semantic_search_python(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        similarity_threshold: float = 0.5,
        source_types: Optional[list[str]] = None,
        document_ids: Optional[list[uuid.UUID]] = None,
    ) -> list[DocumentChunkWithScore]:
        """Perform semantic search using Python-based cosine similarity on JSON embeddings.

        Note: This loads all embeddings into memory. For production with large datasets,
        install pgvector extension when available.
        """
        # Build query to fetch chunks with embeddings and document metadata
        query = select(
            DocumentChunkModel.id,
            DocumentChunkModel.document_id,
            DocumentChunkModel.chunk_index,
            DocumentChunkModel.content,
            DocumentChunkModel.token_count,
            DocumentChunkModel.embedding,
            KnowledgeDocumentModel.title.label("document_title"),
            KnowledgeDocumentModel.source_url.label("document_source_url"),
            KnowledgeDocumentModel.source_type.label("document_source_type"),
        ).join(
            KnowledgeDocumentModel, DocumentChunkModel.document_id == KnowledgeDocumentModel.id
        ).where(
            DocumentChunkModel.embedding.is_not(None)
        )

        # Add source type filter
        if source_types:
            query = query.where(KnowledgeDocumentModel.source_type.in_(source_types))

        # Add document ID filter
        if document_ids:
            query = query.where(DocumentChunkModel.document_id.in_(document_ids))

        result = await self.session.execute(query)

        # Calculate similarity scores in Python
        scored_chunks = []
        for row in result.mappings():
            embedding = row["embedding"]
            if embedding:
                similarity = cosine_similarity(query_embedding, embedding)
                if similarity >= similarity_threshold:
                    scored_chunks.append((
                        similarity,
                        DocumentChunkWithScore(
                            id=row["id"],
                            document_id=row["document_id"],
                            chunk_index=row["chunk_index"],
                            content=row["content"],
                            token_count=row["token_count"],
                            similarity_score=similarity,
                            document_title=row["document_title"],
                            document_source_url=row["document_source_url"],
                            document_source_type=row["document_source_type"],
                        )
                    ))

        # Sort by similarity (highest first) and limit
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored_chunks[:top_k]]

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        """Main retrieval method: embed query and search."""
        start_time = time.time()

        # Generate query embedding
        query_embedding = await self._generate_embedding(request.query)

        # Perform semantic search
        results = await self.semantic_search(
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

    async def _generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for text using sentence-transformers."""
        try:
            from sentence_transformers import SentenceTransformer
            # Use a small, fast model for embeddings
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embedding = model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            # Return zero vector as fallback
            return [0.0] * EMBEDDING_DIM

    async def update_embeddings_for_document(self, document_id: uuid.UUID) -> int:
        """Regenerate embeddings for all chunks of a document."""
        chunks = await self.get_chunks_for_document(document_id)
        updated = 0

        for chunk in chunks:
            embedding = await self._generate_embedding(chunk.content)
            chunk.embedding = embedding
            updated += 1

        await self.session.flush()
        return updated