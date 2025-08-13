# tests/test_auth_routes.py
"""
Integration tests for /auth routes using TestClient.
These ensure request/response wiring, headers, and DI are correct.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_login_and_me_flow(
    client: AsyncClient, session: AsyncSession, redis_client: Redis, make_user
):
    """A normal login returns a token; /auth/me returns the user shape."""
    await make_user(email="api@example.com", password="MyPass123!!")

    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "api@example.com", "password": "MyPass123!!"},
    )
    assert r.status_code == 200
    data = r.json()
    token = data["access_token"]
    assert data["token_type"] == "bearer"

    # /auth/me
    r2 = await client.get("/api/v1/auth/me", headers=_auth_header(token))
    assert r2.status_code == 200
    me = r2.json()
    assert me["email"] == "api@example.com"
    assert isinstance(me["roles"], list)
    assert isinstance(me["permissions"], list)


@pytest.mark.asyncio
async def test_login_rate_limited(client: AsyncClient):
    """Exceeding login attempts triggers 429 via the login_rate_limit dep."""
    payload = {"email": "ratelimit@example.com", "password": "anything"}
    # First few attempts allowed
    for _ in range(5):
        await client.post("/api/v1/auth/login", json=payload)
    # Next attempt should be blocked
    r = await client.post("/api/v1/auth/login", json=payload)
    assert r.status_code == 429
    assert "Rate limit exceeded" in r.json()["detail"]


@pytest.mark.asyncio
async def test_logout_revokes_token(client: AsyncClient, make_user, auth_header):
    """
    Logout blacklists the token;
    subsequent /auth/me with same token is rejected.
    """
    await make_user(email="logout2@example.com", password="TempPass123!!")

    headers = await auth_header("logout2@example.com", "TempPass123!!")
    token = headers["Authorization"].split(" ")[1]

    r2 = await client.post("/api/v1/auth/logout", headers=headers)
    assert r2.status_code == 200

    # Using the same token should now fail on protected endpoints
    r3 = await client.get("/api/v1/auth/me", headers=_auth_header(token))
    assert r3.status_code == 401
