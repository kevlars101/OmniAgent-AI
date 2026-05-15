from dataclasses import dataclass
from uuid import UUID
from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class Principal:
    user_id: UUID
    email: str
    subject: str


async def require_principal(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Principal:
    """
    Dependency to require an authenticated principal.
    For local development, returns a default principal if no token is provided.
    """
    # Real Clerk/JWT validation is added in Phase 4.
    subject = credentials.credentials if credentials else "local-dev"
    return Principal(
        user_id=UUID(settings.auth_dev_user_id),
        email=settings.auth_dev_email,
        subject=subject,
    )
