from uuid import UUID

from app.schemas.documents import DocumentSearchHit
from rag.store.chroma import ChromaVectorStore


class HybridSearchService:
    def __init__(self, vector_store: ChromaVectorStore):
        self.vector_store = vector_store

    async def search(
        self,
        user_id: UUID,
        query: str,
        limit: int,
        document_ids: list[UUID] | None = None,
    ) -> list[DocumentSearchHit]:
        vector_hits = await self.vector_store.query(
            user_id=user_id,
            query=query,
            limit=limit,
            document_ids=document_ids,
        )

        # Phase 2 hybrid baseline: semantic retrieval with lexical score boosting.
        # A Postgres tsvector branch can be added when message/document search tables are expanded.
        query_terms = {term.lower() for term in query.split() if len(term) > 2}
        ranked = []
        for hit in vector_hits:
            content_terms = hit["content"].lower()
            lexical_matches = sum(1 for term in query_terms if term in content_terms)
            lexical_boost = min(0.15, lexical_matches * 0.03)
            hit["score"] = min(1.0, hit["score"] + lexical_boost)
            ranked.append(hit)

        ranked.sort(key=lambda item: item["score"], reverse=True)
        return [
            DocumentSearchHit(
                document_id=UUID(hit["metadata"]["document_id"]),
                chunk_id=None,
                content=hit["content"],
                score=hit["score"],
                metadata=hit["metadata"],
            )
            for hit in ranked[:limit]
        ]

