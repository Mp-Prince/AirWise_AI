"""RAG-related models (Phase 4).

Note: Core document and chunk models are in:
- app/modules/knowledge_documents/models.py (KnowledgeDocumentModel)
- app/modules/document_chunks/models.py (DocumentChunkModel)

This file contains additional RAG-specific tables.
"""
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class KnowledgeAuditLogModel(Base):
    """Audit log for RAG retrieval operations."""

    __tablename__ = "knowledge_audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    user_id: Mapped[datetime] = mapped_column(String(36), nullable=True, index=True)  # User UUID as string
    query: Mapped[str] = mapped_column(String(2000), nullable=False)
    documents_retrieved: Mapped[int] = mapped_column(Integer, nullable=False)
    processing_time_ms: Mapped[float] = mapped_column(Integer, nullable=False)
    model: Mapped[str] = mapped_column(String(100), default="sentence-transformers/all-MiniLM-L6-v2", nullable=False)
    is_successful: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )