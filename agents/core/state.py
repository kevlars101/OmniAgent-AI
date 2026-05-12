from typing import Literal, NotRequired, TypedDict
from uuid import UUID

from pydantic import BaseModel, Field

AgentName = Literal["planning", "research", "coding", "report", "presentation"]
WorkflowStatus = Literal["queued", "running", "completed", "failed"]


class AgentFinding(BaseModel):
    agent: AgentName
    title: str
    content: str
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    citations: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class AgentTask(BaseModel):
    id: str
    agent: AgentName
    title: str
    objective: str
    depends_on: list[str] = Field(default_factory=list)
    status: WorkflowStatus = "queued"


class AgentMessage(BaseModel):
    agent: AgentName
    content: str
    metadata: dict = Field(default_factory=dict)


class WorkflowState(TypedDict):
    workflow_id: UUID
    user_id: UUID
    conversation_id: UUID | None
    objective: str
    document_ids: list[UUID]
    tasks: list[dict]
    active_agent: NotRequired[AgentName]
    findings: list[dict]
    messages: list[dict]
    artifacts: dict
    errors: list[str]
    status: WorkflowStatus


def create_initial_state(
    workflow_id: UUID,
    user_id: UUID,
    conversation_id: UUID | None,
    objective: str,
    document_ids: list[UUID] | None = None,
) -> WorkflowState:
    return {
        "workflow_id": workflow_id,
        "user_id": user_id,
        "conversation_id": conversation_id,
        "objective": objective,
        "document_ids": document_ids or [],
        "tasks": [],
        "findings": [],
        "messages": [],
        "artifacts": {},
        "errors": [],
        "status": "queued",
    }

