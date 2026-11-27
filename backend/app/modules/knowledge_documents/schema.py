"""Knowledge document schemas (Phase 4)."""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class KnowledgeDocumentBase(BaseModel):
    """Base knowledge document schema."""
    title: str = Field(..., min_length=1, max_length=500, description="Document title")
    source_url: Optional[str] = Field(None, max_length=1000, description="Source URL if web document")
    source_type: str = Field(..., min_length=1, max_length=50, description="Source type: pdf, web, manual")
    metadata_json: dict = Field(default_factory=dict, description="Additional metadata (author, date, etc.)")


class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    """Schema for creating a knowledge document."""
    content: str = Field(..., min_length=1, description="Full text content of the document")


class KnowledgeDocumentUpdate(BaseModel):
    """Schema for updating a knowledge document."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    source_url: Optional[str] = Field(None, max_length=1000)
    source_type: Optional[str] = Field(None, min_length=1, max_length=50)
    metadata_json: Optional[dict] = None
    is_active: Optional[bool] = None


class KnowledgeDocumentResponse(KnowledgeDocumentBase):
    """Schema for knowledge document response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content_hash: str
    full_text: Optional[str] = None
    created_at: str
    updated_at: str
    is_active: bool = True
    chunk_count: int = 0


class KnowledgeDocumentListResponse(BaseModel):
    """Schema for paginated knowledge document list."""
    documents: list[KnowledgeDocumentResponse]
    total: int
    page: int
    page_size: int


class DocumentIngestRequest(BaseModel):
    """Request schema for document ingestion."""
    title: str = Field(..., min_length=1, max_length=500)
    source_url: Optional[str] = Field(None, max_length=1000)
    source_type: str = Field(..., pattern="^(pdf|web|manual)$")
    content: Optional[str] = None  # For manual entry
    file_content: Optional[str] = None  # Base64 encoded file for PDF upload
    metadata_json: dict = Field(default_factory=dict)


class DocumentIngestResponse(BaseModel):
    """Response schema for document ingestion."""
    document_id: UUID
    title: str
    chunks_created: int
    status: str
    message: Optional[str] = None