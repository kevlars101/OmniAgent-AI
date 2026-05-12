import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)

class Episode:
    def __init__(self, user_id: str, workflow_id: str, agent: str, action: str, content: str, metadata: dict = None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.workflow_id = workflow_id
        self.agent = agent
        self.action = action
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc)

class EpisodicMemory:
    """
    Chronological store of all events, actions, and messages within a workflow.
    In production, this would be backed by PostgreSQL or a time-series database.
    """
    def __init__(self):
        # Mock storage: list of Episodes
        self._store: List[Episode] = []

    async def add_episode(self, episode: Episode) -> None:
        """Stores a new episode in the timeline."""
        self._store.append(episode)
        logger.debug(f"Stored episodic memory for {episode.agent}: {episode.action}")

    async def get_recent_episodes(self, user_id: str, workflow_id: Optional[str] = None, limit: int = 20) -> List[Episode]:
        """Retrieves recent episodes for context construction."""
        episodes = [e for e in self._store if e.user_id == user_id]
        if workflow_id:
            episodes = [e for e in episodes if e.workflow_id == workflow_id]
        
        # Sort by timestamp descending and take the limit
        episodes.sort(key=lambda x: x.timestamp, reverse=True)
        return episodes[:limit]
    
    async def get_episodes_by_agent(self, user_id: str, agent: str, limit: int = 10) -> List[Episode]:
        """Retrieves history specific to a single agent's past actions."""
        episodes = [e for e in self._store if e.user_id == user_id and e.agent == agent]
        episodes.sort(key=lambda x: x.timestamp, reverse=True)
        return episodes[:limit]

# Singleton instance for the platform
episodic_memory_store = EpisodicMemory()
