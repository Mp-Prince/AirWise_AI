"""Knowledge document service (Phase 4)."""
import hashlib
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from app.modules.knowledge_documents.models import KnowledgeDocumentModel
from app.modules.document_chunks.models import DocumentChunkModel
from app.modules.knowledge_documents.schema import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
    KnowledgeDocumentResponse,
    KnowledgeDocumentListResponse,
    DocumentIngestRequest,
    DocumentIngestResponse,
)

# Chunking configuration
CHUNK_SIZE = 512  # tokens (approximate)
CHUNK_OVERLAP = 50  # tokens


class KnowledgeDocumentService:
    """Service for knowledge document operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, doc_id: uuid.UUID) -> Optional[KnowledgeDocumentModel]:
        """Get document by ID with chunk count."""
        result = await self.session.execute(
            select(KnowledgeDocumentModel)
            .where(KnowledgeDocumentModel.id == doc_id)
            .options(selectinload(KnowledgeDocumentModel.chunks))
        )
        return result.scalars().first()

    async def get_by_content_hash(self, content_hash: str) -> Optional[KnowledgeDocumentModel]:
        """Get document by content hash."""
        result = await self.session.execute(
            select(KnowledgeDocumentModel).where(KnowledgeDocumentModel.content_hash == content_hash)
        )
        return result.scalars().first()

    async def list_documents(
        self,
        page: int = 1,
        page_size: int = 20,
        source_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> KnowledgeDocumentListResponse:
        """List documents with pagination and filters."""
        query = select(KnowledgeDocumentModel)
        count_query = select(func.count(KnowledgeDocumentModel.id))

        if source_type:
            query = query.where(KnowledgeDocumentModel.source_type == source_type)
            count_query = count_query.where(KnowledgeDocumentModel.source_type == source_type)

        if is_active is not None:
            query = query.where(KnowledgeDocumentModel.is_active == is_active)
            count_query = count_query.where(KnowledgeDocumentModel.is_active == is_active)

        query = query.order_by(KnowledgeDocumentModel.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(query)
        documents = result.scalars().all()

        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Get chunk counts for each document
        doc_responses = []
        for doc in documents:
            chunk_count_result = await self.session.execute(
                select(func.count(DocumentChunkModel.id)).where(DocumentChunkModel.document_id == doc.id)
            )
            chunk_count = chunk_count_result.scalar() or 0

            doc_responses.append(KnowledgeDocumentResponse(
                id=doc.id,
                title=doc.title,
                source_url=doc.source_url,
                source_type=doc.source_type,
                content_hash=doc.content_hash,
                full_text=doc.full_text,
                metadata_json=doc.metadata_json,
                created_at=doc.created_at.isoformat() if doc.created_at else "",
                updated_at=doc.updated_at.isoformat() if doc.updated_at else "",
                is_active=getattr(doc, 'is_active', True),
                chunk_count=chunk_count,
            ))

        return KnowledgeDocumentListResponse(
            documents=doc_responses,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def create(self, doc_data: KnowledgeDocumentCreate) -> KnowledgeDocumentModel:
        """Create a new knowledge document."""
        content_hash = hashlib.sha256(doc_data.content.encode()).hexdigest()

        # Check for duplicate
        existing = await self.get_by_content_hash(content_hash)
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
        self.session.add(doc)
        await self.session.flush()
        return doc

    async def update(self, doc_id: uuid.UUID, doc_data: KnowledgeDocumentUpdate) -> Optional[KnowledgeDocumentModel]:
        """Update a knowledge document."""
        doc = await self.get_by_id(doc_id)
        if not doc:
            return None

        update_data = doc_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)

        await self.session.flush()
        return doc

    async def delete(self, doc_id: uuid.UUID) -> bool:
        """Delete a knowledge document and its chunks."""
        doc = await self.get_by_id(doc_id)
        if not doc:
            return False

        # Delete chunks first (cascade should handle this, but explicit is safer)
        await self.session.execute(
            delete(DocumentChunkModel).where(DocumentChunkModel.document_id == doc_id)
        )
        await self.session.delete(doc)
        await self.session.flush()
        return True

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        if len(words) <= CHUNK_SIZE:
            return [text]

        chunks = []
        start = 0
        while start < len(words):
            end = min(start + CHUNK_SIZE, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            if end >= len(words):
                break
            start = end - CHUNK_OVERLAP

        return chunks

    async def ingest_document(self, request: DocumentIngestRequest) -> DocumentIngestResponse:
        """Ingest a document: extract text, chunk, generate embeddings, store."""
        content = request.content

        # Extract text from different sources
        if request.file_content:
            # Base64 encoded PDF
            import base64
            pdf_bytes = base64.b64decode(request.file_content)
            content = self._extract_pdf_text(pdf_bytes)
        elif request.source_url and request.source_type == "web":
            content = await self._fetch_web_content(request.source_url)
        elif not content:
            return DocumentIngestResponse(
                document_id=uuid.uuid4(),
                title=request.title,
                chunks_created=0,
                status="error",
                message="No content provided",
            )

        # Create document
        doc_data = KnowledgeDocumentCreate(
            title=request.title,
            source_url=request.source_url,
            source_type=request.source_type,
            content=content,
            metadata_json=request.metadata_json,
        )
        doc = await self.create(doc_data)

        # Chunk the content
        chunks = self._chunk_text(content)

        # Generate embeddings and store chunks
        chunks_created = 0
        for i, chunk_text in enumerate(chunks):
            embedding = await self._generate_embedding(chunk_text)

            chunk = DocumentChunkModel(
                document_id=doc.id,
                chunk_index=i,
                content=chunk_text,
                embedding=embedding,
                token_count=len(chunk_text.split()),
            )
            self.session.add(chunk)
            chunks_created += 1

        await self.session.flush()

        return DocumentIngestResponse(
            document_id=doc.id,
            title=doc.title,
            chunks_created=chunks_created,
            status="success",
            message=f"Document ingested with {chunks_created} chunks",
        )

    def _extract_pdf_text(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes."""
        try:
            import pypdf
            import io
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n\n".join(text_parts)
        except Exception as e:
            raise ValueError(f"Failed to extract PDF text: {str(e)}")

    async def _fetch_web_content(self, url: str) -> str:
        """Fetch and extract text from web URL."""
        try:
            import httpx
            from bs4 import BeautifulSoup

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text
            text = soup.get_text(separator='\n', strip=True)
            return text
        except Exception as e:
            raise ValueError(f"Failed to fetch web content: {str(e)}")

    async def _generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for text using sentence-transformers."""
        try:
            from sentence_transformers import SentenceTransformer
            # Use a small, fast model for embeddings
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embedding = model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            # Return zero vector as fallback (should not happen in production)
            return [0.0] * 384  # all-MiniLM-L6-v2 dimension


class DocumentChunkService:
    """Service for document chunk operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_chunks_for_document(self, document_id: uuid.UUID) -> list[DocumentChunkModel]:
        """Get all chunks for a document."""
        result = await self.session.execute(
            select(DocumentChunkModel)
            .where(DocumentChunkModel.document_id == document_id)
            .order_by(DocumentChunkModel.chunk_index)
        )
        return result.scalars().all()

    async def delete_chunks_for_document(self, document_id: uuid.UUID) -> int:
        """Delete all chunks for a document."""
        result = await self.session.execute(
            delete(DocumentChunkModel).where(DocumentChunkModel.document_id == document_id)
        )
        return result.rowcount