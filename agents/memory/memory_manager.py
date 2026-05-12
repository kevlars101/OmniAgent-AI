import logging
from typing import List, Dict, Any, Optional

from agents.memory.episodic_memory import Episode, episodic_memory_store
from agents.memory.semantic_memory import semantic_memory_store
from agents.memory.context_optimizer import context_optimizer
from agents.memory.reflection_engine import reflection_engine

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Unified facade for all long-term memory operations.
    Agents use this to commit actions to memory and retrieve optimized,
    deduplicated context for their prompts.
    """
    
    async def commit_action(self, user_id: str, workflow_id: str, agent: str, action: str, content: str, metadata: dict = None) -> None:
        """
        Logs a specific action taken by an agent into Episodic Memory.
        """
        episode = Episode(
            user_id=user_id,
            workflow_id=workflow_id,
            agent=agent,
            action=action,
            content=content,
            metadata=metadata
        )
        await episodic_memory_store.add_episode(episode)
        
    async def retrieve_context(self, user_id: str, query: str, workflow_id: Optional[str] = None) -> str:
        """
        Retrieves a highly optimized context string combining:
        1. Recent chronological events (Episodic)
        2. Generalized knowledge & preferences related to the query (Semantic)
        """
        logger.debug(f"Retrieving optimized context for query: {query[:30]}...")
        
        # 1. Fetch semantic knowledge related to the current task
        raw_semantic = await semantic_memory_store.search_knowledge(user_id=user_id, query=query, limit=10)
        
        # 2. Optimize Semantic Memory (Decay & Deduplicate)
        decayed_semantic = context_optimizer.apply_decay(raw_semantic)
        unique_semantic = context_optimizer.deduplicate(decayed_semantic)
        
        # 3. Fetch recent episodic memory
        recent_episodes = await episodic_memory_store.get_recent_episodes(user_id=user_id, workflow_id=workflow_id, limit=5)
        
        # 4. Construct final context string
        context_parts = []
        
        if unique_semantic:
            context_parts.append("--- LONG-TERM KNOWLEDGE ---")
            for mem in unique_semantic[:5]: # Take top 5 optimized facts
                context_parts.append(f"- {mem['metadata'].get('category', 'Fact')}: {mem['text']}")
                
        if recent_episodes:
            context_parts.append("\n--- RECENT ACTIONS ---")
            for ep in reversed(recent_episodes): # Chronological order
                context_parts.append(f"[{ep.agent}]: {ep.content}")
                
        final_context = "\n".join(context_parts)
        
        # 5. Compress if necessary
        return context_optimizer.compress_context(final_context)

    async def consolidate_workflow(self, user_id: str, workflow_id: str) -> None:
        """
        Triggered when a workflow ends. Initiates the reflection loop to
        extract semantic knowledge from episodic logs.
        """
        logger.info(f"Consolidating workflow {workflow_id} into long-term memory...")
        # In a real app, this should be dispatched as a background task (e.g., Celery)
        await reflection_engine.run_reflection_loop(user_id=user_id, workflow_id=workflow_id)

# Global singleton
memory_manager = MemoryManager()
