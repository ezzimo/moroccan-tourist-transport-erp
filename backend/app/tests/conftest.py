"""
Test configuration and fixtures
"""
from models.permission import Permission
from models.role import Role, RolePermission
from fastapi.testclient import TestClient
from sqlmodel import Session, select
import pytest
import fakeredis
import os
from main import app
from database import get_session, get_redis
from test_database import create_test_db_and_tables, test_engine
from utils.security import get_password_hash
from models.user import User, UserRole


# Test database engine
@pytest.fixture(name="session")
def session_fixture():
    """Create test database session"""
    # Create tables
    create_test_db_and_tables()

    with Session(test_engine) as session:
        yield session

    # Clean up
    if os.path.exists("test_auth.db"):
        os.unlink("test_auth.db")


@pytest.fixture(name="redis_client")
def redis_client_fixture():
    """Create fake Redis client for testing"""
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture(name="client")
def client_fixture(session: Session, redis_client):
    """Create test client with dependency overrides"""
    def get_session_override():
        return session

    def get_redis_override():
        return redis_client

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_redis] = get_redis_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def make_user(session: Session):
    """
    Factory fixture to create a user with a hashed password.
    """
    def _make_user(
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
        session.commit()
        session.refresh(user)
        return user
    return _make_user


@pytest.fixture
def make_permission(session: Session):
    """
    Create (or return existing) Permission(service_name, action, resource).
    Normalizes fields to lowercase.
    """
    def _make_permission(
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
        perm = session.exec(stmt).first()
        if perm:
            return perm

        perm = Permission(service_name=svc, action=act, resource=res)
        session.add(perm)
        session.commit()
        session.refresh(perm)
        return perm
    return _make_permission


@pytest.fixture
def make_role(session: Session):
    """
    Create a Role by name (unique). Returns existing if already present.
    """
    def _make_role(name: str, description: str | None = None) -> Role:
        stmt = select(Role).where(Role.name == name)
        role = session.exec(stmt).first()
        if role:
            return role

        role = Role(name=name, description=description)
        session.add(role)
        session.commit()
        session.refresh(role)
        return role
    return _make_role


@pytest.fixture
def grant_permission(session: Session):
    """
    Attach a permission to a role (idempotent).
    """
    def _grant(role: Role, permission: Permission) -> None:
        # Check if link exists
        stmt = select(RolePermission).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == permission.id,
        )
        rp = session.exec(stmt).first()
        if not rp:
            session.add(RolePermission(
                role_id=role.id,
                permission_id=permission.id,
            ))
            session.commit()
    return _grant


@pytest.fixture
def assign_role(session: Session):
    """
    Assign a role to a user (idempotent).
    """
    def _assign(user: User, role: Role) -> None:
        # Check if link exists
        stmt = select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id,
        )
        ur = session.exec(stmt).first()
        if not ur:
            session.add(UserRole(user_id=user.id, role_id=role.id))
            session.commit()
    return _assign


@pytest.fixture
def role_with_perms(make_role, make_permission, grant_permission):
    """
    Create a role and attach the provided list of
    (service, action, resource) tuples.
    Returns the role.
    """
    def _make(name: str, perms: list[tuple[str, str, str]]):
        role = make_role(name)
        for svc, act, res in perms:
            perm = make_permission(svc, act, res)
            grant_permission(role, perm)
        return role
    return _make


@pytest.fixture
def auth_header(client):
    """
    Helper to log a user in and return Authorization header dict.
    Usage: headers = auth_header("email@example.com", "Password123!")
    """
    def _header(email: str, password: str) -> dict[str, str]:
        r = client.post(
            "/api/v1/auth/login",
            json={
                "email": email,
                "password": password
            },
        )
        assert r.status_code == 200, r.text
        token = r.json()["access_token"]
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
