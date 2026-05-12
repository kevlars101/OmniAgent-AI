from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import os
import aiofiles
from fastapi import UploadFile, BackgroundTasks
from app.db.models import Document

# In a real system, this would upload to S3/GCS and push to a Celery queue for RAG ingestion
UPLOAD_DIR = "var/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Add RAG pipeline import (assuming rag module is in PYTHONPATH, e.g., adjacent to backend)
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
try:
    from rag.ingestion.pipeline import rag_pipeline
except ImportError:
    rag_pipeline = None

class DocumentService:
    @staticmethod
    async def upload_document(db: AsyncSession, file: UploadFile, user_id: UUID, background_tasks: BackgroundTasks = None) -> Document:
        file_path = os.path.join(UPLOAD_DIR, f"{user_id}_{file.filename}")
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        db_doc = Document(
            filename=file.filename,
            content_type=file.content_type,
            file_path=file_path,
            user_id=user_id
        )
        db.add(db_doc)
        await db.commit()
        await db.refresh(db_doc)
        
        # Dispatch background task for RAG ingestion
        if background_tasks and rag_pipeline:
            # Create a sync wrapper for the async background task execution if necessary,
            # or FastAPI handles async background tasks directly.
            background_tasks.add_task(
                rag_pipeline.ingest_document,
                file_path=file_path,
                user_id=user_id,
                document_id=db_doc.id
            )
        
        return db_doc

    @staticmethod
    async def get_documents(db: AsyncSession, user_id: UUID):
        from sqlalchemy import select
        result = await db.execute(select(Document).where(Document.user_id == user_id))
        return result.scalars().all()
