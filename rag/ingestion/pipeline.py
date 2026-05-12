import os
from typing import Dict, Any
from uuid import UUID
import logging

from rag.ingestion.pdf_loader import PDFLoader
from rag.ingestion.docx_loader import DocxLoader
from rag.chunking.semantic_chunker import SemanticChunker
from rag.store.chroma import ChromaVectorStore

logger = logging.getLogger(__name__)

class RAGPipeline:
    """
    Orchestrates the entire ingestion flow: Loading -> Chunking -> Embedding -> Storage.
    """
    def __init__(self, vector_store: ChromaVectorStore | None = None):
        self.pdf_loader = PDFLoader()
        self.docx_loader = DocxLoader()
        self.chunker = SemanticChunker(chunk_size=800, chunk_overlap=150)
        self.vector_store = vector_store or ChromaVectorStore()

    async def ingest_document(self, file_path: str, user_id: UUID, document_id: UUID) -> Dict[str, Any]:
        """
        Main entry point for processing a new document.
        Designed to be run as an async background task.
        """
        logger.info(f"Starting RAG ingestion pipeline for {file_path}")
        
        # 1. Determine file type and load
        _, ext = os.path.splitext(file_path.lower())
        
        if ext == '.pdf':
            doc_extract = await self.pdf_loader.load_async(file_path, str(user_id), str(document_id))
        elif ext == '.docx':
            doc_extract = await self.docx_loader.load_async(file_path, str(user_id), str(document_id))
        elif ext == '.txt':
            # Simple text fallback
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            doc_extract = type('obj', (object,), {'text': text, 'metadata': {
                'source': file_path, 'user_id': str(user_id), 'document_id': str(document_id), 'file_type': 'txt'
            }})()
        else:
            raise ValueError(f"Unsupported file type: {ext}")
            
        logger.debug(f"Extraction complete. Extracted {len(doc_extract.text)} characters.")
        
        # 2. Semantic Chunking
        chunks = self.chunker.split_text(doc_extract.text, base_metadata=doc_extract.metadata)
        logger.debug(f"Document split into {len(chunks)} semantic chunks.")
        
        # 3. Embedding and Storage
        await self.vector_store.add_chunks(chunks)
        
        logger.info(f"Successfully ingested {document_id} into RAG storage.")
        
        return {
            "status": "success",
            "document_id": str(document_id),
            "chunks_created": len(chunks)
        }

# Global singleton for FastAPI injection
rag_pipeline = RAGPipeline()
