from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, AnyHttpUrl
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "OmniAgentAI Backend"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # Configurable in prod

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/omniagent"
    redis_url: str = "redis://localhost:6379/0"

    # Authentication (Dev Placeholders)
    auth_dev_user_id: str = "00000000-0000-0000-0000-000000000000"
    auth_dev_email: str = "dev@omniagent.ai"

    # File Uploads
    upload_dir: str = "var/uploads"
    max_upload_mb: int = 20

    # Vector DB (Chroma)
    chroma_db_dir: str = "var/chroma"
    chroma_collection_name: str = "omniagent_knowledge"

    # Retrieval Settings
    retrieval_top_k: int = 5
    similarity_threshold: float = 0.3
    max_context_chunks: int = 10

    # LLM Settings (passed to LangGraph agents)
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    model_config = SettingsConfigDict(case_sensitive=False, env_file=".env", extra="ignore")

settings = Settings()
