"""Document chunk schemas (Phase 4)."""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class DocumentChunkBase(BaseModel):
    """Base document chunk schema."""
    document_id: UUID = Field(..., description="Parent document ID")
    chunk_index: int = Field(..., ge=0, description="Chunk sequence index")
    content: str = Field(..., min_length=1, description="Chunk text content")
    token_count: Optional[int] = Field(None, ge=0, description="Approximate token count")


class DocumentChunkCreate(DocumentChunkBase):
    """Schema for creating a document chunk."""
    embedding: Optional[list[float]] = Field(None, description="Vector embedding")


class DocumentChunkResponse(DocumentChunkBase):
    """Schema for document chunk response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: str
    # Embedding not included in standard response (large)


class DocumentChunkWithScore(BaseModel):
    """Document chunk with similarity score for retrieval."""
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    token_count: Optional[int]
    similarity_score: float
    document_title: Optional[str] = None
    document_source_url: Optional[str] = None
    document_source_type: Optional[str] = None


class RetrievalRequest(BaseModel):
    """Request schema for semantic retrieval."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")
    similarity_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Minimum similarity score")
    source_types: Optional[list[str]] = Field(None, description="Filter by source types")
    document_ids: Optional[list[UUID]] = Field(None, description="Filter by specific documents")


class RetrievalResponse(BaseModel):
    """Response schema for semantic retrieval."""
    query: str
    results: list[DocumentChunkWithScore]
    total_searched: int
    retrieval_time_ms: float