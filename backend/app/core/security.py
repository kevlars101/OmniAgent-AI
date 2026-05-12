from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    user_id: UUID
    email: str
    subject: str


async def require_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Principal:
    # Local Phase 2 implementation: accept a bearer token boundary but resolve a
    # stable dev principal until Clerk JWT verification is added in Phase 4.
    subject = credentials.credentials if credentials else "local-dev"
    return Principal(
        user_id=UUID(settings.auth_dev_user_id),
        email=settings.auth_dev_email,
        subject=subject,
    )

