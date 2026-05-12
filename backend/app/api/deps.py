from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
import uuid

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Mock auth dependency for now. In production, use OAuth2PasswordBearer + JWT validation.
async def get_current_user_id() -> uuid.UUID:
    # Always returning a static UUID for development/testing
    return uuid.UUID("00000000-0000-0000-0000-000000000000")
