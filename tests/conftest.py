import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_payflow.db"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-real-use"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import Base, engine, get_db
from app.main import app

pytest_plugins = ["anyio"]


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
        
async def register_and_login(client: AsyncClient, email: str = "user@example.com") -> dict[str, str]:
    await client.post("/register", json={"email": email, "password": "testpass123"})
    response = await client.post("/login", data={"username": email, "password": "testpass123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}