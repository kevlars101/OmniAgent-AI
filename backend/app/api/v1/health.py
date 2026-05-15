from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis

from app.schemas.health import HealthResponse
from app.db.session import get_session
from app.core.config import settings

router = APIRouter()

@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check to verify API is responsive."""
    return HealthResponse(status="ok")

@router.get("/db", response_model=HealthResponse)
async def health_db(session: AsyncSession = Depends(get_session)) -> HealthResponse:
    """Check connectivity to PostgreSQL."""
    try:
        await session.execute(text("SELECT 1"))
        return HealthResponse(status="ok")
    except Exception as e:
        return HealthResponse(status=f"error: {str(e)}")

@router.get("/redis", response_model=HealthResponse)
async def health_redis() -> HealthResponse:
    """Check connectivity to Redis."""
    try:
        r = redis.from_url(settings.redis_url)
        await r.ping()
        await r.close()
        return HealthResponse(status="ok")
    except Exception as e:
        return HealthResponse(status=f"error: {str(e)}")

@router.get("/vectorstore", response_model=HealthResponse)
async def health_vectorstore() -> HealthResponse:
    """Check connectivity to ChromaDB."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=settings.chroma_db_dir)
        client.heartbeat()
        return HealthResponse(status="ok")
    except Exception as e:
        return HealthResponse(status=f"error: {str(e)}")
