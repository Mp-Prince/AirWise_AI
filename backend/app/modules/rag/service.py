"""RAG (Retrieval-Augmented Generation) service (Phase 4)."""
import time
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.embedding_provider import EMBEDDING_MODEL_NAME
from app.modules.document_chunks.schema import DocumentChunkWithScore, RetrievalRequest
from app.modules.document_chunks.service import DocumentChunkService
from app.modules.rag.repository import RAGRepository
from app.modules.rag.schema import RAGCitation, RAGRequest, RAGResponse


class RAGService:
    """Service for RAG operations: retrieval, prompt construction, and audit logging."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.chunk_service = DocumentChunkService(session)
        self.repo = RAGRepository(session)

    async def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.3,
        source_types: Optional[list[str]] = None,
        document_ids: Optional[list[UUID]] = None,
    ) -> list[DocumentChunkWithScore]:
        """Retrieve relevant document chunks for a query."""
        retrieval_request = RetrievalRequest(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            source_types=source_types,
            document_ids=document_ids,
        )
        result = await self.chunk_service.retrieve(retrieval_request)
        return result.results

    async def query_with_citations(
        self,
        request: RAGRequest,
        user_id: Optional[UUID] = None,
    ) -> RAGResponse:
        """Retrieve grounded passages with citations and record an audit entry."""
        start_time = time.time()
        chunks = await self.retrieve_context(
            query=request.query,
            top_k=request.top_k,
            source_types=request.source_types,
        )
        processing_time_ms = (time.time() - start_time) * 1000

        await self.repo.log_query(
            user_id=user_id,
            query=request.query,
            documents_retrieved=len(chunks),
            processing_time_ms=int(round(processing_time_ms)),
            model=EMBEDDING_MODEL_NAME,
            is_successful=True,
        )

        if not chunks:
            return RAGResponse(
                query=request.query,
                answer="I don't have reliable information in my knowledge base to answer that question yet.",
                citations=[],
                sources_used=0,
                total_available=0,
                processing_time_ms=processing_time_ms,
                is_grounded=False,
            )

        citations = [
            RAGCitation(
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                page_number=chunk.page_number,
                document_title=chunk.document_title,
                source_url=chunk.document_source_url,
                snippet=chunk.content[:320] + ("..." if len(chunk.content) > 320 else ""),
                confidence=chunk.similarity_score,
                source_type=chunk.document_source_type,
            )
            for chunk in chunks
        ]

        return RAGResponse(
            query=request.query,
            answer="",  # Phase 5 LLM synthesizes the final response from citations
            citations=citations if request.include_references else [],
            sources_used=len(chunks),
            total_available=len(chunks),
            processing_time_ms=processing_time_ms,
            is_grounded=True,
        )

    async def get_stats(self) -> dict:
        stats = await self.repo.get_stats()
        stats["embedding_model"] = EMBEDDING_MODEL_NAME
        return stats

    def format_retrieved_documents(
        self,
        chunks: list[DocumentChunkWithScore],
        max_chars_per_chunk: int = 2000,
    ) -> str:
        """Format retrieved chunks into a single context string for prompts."""
        if not chunks:
            return "No relevant documents found."

        formatted_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.document_title or "Unknown source"
            if chunk.document_source_type:
                source = f"[{chunk.document_source_type}] {source}"
            if chunk.page_number:
                source = f"{source} (p. {chunk.page_number})"

            content = chunk.content
            if len(content) > max_chars_per_chunk:
                content = content[:max_chars_per_chunk] + "..."

            formatted_parts.append(
                f"[{i}] Source: {source}\n"
                f"Confidence: {chunk.similarity_score:.2f}\n"
                f"Content: {content}\n"
                f"---"
            )

        return "\n\n".join(formatted_parts)

    def format_system_prompt(
        self,
        chunks: list[DocumentChunkWithScore],
        user: str,
    ) -> str:
        """Format a grounded system prompt with retrieved context."""
        context = self.format_retrieved_documents(chunks)

        return f"""You are AirWise AI, an expert environmental advisor. Provide grounded, evidence-based recommendations.

Retrieved relevant documents:
{context}

Guidelines:
- Always cite sources when making factual claims
- If a claim cannot be supported by the documents, say "I don't have reliable information about that"
- Present AQI values and recommendations clearly
- Consider user's location and environmental conditions

User: {user}
Assistant:"""
