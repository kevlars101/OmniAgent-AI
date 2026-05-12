from uuid import UUID

from pydantic import BaseModel, Field


class WorkflowRunRequest(BaseModel):
    objective: str = Field(min_length=4, max_length=4000)
    conversation_id: UUID | None = None
    document_ids: list[UUID] = Field(default_factory=list)


class WorkflowRunResponse(BaseModel):
    workflow_id: UUID
    status: str
    findings: list[dict]
    messages: list[dict]
    artifacts: dict

