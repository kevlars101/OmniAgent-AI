from agents.core.agent_base import BaseAgent
from agents.core.memory import workspace_memory
from agents.core.state import AgentFinding, WorkflowState
from agents.tools.document_search import DocumentSearchTool


class ResearchAgent(BaseAgent):
    name = "research"

    def __init__(self, document_search: DocumentSearchTool | None = None) -> None:
        self.document_search = document_search or DocumentSearchTool()

    async def run(self, state: WorkflowState) -> WorkflowState:
        hits = await self.document_search.search(
            user_id=state["user_id"],
            query=state["objective"],
            document_ids=state["document_ids"] or None,
            limit=5,
        )
        if hits:
            content = "\n\n".join(hit["content"] for hit in hits[:3])
            citations = [
                f"document:{hit['metadata'].get('document_id')}#chunk:{hit['metadata'].get('chunk_index')}"
                for hit in hits
            ]
        else:
            content = "No indexed document evidence was found. Continue using the user objective as primary context."
            citations = []

        workspace_memory.add_finding(
            state["workflow_id"],
            AgentFinding(
                agent=self.name,
                title="Research context",
                content=content,
                confidence=0.75 if hits else 0.45,
                citations=citations,
                metadata={"hit_count": len(hits)},
            ),
        )
        return state

