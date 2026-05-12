from fastapi import APIRouter, Depends

from app.core.security import Principal, require_principal
from app.schemas.workflows import WorkflowRunRequest, WorkflowRunResponse
from app.services.workflows import WorkflowService

router = APIRouter()


@router.post("/run", response_model=WorkflowRunResponse)
async def run_workflow(
    request: WorkflowRunRequest,
    principal: Principal = Depends(require_principal),
) -> WorkflowRunResponse:
    return await WorkflowService().run(user_id=principal.user_id, request=request)

