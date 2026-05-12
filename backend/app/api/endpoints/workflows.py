from fastapi import APIRouter, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.api.deps import get_db, get_current_user_id
from app.schemas.workflow import WorkflowCreate, WorkflowStateResponse, WorkflowResponse
from app.services.workflow_service import WorkflowService

router = APIRouter()

@router.post("/run", response_model=WorkflowStateResponse)
async def run_workflow(
    workflow_in: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Create and run a workflow synchronously.
    In a high-load environment, you would use BackgroundTasks and return the workflow ID immediately.
    """
    # 1. Create Workflow Record
    workflow = await WorkflowService.create_workflow(
        db=db, 
        objective=workflow_in.objective, 
        user_id=user_id
    )
    
    # 2. Execute LangGraph agents
    # Overriding the schema user_id with the authenticated user_id for security
    completed_workflow = await WorkflowService.run_workflow(
        db=db, 
        workflow_id=workflow.id, 
        document_ids=workflow_in.document_ids
    )
    
    return completed_workflow


@router.websocket("/{workflow_id}/stream")
async def stream_workflow(
    websocket: WebSocket,
    workflow_id: UUID,
    # Note: WebSocket auth requires a token in query params or headers
    # For now we mock it as standard UUID
):
    """
    Stream real-time agent updates via WebSockets.
    """
    user_id = UUID("00000000-0000-0000-0000-000000000000") # Mock auth
    
    try:
        await WorkflowService.stream_workflow(websocket, workflow_id, user_id)
    except WebSocketDisconnect:
        # Client disconnected early
        pass
