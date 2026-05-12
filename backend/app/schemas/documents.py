from uuid import UUID

from pydantic import BaseModel, Field


class DocumentIngestResponse(BaseModel):
    document_id: UUID
    status: str
    chunk_count: int
    token_count: int


class DocumentSearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    limit: int = Field(default=8, ge=1, le=30)
    document_ids: list[UUID] | None = None


class DocumentSearchHit(BaseModel):
    document_id: UUID
    chunk_id: UUID | None = None
    content: str
    score: float
    metadata: dict = Field(default_factory=dict)


class DocumentSearchResponse(BaseModel):
    query: str
    hits: list[DocumentSearchHit]

