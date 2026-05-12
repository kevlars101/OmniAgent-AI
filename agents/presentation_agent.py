from agents.core.agent_base import BaseAgent
from agents.core.memory import workspace_memory
from agents.core.state import AgentFinding, WorkflowState


class PresentationAgent(BaseAgent):
    name = "presentation"

    async def run(self, state: WorkflowState) -> WorkflowState:
        outline = [
            {"title": "Objective", "bullets": [state["objective"]]},
            {"title": "Evidence", "bullets": self._finding_titles(state, "research")},
            {"title": "Implementation Path", "bullets": self._finding_titles(state, "coding")},
            {"title": "Recommended Next Steps", "bullets": ["Validate retrieval quality", "Add UI workflow controls"]},
        ]
        workspace_memory.set_artifact(state["workflow_id"], "presentation_outline", outline)
        workspace_memory.add_finding(
            state["workflow_id"],
            AgentFinding(
                agent=self.name,
                title="Presentation outline",
                content="Prepared a four-slide executive outline from the workflow findings.",
                confidence=0.86,
            ),
        )
        state["status"] = "completed"
        return state

    def _finding_titles(self, state: WorkflowState, agent: str) -> list[str]:
        titles = [finding["title"] for finding in state["findings"] if finding["agent"] == agent]
        return titles or ["No findings available yet."]

