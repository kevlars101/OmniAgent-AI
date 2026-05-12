from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

class WorkflowCreate(BaseModel):
    objective: str
    user_id: UUID
    document_ids: Optional[List[UUID]] = None

class WorkflowResponse(BaseModel):
    id: UUID
    user_id: UUID
    objective: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WorkflowStateResponse(WorkflowResponse):
    state_data: Optional[Dict[str, Any]] = None
