import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.main import app
from app.db.base import Base
from app.db.session import get_session
from app.core.config import settings

# Use a separate test database or an in-memory one if preferred
# For stabilization smoke tests, we'll try to use the configured DB but we should be careful
# In a real setup, we'd override DATABASE_URL here.
TEST_DATABASE_URL = settings.DATABASE_URL + "_test"

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    # This is a smoke test helper. In a full suite, we'd handle DB creation.
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        # For safety in smoke tests, we don't drop everything unless explicitly asked
        pass
    await engine.dispose()

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def db_session():
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        yield session
