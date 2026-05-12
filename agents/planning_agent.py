from uuid import uuid4

from agents.core.agent_base import BaseAgent
from agents.core.memory import workspace_memory
from agents.core.state import AgentFinding, AgentTask, WorkflowState


class PlanningAgent(BaseAgent):
    name = "planning"

    async def run(self, state: WorkflowState) -> WorkflowState:
        objective = state["objective"]
        tasks = [
            AgentTask(
                id=str(uuid4()),
                agent="research",
                title="Retrieve context",
                objective=f"Find relevant evidence and context for: {objective}",
            ),
            AgentTask(
                id=str(uuid4()),
                agent="coding",
                title="Design implementation approach",
                objective=f"Convert research context into implementation guidance for: {objective}",
            ),
            AgentTask(
                id=str(uuid4()),
                agent="report",
                title="Synthesize report",
                objective=f"Create a concise technical report for: {objective}",
            ),
            AgentTask(
                id=str(uuid4()),
                agent="presentation",
                title="Prepare presentation outline",
                objective=f"Create an executive presentation outline for: {objective}",
            ),
        ]
        state["tasks"] = [task.model_dump() for task in tasks]
        workspace_memory.add_finding(
            state["workflow_id"],
            AgentFinding(
                agent=self.name,
                title="Workflow plan",
                content="Created a four-stage workflow: research, implementation design, report, presentation.",
            ),
        )
        state["status"] = "running"
        return state

