import asyncio
from typing import List
import logging

logger = logging.getLogger(__name__)

class EmbeddingProvider:
    """
    Async interface for generating dense vector embeddings.
    Wraps standard providers like OpenAIEmbeddings, Cohere, or local HuggingFace models.
    """
    def __init__(self, model_name: str = "text-embedding-3-small", dimensions: int = 1536):
        self.model_name = model_name
        self.dimensions = dimensions
        
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        logger.info(f"Generating embeddings for {len(texts)} chunks using {self.model_name}")
        
        # Simulate API call latency
        await asyncio.sleep(0.2)
        
        # Generate dummy embeddings for demonstration
        # In production:
        # client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        # response = await client.embeddings.create(input=texts, model=self.model_name)
        # return [data.embedding for data in response.data]
        
        return [[0.01 * i for i in range(self.dimensions)] for _ in texts]
        
    async def embed_query(self, text: str) -> List[float]:
        logger.debug(f"Generating query embedding")
        await asyncio.sleep(0.05)
        return [0.01 * i for i in range(self.dimensions)]
