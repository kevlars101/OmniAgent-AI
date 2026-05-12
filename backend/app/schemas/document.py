from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
