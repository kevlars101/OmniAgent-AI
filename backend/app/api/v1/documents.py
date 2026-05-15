from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import Principal, require_principal
from app.db.session import get_session
from app.schemas.documents import DocumentIngestResponse, DocumentSearchRequest, DocumentSearchResponse
from app.services.documents import DocumentService

router = APIRouter()


@router.post("/ingest", response_model=DocumentIngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_document(
    file: UploadFile = File(...),
    conversation_id: Optional[UUID] = None,
    principal: Principal = Depends(require_principal),
    session: AsyncSession = Depends(get_session),
) -> DocumentIngestResponse:
    service = DocumentService(session)
    return await service.ingest_upload(
        file=file,
        user_id=principal.user_id,
        conversation_id=conversation_id,
    )


@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(
    request: DocumentSearchRequest,
    principal: Principal = Depends(require_principal),
) -> DocumentSearchResponse:
    service = DocumentService()
    return await service.search(user_id=principal.user_id, request=request)

