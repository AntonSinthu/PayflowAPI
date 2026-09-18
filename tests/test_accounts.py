import pytest
from httpx import AsyncClient

from tests.conftest import register_and_login


@pytest.mark.anyio
async def test_deposit_increases_balance(client: AsyncClient):
    headers = await register_and_login(client)
    account = (await client.post("/accounts", headers=headers)).json()

    response = await client.post(
        f"/accounts/{account['id']}/deposit",
        json={"amount": "100"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["balance"] == "100.0000"


@pytest.mark.anyio
async def test_withdraw_more_than_balance_fails(client: AsyncClient):
    headers = await register_and_login(client)
    account = (await client.post("/accounts", headers=headers)).json()

    response = await client.post(
        f"/accounts/{account['id']}/withdraw",
        json={"amount": "50"},
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"


@pytest.mark.anyio
async def test_cannot_deposit_into_someone_elses_account(client: AsyncClient):
    owner_headers = await register_and_login(client, "owner@example.com")
    account = (await client.post("/accounts", headers=owner_headers)).json()

    attacker_headers = await register_and_login(client, "attacker@example.com")

    response = await client.post(
        f"/accounts/{account['id']}/deposit",
        json={"amount": "10"},
        headers=attacker_headers,
    )

    assert response.status_code == 403