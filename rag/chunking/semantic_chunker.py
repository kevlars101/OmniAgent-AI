import re

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    content: str
    token_count: int
    metadata: dict = Field(default_factory=dict)


class SemanticChunker:
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 180):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str, source: str, base_metadata: dict | None = None) -> list[Chunk]:
        cleaned = self._normalize(text)
        if not cleaned:
            return []

        paragraphs = [paragraph for paragraph in cleaned.split("\n\n") if paragraph.strip()]
        chunks: list[Chunk] = []
        current: list[str] = []
        current_tokens = 0

        for paragraph in paragraphs:
            paragraph_tokens = self._estimate_tokens(paragraph)
            if current and current_tokens + paragraph_tokens > self.chunk_size:
                chunks.append(self._build_chunk(current, source, len(chunks), base_metadata))
                current = self._overlap_tail(current)
                current_tokens = sum(self._estimate_tokens(item) for item in current)
            current.append(paragraph)
            current_tokens += paragraph_tokens

        if current:
            chunks.append(self._build_chunk(current, source, len(chunks), base_metadata))

        return chunks

    def _build_chunk(
        self,
        paragraphs: list[str],
        source: str,
        index: int,
        base_metadata: dict | None,
    ) -> Chunk:
        content = "\n\n".join(paragraphs).strip()
        metadata = dict(base_metadata or {})
        metadata.update({"source": source, "chunk_index": index})
        return Chunk(content=content, token_count=self._estimate_tokens(content), metadata=metadata)

    def _overlap_tail(self, paragraphs: list[str]) -> list[str]:
        tail: list[str] = []
        token_total = 0
        for paragraph in reversed(paragraphs):
            paragraph_tokens = self._estimate_tokens(paragraph)
            if tail and token_total + paragraph_tokens > self.chunk_overlap:
                break
            tail.insert(0, paragraph)
            token_total += paragraph_tokens
        return tail

    def _normalize(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text.split()))

