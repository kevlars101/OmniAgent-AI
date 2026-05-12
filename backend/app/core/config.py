from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "OmniAgent AI"
    app_version: str = "0.1.0"
    environment: Literal["local", "staging", "production"] = "local"
    api_v1_prefix: str = "/api/v1"

    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://omniagent:omniagent@localhost:5432/omniagent"
    )
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    auth_issuer: str | None = None
    auth_audience: str | None = None
    auth_dev_user_id: str = "00000000-0000-0000-0000-000000000001"
    auth_dev_email: str = "local@omniagent.ai"

    upload_dir: str = "var/uploads"
    max_upload_mb: int = 25

    chroma_path: str = "var/chroma"
    chroma_collection: str = "omniagent_documents"

    embedding_provider: Literal["openai", "gemini", "local_stub"] = "gemini"
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    gemini_api_key: str | None = None
    gemini_embedding_model: str = "text-embedding-004"

    chunk_size: int = 1200
    chunk_overlap: int = 180

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
