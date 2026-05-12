import hashlib
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AppError
from app.db.models import Document, DocumentChunk, DocumentStatus
from app.schemas.documents import DocumentIngestResponse, DocumentSearchRequest, DocumentSearchResponse
from rag.ingestion.pipeline import IngestionPipeline
from rag.retrieval.hybrid_search import HybridSearchService
from rag.store.chroma import ChromaVectorStore


class DocumentService:
    def __init__(self, session: AsyncSession | None = None):
        self.session = session

    async def ingest_upload(
        self,
        file: UploadFile,
        user_id: UUID,
        conversation_id: UUID | None,
    ) -> DocumentIngestResponse:
        if self.session is None:
            raise AppError("Database session is required for ingestion.")

        payload = await file.read()
        max_bytes = settings.max_upload_mb * 1024 * 1024
        if len(payload) > max_bytes:
            raise AppError(f"File exceeds {settings.max_upload_mb} MB limit.", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in {".pdf", ".docx"}:
            raise AppError("Only PDF and DOCX files are supported.")

        checksum = hashlib.sha256(payload).hexdigest()
        storage_path = self._persist_upload(payload, suffix)

        document = Document(
            user_id=user_id,
            conversation_id=conversation_id,
            filename=storage_path.name,
            original_filename=file.filename or storage_path.name,
            mime_type=file.content_type or "application/octet-stream",
            storage_url=str(storage_path),
            checksum=checksum,
            status=DocumentStatus.processing,
        )
        self.session.add(document)
        await self.session.flush()

        try:
            pipeline = IngestionPipeline()
            result = await pipeline.ingest_file(storage_path)
            vector_store = ChromaVectorStore()
            embedding_ids = await vector_store.add_chunks(
                user_id=user_id,
                document_id=document.id,
                chunks=result.chunks,
            )

            for index, chunk in enumerate(result.chunks):
                self.session.add(
                    DocumentChunk(
                        document_id=document.id,
                        chunk_index=index,
                        content=chunk.content,
                        token_count=chunk.token_count,
                        embedding_id=embedding_ids[index],
                        chunk_metadata=chunk.metadata,
                    )
                )

            document.status = DocumentStatus.indexed
            document.chunk_count = len(result.chunks)
            document.token_count = result.token_count
            document.document_metadata = result.metadata
            await self.session.commit()
        except Exception as exc:
            document.status = DocumentStatus.failed
            document.error_message = str(exc)
            await self.session.commit()
            raise

        return DocumentIngestResponse(
            document_id=document.id,
            status=document.status.value,
            chunk_count=document.chunk_count,
            token_count=document.token_count,
        )

    async def search(self, user_id: UUID, request: DocumentSearchRequest) -> DocumentSearchResponse:
        search_service = HybridSearchService(ChromaVectorStore())
        hits = await search_service.search(
            user_id=user_id,
            query=request.query,
            limit=request.limit,
            document_ids=request.document_ids,
        )
        return DocumentSearchResponse(query=request.query, hits=hits)

    def _persist_upload(self, payload: bytes, suffix: str) -> Path:
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        path = upload_dir / f"{uuid4()}{suffix}"
        path.write_bytes(payload)
        return path

