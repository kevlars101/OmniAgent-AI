import os
from celery import Celery

# Ensure correct Python path when running in Celery worker context
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Setup Celery Application
celery_app = Celery(
    "omniagent_worker",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="ingest_document_task")
def ingest_document_task(file_path: str, user_id: str, document_id: str):
    """
    Background worker task to process heavy RAG chunking and embedding.
    Because our RAG pipeline is async, we use asyncio.run here inside the sync Celery task.
    """
    import asyncio
    try:
        from rag.ingestion.pipeline import rag_pipeline
        from uuid import UUID
        
        # Run the async pipeline synchronously in the worker
        result = asyncio.run(
            rag_pipeline.ingest_document(
                file_path=file_path, 
                user_id=UUID(user_id), 
                document_id=UUID(document_id)
            )
        )
        return result
    except ImportError:
        return {"error": "RAG pipeline not found"}
    except Exception as e:
        return {"error": str(e)}
