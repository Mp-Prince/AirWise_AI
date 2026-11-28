"""Knowledge document service (Phase 4)."""
import base64
import hashlib
import io
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.embedding_provider import generate_embeddings_batch
from app.modules.document_chunks.models import DocumentChunkModel
from app.modules.document_chunks.repository import DocumentChunkRepository
from app.modules.knowledge_documents.models import KnowledgeDocumentModel
from app.modules.knowledge_documents.repository import KnowledgeDocumentRepository
from app.modules.knowledge_documents.schema import (
    DocumentIngestRequest,
    DocumentIngestResponse,
    KnowledgeDocumentCreate,
    KnowledgeDocumentListResponse,
    KnowledgeDocumentResponse,
    KnowledgeDocumentUpdate,
)

# Chunking configuration (approximate word tokens)
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50


class KnowledgeDocumentService:
    """Business logic for knowledge document management and ingestion."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = KnowledgeDocumentRepository(session)
        self.chunk_repo = DocumentChunkRepository(session)

    def _to_response(self, doc: KnowledgeDocumentModel, chunk_count: int) -> KnowledgeDocumentResponse:
        return KnowledgeDocumentResponse(
            id=doc.id,
            title=doc.title,
            source_url=doc.source_url,
            source_type=doc.source_type,
            content_hash=doc.content_hash,
            full_text=doc.full_text,
            metadata_json=doc.metadata_json,
            created_at=doc.created_at.isoformat() if doc.created_at else "",
            updated_at=doc.updated_at.isoformat() if doc.updated_at else "",
            is_active=getattr(doc, "is_active", True),
            chunk_count=chunk_count,
        )

    async def get_by_id(self, doc_id: uuid.UUID) -> Optional[KnowledgeDocumentModel]:
        return await self.repo.get_by_id(doc_id)

    async def get_response_by_id(self, doc_id: uuid.UUID) -> Optional[KnowledgeDocumentResponse]:
        doc = await self.repo.get_by_id(doc_id)
        if not doc:
            return None
        chunk_count = await self.chunk_repo.count_by_document(doc.id)
        return self._to_response(doc, chunk_count)

    async def list_documents(
        self,
        page: int = 1,
        page_size: int = 20,
        source_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> KnowledgeDocumentListResponse:
        documents, total = await self.repo.list_paginated(
            page=page,
            page_size=page_size,
            source_type=source_type,
            is_active=is_active,
        )
        counts = await self.repo.get_chunk_counts([doc.id for doc in documents])
        doc_responses = [self._to_response(doc, counts.get(doc.id, 0)) for doc in documents]
        return KnowledgeDocumentListResponse(
            documents=doc_responses,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def create(self, doc_data: KnowledgeDocumentCreate) -> KnowledgeDocumentModel:
        content_hash = hashlib.sha256(doc_data.content.encode("utf-8")).hexdigest()
        existing = await self.repo.get_by_content_hash(content_hash)
        if existing:
            return existing

        doc = KnowledgeDocumentModel(
            title=doc_data.title,
            source_url=doc_data.source_url,
            source_type=doc_data.source_type,
            content_hash=content_hash,
            full_text=doc_data.content,
            metadata_json=doc_data.metadata_json,
        )
        return await self.repo.add(doc)

    async def update(
        self, doc_id: uuid.UUID, doc_data: KnowledgeDocumentUpdate
    ) -> Optional[KnowledgeDocumentResponse]:
        doc = await self.repo.get_by_id(doc_id)
        if not doc:
            return None

        update_data = doc_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)

        await self.session.flush()
        chunk_count = await self.chunk_repo.count_by_document(doc.id)
        return self._to_response(doc, chunk_count)

    async def delete(self, doc_id: uuid.UUID) -> bool:
        doc = await self.repo.get_by_id(doc_id)
        if not doc:
            return False
        await self.chunk_repo.delete_by_document(doc_id)
        await self.repo.delete(doc)
        return True

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping word chunks."""
        words = text.split()
        if not words:
            return []
        if len(words) <= CHUNK_SIZE:
            return [" ".join(words)]

        chunks = []
        start = 0
        while start < len(words):
            end = min(start + CHUNK_SIZE, len(words))
            chunks.append(" ".join(words[start:end]))
            if end >= len(words):
                break
            start = end - CHUNK_OVERLAP
        return chunks

    def _chunk_pages(self, pages: list[tuple[Optional[int], str]]) -> list[tuple[Optional[int], str]]:
        """Chunk extracted text while preserving source page number metadata."""
        chunked: list[tuple[Optional[int], str]] = []
        for page_num, page_text in pages:
            for chunk_text in self._chunk_text(page_text):
                chunked.append((page_num, chunk_text))
        return chunked

    async def ingest_document(self, request: DocumentIngestRequest) -> DocumentIngestResponse:
        """Ingest a document: extract text, chunk with page metadata, embed, and store."""
        pages: list[tuple[Optional[int], str]] = []

        if request.file_content:
            pdf_bytes = base64.b64decode(request.file_content)
            pages = self._extract_pdf_pages(pdf_bytes)
            content = "\n\n".join(text for _, text in pages)
        elif request.source_url and request.source_type == "web":
            content = await self._fetch_web_content(request.source_url)
            pages = [(None, content)]
        elif request.content:
            content = request.content
            pages = [(None, content)]
        else:
            return DocumentIngestResponse(
                document_id=uuid.uuid4(),
                title=request.title,
                chunks_created=0,
                status="error",
                message="No content provided",
            )

        if not content.strip():
            return DocumentIngestResponse(
                document_id=uuid.uuid4(),
                title=request.title,
                chunks_created=0,
                status="error",
                message="Extracted document content is empty",
            )

        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        existing = await self.repo.get_by_content_hash(content_hash)
        if existing:
            existing_chunks = await self.chunk_repo.count_by_document(existing.id)
            if existing_chunks > 0:
                return DocumentIngestResponse(
                    document_id=existing.id,
                    title=existing.title,
                    chunks_created=0,
                    status="duplicate",
                    message=f"Document already ingested ({existing_chunks} chunks exist)",
                )
            doc = existing
        else:
            doc = await self.create(
                KnowledgeDocumentCreate(
                    title=request.title,
                    source_url=request.source_url,
                    source_type=request.source_type,
                    content=content,
                    metadata_json=request.metadata_json,
                )
            )

        chunk_items = self._chunk_pages(pages)
        embeddings = await generate_embeddings_batch([text for _, text in chunk_items])

        chunk_models = [
            DocumentChunkModel(
                document_id=doc.id,
                chunk_index=i,
                page_number=page_num,
                content=chunk_text,
                embedding=embedding,
                token_count=len(chunk_text.split()),
            )
            for i, ((page_num, chunk_text), embedding) in enumerate(zip(chunk_items, embeddings))
        ]
        await self.chunk_repo.add_many(chunk_models)

        return DocumentIngestResponse(
            document_id=doc.id,
            title=doc.title,
            chunks_created=len(chunk_models),
            status="success",
            message=f"Document ingested with {len(chunk_models)} chunks",
        )

    def _extract_pdf_pages(self, pdf_bytes: bytes) -> list[tuple[int, str]]:
        """Extract text from PDF bytes page-by-page, preserving 1-based page numbers."""
        try:
            import pypdf

            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            pages: list[tuple[int, str]] = []
            for idx, page in enumerate(reader.pages, start=1):
                text = (page.extract_text() or "").strip()
                if text:
                    pages.append((idx, text))
            return pages
        except Exception as exc:
            raise ValueError(f"Failed to extract PDF text: {exc}") from exc

    async def _fetch_web_content(self, url: str) -> str:
        """Fetch and extract readable text from a web URL."""
        try:
            import httpx
            from bs4 import BeautifulSoup

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            return soup.get_text(separator="\n", strip=True)
        except Exception as exc:
            raise ValueError(f"Failed to fetch web content: {exc}") from exc
