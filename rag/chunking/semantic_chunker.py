import re
from typing import List, Dict, Any
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class DocumentChunk(BaseModel):
    text: str
    metadata: Dict[str, Any]
    chunk_index: int

class SemanticChunker:
    """
    Splits text into smaller, overlapping chunks while attempting to respect semantic boundaries (sentences/paragraphs).
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str, base_metadata: Dict[str, Any]) -> List[DocumentChunk]:
        logger.debug(f"Chunking document {base_metadata.get('document_id')} with size {self.chunk_size} and overlap {self.chunk_overlap}")
        
        # Simple fallback tokenization (character/word based for demonstration)
        # In production, use tiktoken to count actual LLM tokens.
        
        # Split by paragraphs first to try and maintain semantic boundaries
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk_text = ""
        current_length = 0
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            para_length = len(para) # Approximate token count by char length for demo
            
            # If a single paragraph is too large, it needs a hard split (omitted for brevity)
            if current_length + para_length > self.chunk_size and current_chunk_text:
                # Save the current chunk
                chunks.append(DocumentChunk(
                    text=current_chunk_text.strip(),
                    metadata=base_metadata.copy(),
                    chunk_index=chunk_index
                ))
                chunk_index += 1
                
                # Start new chunk, carrying over overlap from the end of the last chunk
                # In a real implementation, overlap logic needs to precisely back-track tokens
                overlap_text = current_chunk_text[-self.chunk_overlap:] if len(current_chunk_text) > self.chunk_overlap else current_chunk_text
                current_chunk_text = overlap_text + " " + para
                current_length = len(current_chunk_text)
            else:
                current_chunk_text += " " + para
                current_length = len(current_chunk_text)
                
        # Add the last chunk
        if current_chunk_text:
            chunks.append(DocumentChunk(
                text=current_chunk_text.strip(),
                metadata=base_metadata.copy(),
                chunk_index=chunk_index
            ))
            
        return chunks
