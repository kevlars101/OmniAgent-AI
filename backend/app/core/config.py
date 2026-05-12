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

    # LLM Settings (passed to LangGraph agents)
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
