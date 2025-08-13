"""
Test configuration and fixtures
"""
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlmodel import select
import pytest
import httpx
from main import app
from database_async import get_async_session, get_async_redis
from test_database import create_test_db_and_tables, get_test_async_session, get_test_redis
from utils.security import get_password_hash
from models.user import User, UserRole
from models.role import Role, RolePermission
from models.permission import Permission
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis


@pytest_asyncio.fixture(name="session")
async def session_fixture() -> AsyncSession:
    """Create test database session"""
    await create_test_db_and_tables()
    async for session in get_test_async_session():
        yield session


@pytest_asyncio.fixture(name="redis_client")
async def redis_client_fixture() -> Redis:
    """Create fake Redis client for testing"""
    return get_test_redis()


@pytest_asyncio.fixture(name="client")
async def client_fixture(session: AsyncSession, redis_client: Redis):
    """Create test client with dependency overrides"""

    async def get_session_override():
        yield session

    async def get_redis_override():
        yield redis_client

    app.dependency_overrides[get_async_session] = get_session_override
    app.dependency_overrides[get_async_redis] = get_redis_override

    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def make_user(session: AsyncSession):
    """
    Factory fixture to create a user with a hashed password.
    """
    async def _make_user(
        *,
        full_name="Test User",
        email="user@example.com",
        phone="+212600000000",
        password="StrongPassw0rd!",
        is_active=True,
        is_verified=True,
        is_locked=False,
    ) -> User:
        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password_hash=get_password_hash(password),
            is_active=is_active,
            is_verified=is_verified,
            is_locked=is_locked,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    return _make_user


@pytest_asyncio.fixture
async def make_permission(session: AsyncSession):
    """
    Create (or return existing) Permission(service_name, action, resource).
    Normalizes fields to lowercase.
    """
    async def _make_permission(
            service_name: str,
            action: str,
            resource: str = "*",
    ) -> Permission:
        svc = service_name.strip().lower()
        act = action.strip().lower()
        res = resource.strip().lower() if resource else "*"

        stmt = select(Permission).where(
            Permission.service_name == svc,
            Permission.action == act,
            Permission.resource == res,
        )
        result = await session.execute(stmt)
        perm = result.scalar_one_or_none()
        if perm:
            return perm

        perm = Permission(service_name=svc, action=act, resource=res)
        session.add(perm)
        await session.commit()
        await session.refresh(perm)
        return perm
    return _make_permission


@pytest_asyncio.fixture
async def make_role(session: AsyncSession):
    """
    Create a Role by name (unique). Returns existing if already present.
    """
    async def _make_role(name: str, description: str | None = None) -> Role:
        stmt = select(Role).where(Role.name == name)
        result = await session.execute(stmt)
        role = result.scalar_one_or_none()
        if role:
            return role

        role = Role(name=name, description=description)
        session.add(role)
        await session.commit()
        await session.refresh(role)
        return role
    return _make_role


@pytest_asyncio.fixture
async def grant_permission(session: AsyncSession):
    """
    Attach a permission to a role (idempotent).
    """
    async def _grant(role: Role, permission: Permission) -> None:
        # Check if link exists
        stmt = select(RolePermission).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == permission.id,
        )
        result = await session.execute(stmt)
        rp = result.scalar_one_or_none()
        if not rp:
            session.add(RolePermission(
                role_id=role.id,
                permission_id=permission.id,
            ))
            await session.commit()
    return _grant


@pytest_asyncio.fixture
async def assign_role(session: AsyncSession):
    """
    Assign a role to a user (idempotent).
    """
    async def _assign(user: User, role: Role) -> None:
        # Check if link exists
        stmt = select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id,
        )
        result = await session.execute(stmt)
        ur = result.scalar_one_or_none()
        if not ur:
            session.add(UserRole(user_id=user.id, role_id=role.id))
            await session.commit()
    return _assign


@pytest_asyncio.fixture
async def role_with_perms(make_role, make_permission, grant_permission):
    """
    Create a role and attach the provided list of
    (service, action, resource) tuples.
    Returns the role.
    """
    async def _make(name: str, perms: list[tuple[str, str, str]]):
        role = await make_role(name)
        for svc, act, res in perms:
            perm = await make_permission(svc, act, res)
            await grant_permission(role, perm)
        return role
    return _make


@pytest_asyncio.fixture
async def auth_header(client: httpx.AsyncClient):
    """
    Helper to log a user in and return Authorization header dict.
    Usage: headers = await auth_header("email@example.com", "Password123!")
    """
    async def _header(email: str, password: str) -> dict[str, str]:
        r = await client.post(
            "/api/v1/auth/login",
            json={
                "email": email,
                "password": password
            },
        )
        assert r.status_code == 200, r.text
        token = r.json().get("access_token")
        assert token is not None
        return {"Authorization": f"Bearer {token}"}
    return _header


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "full_name": "Ahmed Hassan",
        "email": "ahmed@example.com",
        "phone": "+212600123456",
        "password": "SecurePassword123!"
    }


@pytest.fixture
def sample_role_data():
    """Sample role data for testing"""
    return {
        "name": "transport_manager",
        "description": "Manager for transport operations"
    }


@pytest.fixture
def sample_permission_data():
    """Sample permission data for testing"""
    return {
        "service_name": "vehicles",
        "action": "read",
        "resource": "all"
    }
