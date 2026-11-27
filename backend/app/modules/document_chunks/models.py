"""Document chunk entity model with pgvector embedding."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, Index, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

# pgvector extension not yet installed in PostgreSQL - using JSON for now
# When pgvector is available, change embedding column to Vector(384)
# and enable the pgvector similarity search in service.py


class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(JSON, nullable=True)  # pgvector when available
    token_count: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationship back to document
    document: Mapped["KnowledgeDocumentModel"] = relationship("KnowledgeDocumentModel", back_populates="chunks")

    __table_args__ = (
        Index("ix_document_chunks_document", "document_id", "chunk_index"),
    )