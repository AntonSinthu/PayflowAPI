import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_register_creates_a_user(client: AsyncClient):
    response = await client.post(
    "/register",
    json={"email": "test@example.com", "password": "testpass123"},
)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data
    assert "hashed_password" not in data