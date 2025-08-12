"""
RBAC integration tests to verify that route guards enforce:
- 401 when no token
- 403 when authenticated but lacking required permission
- 200 when authenticated and permission is granted

We test:
- GET /api/v1/users              (requires auth:read:users)
- POST /api/v1/users             (requires auth:create:users)
"""

from fastapi.testclient import TestClient
from sqlmodel import Session


def test_users_list_requires_auth_token(client: TestClient):
    """
    Without Authorization header, protected routes should return 401.
    """
    r = client.get("/api/v1/users")
    assert r.status_code == 401  # WWW-Authenticate: Bearer


def test_users_list_denied_without_permission(
    client: TestClient,
    session: Session,
    make_user,
    auth_header,
):
    """
    Authenticated user without 'auth:read:users' must be denied.
    Expected status: 403 (Forbidden) if your require_permission returns 403.
    If your implementation returns 401 for missing perms, adjust assertion.
    """
    make_user(email="noperms@example.com", password="Pw123456!!")
    headers = auth_header("noperms@example.com", "Pw123456!!")

    r = client.get("/api/v1/users", headers=headers)
    assert r.status_code in (401, 403)
    # Preferably 403 for "authenticated but not allowed"
    # If it's 401 in your implementation, keep it—just be consistent.


def test_users_list_allowed_with_permission(
    client: TestClient,
    session: Session,
    make_user,
    role_with_perms,
    assign_role,
    auth_header,
):
    """
    User with 'auth:read:users' can list users.
    """
    # Actor with permission
    actor = make_user(email="reader@example.com", password="Pw123456!!")
    role = role_with_perms("reader_role", [("auth", "read", "users")])
    assign_role(actor, role)

    headers = auth_header("reader@example.com", "Pw123456!!")
    r = client.get("/api/v1/users", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_create_user_denied_without_permission(
    client: TestClient,
    make_user,
    auth_header,
):
    """
    User lacking 'auth:create:users' cannot create users.
    """
    make_user(email="no_creator@example.com", password="Pw123456!!")
    headers = auth_header("no_creator@example.com", "Pw123456!!")

    payload = {
        "full_name": "New Guy",
        "email": "newguy@example.com",
        "phone": "+212611111111",
        "password": "StrongPassw0rd!",
        "is_verified": True,
        "must_change_password": False,
    }
    r = client.post("/api/v1/users/", json=payload, headers=headers)
    assert r.status_code in (401, 403)


def test_create_user_allowed_with_permission(
    client: TestClient,
    make_user,
    role_with_perms,
    assign_role,
    auth_header,
):
    """
    User with 'auth:create:users' can create users and receives 200
    with the created users.
    """
    actor = make_user(email="creator@example.com", password="Pw123456!!")
    role = role_with_perms("creator_role", [("auth", "create", "users")])
    assign_role(actor, role)

    headers = auth_header("creator@example.com", "Pw123456!!")

    payload = {
        "full_name": "New Person",
        "email": "newperson@example.com",
        "phone": "+212622222222",
        "password": "StrongPassw0rd!",
        "is_verified": True,
        "must_change_password": False,
    }
    r = client.post("/api/v1/users/", json=payload, headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["email"] == "newperson@example.com"
