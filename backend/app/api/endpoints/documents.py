from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.api.deps import get_db, get_current_user_id
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Upload a document. Simulates ingesting into the RAG pipeline.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    document = await DocumentService.upload_document(db=db, file=file, user_id=user_id, background_tasks=background_tasks)
    return document

@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    List all uploaded documents for the user.
    """
    documents = await DocumentService.get_documents(db=db, user_id=user_id)
    return documents
