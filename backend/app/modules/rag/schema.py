"""RAG schemas (Phase 4)."""
from typing import Optional, Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RAGRequest(BaseModel):
    """Request schema for RAG-powered query."""

    query: str = Field(..., min_length=1, max_length=2000, description="User's question or prompt")
    top_k: int = Field(5, ge=1, le=10, description="Number of documents to retrieve")
    include_references: bool = Field(True, description="Include source references in response")
    source_types: Optional[list[str]] = Field(None, description="Filter by document source types")


class RAGCitation(BaseModel):
    """Citation for a retrieved document."""

    document_id: UUID
    chunk_index: int
    page_number: Optional[int] = None
    document_title: Optional[str] = None
    source_url: Optional[str] = None
    snippet: Optional[str] = None
    confidence: float
    source_type: Optional[str] = None


class RAGResponse(BaseModel):
    """Response schema for RAG-powered query."""

    model_config = ConfigDict(from_attributes=True)

    query: str
    answer: str
    citations: list[RAGCitation]
    sources_used: int
    total_available: int
    processing_time_ms: float
    is_grounded: bool  # True if response is based on retrieved documents


class DocumentSource(BaseModel):
    """Source document with chunks for admin use."""

    id: UUID
    title: str
    source_type: str
    is_active: bool
    chunk_count: int
    created_at: str


class KnowledgeAudit(BaseModel):
    """Audit log for knowledge base usage."""

    timestamp: str
    user_id: Optional[UUID]
    query: str
    documents_retrieved: int
    processing_time_ms: float
    model: str = "sentence-transformers/all-MiniLM-L6-v2"