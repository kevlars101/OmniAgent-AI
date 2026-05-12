import time
import math
from typing import List, Dict, Any

class ContextOptimizer:
    """
    Manages the limited context window of LLMs by applying memory decay,
    deduplication, and relevance scoring to raw memory retrievals.
    """
    def __init__(self, decay_rate: float = 0.05, max_tokens: int = 4000):
        self.decay_rate = decay_rate
        self.max_tokens = max_tokens

    def apply_decay(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Applies exponential time decay to memory scores.
        Older memories have their relevance score reduced unless they have high initial importance.
        """
        current_time = time.time()
        for memory in memories:
            timestamp = memory.get("metadata", {}).get("timestamp", current_time)
            # Days elapsed (simplified for demo)
            days_elapsed = max(0, (current_time - timestamp) / 86400)
            
            base_score = memory.get("score", 1.0)
            importance = memory.get("metadata", {}).get("importance", 1.0)
            
            # Decay formula: score * e^(-decay_rate * days_elapsed / importance)
            decayed_score = base_score * math.exp(-self.decay_rate * days_elapsed / importance)
            memory["decayed_score"] = decayed_score
            
        # Sort by the new decayed score
        return sorted(memories, key=lambda x: x.get("decayed_score", 0), reverse=True)

    def deduplicate(self, memories: List[Dict[str, Any]], similarity_threshold: float = 0.9) -> List[Dict[str, Any]]:
        """
        Removes highly overlapping or redundant memories.
        In a real implementation, this would compute pairwise cosine similarity of the texts.
        """
        unique_memories = []
        seen_texts = set()
        
        for memory in memories:
            text_prefix = memory["text"][:100] # Simplistic deduplication based on prefix
            if text_prefix not in seen_texts:
                seen_texts.add(text_prefix)
                unique_memories.append(memory)
                
        return unique_memories

    def compress_context(self, text: str) -> str:
        """
        Compresses text by removing filler words or using an LLM to summarize.
        (Placeholder for a true LLM-based summary call).
        """
        return text # Returns raw for now, would hook to a small local model like DistilBART

# Singleton instance
context_optimizer = ContextOptimizer()
