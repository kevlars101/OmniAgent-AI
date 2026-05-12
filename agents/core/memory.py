from collections import defaultdict
from uuid import UUID

from agents.core.state import AgentFinding, AgentMessage, AgentName, WorkflowState


class WorkspaceMemory:
    def __init__(self) -> None:
        self._findings: dict[UUID, list[AgentFinding]] = defaultdict(list)
        self._messages: dict[UUID, list[AgentMessage]] = defaultdict(list)
        self._artifacts: dict[UUID, dict] = defaultdict(dict)

    def hydrate(self, state: WorkflowState) -> WorkflowState:
        workflow_id = state["workflow_id"]
        state["findings"] = [finding.model_dump() for finding in self._findings[workflow_id]]
        state["messages"] = [message.model_dump() for message in self._messages[workflow_id]]
        state["artifacts"] = dict(self._artifacts[workflow_id])
        return state

    def add_finding(self, workflow_id: UUID, finding: AgentFinding) -> None:
        self._findings[workflow_id].append(finding)

    def add_message(self, workflow_id: UUID, agent: AgentName, content: str, metadata: dict | None = None) -> None:
        self._messages[workflow_id].append(
            AgentMessage(agent=agent, content=content, metadata=metadata or {})
        )

    def set_artifact(self, workflow_id: UUID, key: str, value: dict | str | list) -> None:
        self._artifacts[workflow_id][key] = value

    def snapshot(self, workflow_id: UUID) -> dict:
        return {
            "findings": [finding.model_dump() for finding in self._findings[workflow_id]],
            "messages": [message.model_dump() for message in self._messages[workflow_id]],
            "artifacts": self._artifacts[workflow_id],
        }


workspace_memory = WorkspaceMemory()

