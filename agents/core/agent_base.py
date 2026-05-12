from abc import ABC, abstractmethod

from agents.core.memory import workspace_memory
from agents.core.state import AgentName, WorkflowState


class BaseAgent(ABC):
    name: AgentName

    async def __call__(self, state: WorkflowState) -> WorkflowState:
        workflow_id = state["workflow_id"]
        state["active_agent"] = self.name
        workspace_memory.add_message(workflow_id, self.name, f"{self.name} agent started.")
        next_state = await self.run(state)
        snapshot = workspace_memory.snapshot(workflow_id)
        next_state["findings"] = snapshot["findings"]
        next_state["messages"] = snapshot["messages"]
        next_state["artifacts"] = snapshot["artifacts"]
        return next_state

    @abstractmethod
    async def run(self, state: WorkflowState) -> WorkflowState:
        ...

