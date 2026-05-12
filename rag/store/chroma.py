from uuid import UUID

import chromadb
from chromadb.api.models.Collection import Collection

from app.core.config import settings
from rag.chunking.semantic_chunker import Chunk
from rag.embeddings.provider import get_embedding_provider


class ChromaVectorStore:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection: Collection = self.client.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"hnsw:space": "cosine"},
        )
        self.embedding_provider = get_embedding_provider()

    async def add_chunks(self, user_id: UUID, document_id: UUID, chunks: list[Chunk]) -> list[str]:
        if not chunks:
            return []

        ids = [f"{document_id}:{index}" for index, _ in enumerate(chunks)]
        texts = [chunk.content for chunk in chunks]
        embeddings = await self.embedding_provider.embed_texts(texts)
        metadatas = [
            {
                **chunk.metadata,
                "user_id": str(user_id),
                "document_id": str(document_id),
                "chunk_index": index,
            }
            for index, chunk in enumerate(chunks)
        ]

        self.collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
        return ids

    async def query(
        self,
        user_id: UUID,
        query: str,
        limit: int,
        document_ids: list[UUID] | None = None,
    ) -> list[dict]:
        embedding = await self.embedding_provider.embed_query(query)
        where: dict = {"user_id": str(user_id)}
        if document_ids:
            where = {"$and": [where, {"document_id": {"$in": [str(item) for item in document_ids]}}]}

        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=limit,
            where=where,
            include=["documents", "distances", "metadatas"],
        )

        documents = result.get("documents", [[]])[0]
        distances = result.get("distances", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        ids = result.get("ids", [[]])[0]

        hits = []
        for index, content in enumerate(documents):
            metadata = metadatas[index] or {}
            hits.append(
                {
                    "id": ids[index],
                    "content": content,
                    "score": max(0.0, 1.0 - float(distances[index])),
                    "metadata": metadata,
                }
            )
        return hits

