from pathlib import Path

from pydantic import BaseModel, Field

from app.core.config import settings
from rag.chunking.semantic_chunker import Chunk, SemanticChunker
from rag.ingestion.docx_loader import DocxLoader
from rag.ingestion.pdf_loader import PdfLoader


class IngestionResult(BaseModel):
    chunks: list[Chunk]
    token_count: int
    metadata: dict = Field(default_factory=dict)


class IngestionPipeline:
    def __init__(self, chunker: SemanticChunker | None = None):
        self.chunker = chunker or SemanticChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

    async def ingest_file(self, path: Path) -> IngestionResult:
        text, metadata = await self._load_text(path)
        chunks = self.chunker.chunk(text, source=str(path), base_metadata=metadata)
        return IngestionResult(
            chunks=chunks,
            token_count=sum(chunk.token_count for chunk in chunks),
            metadata=metadata,
        )

    async def _load_text(self, path: Path) -> tuple[str, dict]:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return await PdfLoader().load(path)
        if suffix == ".docx":
            return await DocxLoader().load(path)
        raise ValueError(f"Unsupported document type: {suffix}")

