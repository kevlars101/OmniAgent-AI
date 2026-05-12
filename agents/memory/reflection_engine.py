import logging
from typing import List
from agents.memory.episodic_memory import Episode, episodic_memory_store
from agents.memory.semantic_memory import semantic_memory_store

logger = logging.getLogger(__name__)

class ReflectionEngine:
    """
    An autonomous background process that analyzes recent episodic memory
    and synthesizes persistent semantic knowledge.
    """
    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider

    async def run_reflection_loop(self, user_id: str, workflow_id: str):
        """
        Analyzes a completed workflow's episodes to extract lessons learned.
        """
        logger.info(f"Starting reflection loop for workflow {workflow_id}")
        
        episodes = await episodic_memory_store.get_recent_episodes(user_id=user_id, workflow_id=workflow_id, limit=50)
        
        if not episodes:
            logger.debug("No episodes found for reflection.")
            return

        # 1. Prepare context for reflection
        transcript = "\n".join([f"[{e.agent}] {e.action}: {e.content}" for e in episodes])
        
        # 2. Extract facts via LLM (Simulated here)
        # prompt = f"Analyze this workflow transcript and extract 3 key facts, preferences, or technical constraints:\n{transcript}"
        # extracted_facts = await self.llm_provider.generate(prompt)
        
        simulated_facts = [
            {"concept": "User preference", "category": "preference", "content": "User prefers React with TailwindCSS over standard CSS."},
            {"concept": "Technical blocker", "category": "technical", "content": "PostgreSQL connection requires SSL mode=require in this environment."}
        ]
        
        # 3. Consolidate into Semantic Memory
        for fact in simulated_facts:
            await semantic_memory_store.add_knowledge(
                user_id=user_id,
                concept=fact["concept"],
                category=fact["category"],
                content=fact["content"],
                importance=1.5 # Synthesized facts are highly important
            )
            
        logger.info(f"Reflection complete. Consolidated {len(simulated_facts)} facts into semantic memory.")

# Singleton instance
reflection_engine = ReflectionEngine()
