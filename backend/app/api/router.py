from fastapi import APIRouter

from app.api.endpoints import health, documents, workflows

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
