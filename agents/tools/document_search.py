from typing import Any
from uuid import UUID

from app.schemas.documents import DocumentSearchRequest
from rag.retrieval.hybrid_search import HybridSearchService
from rag.store.chroma import ChromaVectorStore


class DocumentSearchTool:
    name = "document_search"

    def __init__(self) -> None:
        self.search_service = HybridSearchService(ChromaVectorStore())

    async def search(
        self,
        user_id: UUID,
        query: str,
        document_ids: list[UUID] | None = None,
        limit: int = 5,
    ) -> list[dict]:
        request = DocumentSearchRequest(query=query, document_ids=document_ids, limit=limit)
        hits = await self.search_service.search(
            user_id=user_id,
            query=request.query,
            limit=request.limit,
            document_ids=request.document_ids,
        )
        return [hit.model_dump(mode="json") for hit in hits]

    async def ainvoke(self, kwargs: dict) -> Any:
        return await self.search(**kwargs)

