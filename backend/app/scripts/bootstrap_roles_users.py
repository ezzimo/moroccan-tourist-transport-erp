"""
Bootstrap roles, permissions, and demo users for the auth_service.

- Idempotent (safe to run multiple times)
- Async (uses the service's AsyncSession)
- Uses exact ORM columns from your models:
    Permission(service_name, action, resource)
- Ensures tables exist (create_all) for dev/CI robustness
- Flattens role inheritance at write time (children receive parent perms)
- Logs a compact audit trail to stdout

Run inside the container:
    docker compose exec auth_service python -m scripts.bootstrap_roles_users --commit

Dry-run:
    docker compose exec auth_service python -m scripts.bootstrap_roles_users --dry-run

Environment overrides:
    ADMIN_EMAIL=admin@example.com
    ADMIN_PASSWORD=ChangeMe!123
    DEMO_PASSWORD=Tourist!234
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Iterable, Optional, Set, Tuple, Dict

from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel
from typing import Optional

# --- service internals ---

from utils.security import get_password_hash
from models.permission import Permission
from models.role import Role, RolePermission
from models.user import User, UserRole
from database_async import get_async_session, get_async_engine, init_models


# --------------------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------------------
logger = logging.getLogger("bootstrap")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# --------------------------------------------------------------------------------------
# RBAC Definition (service, action, resource) triplets expected by your codebase/tests.
# Keep names aligned with tests that call require_permission("auth","read","users"), etc.
# --------------------------------------------------------------------------------------

PERMISSIONS: list[dict] = [
    # --- Auth management
    {"service": "auth", "action": "read", "resource": "users"},
    {"service": "auth", "action": "create", "resource": "users"},
    {"service": "auth", "action": "update", "resource": "users"},
    {"service": "auth", "action": "delete", "resource": "users"},
    {"service": "auth", "action": "read", "resource": "roles"},
    {"service": "auth", "action": "create", "resource": "roles"},
    {"service": "auth", "action": "update", "resource": "roles"},
    {"service": "auth", "action": "delete", "resource": "roles"},
    {"service": "auth", "action": "read", "resource": "permissions"},
    {"service": "auth", "action": "assign", "resource": "roles"},
    {"service": "auth", "action": "manage", "resource": "security"},
    # --- CRM management
    {"service": "crm", "action": "read", "resource": "customers"},
    {"service": "crm", "action": "create", "resource": "customers"},
    {"service": "crm", "action": "update", "resource": "customers"},
    {"service": "crm", "action": "delete", "resource": "customers"},
    # --- Customer management
    {"service": "crm", "action": "read", "resource": "interactions"},
    {"service": "crm", "action": "create", "resource": "interactions"},
    {"service": "crm", "action": "update", "resource": "interactions"},
    {"service": "crm", "action": "delete", "resource": "interactions"},
    {"service": "crm", "action": "read", "resource": "feedback"},
    {"service": "crm", "action": "create", "resource": "feedback"},
    {"service": "crm", "action": "update", "resource": "feedback"},
    {"service": "crm", "action": "delete", "resource": "feedback"},
    # --- Fleet management
    {"service": "fleet", "action": "read", "resource": "vehicles"},
    {"service": "fleet", "action": "create", "resource": "vehicles"},
    {"service": "fleet", "action": "update", "resource": "vehicles"},
    {"service": "fleet", "action": "delete", "resource": "vehicles"},
    {"service": "fleet", "action": "read", "resource": "maintenance"},
    {"service": "fleet", "action": "schedule", "resource": "maintenance"},
    {"service": "fleet", "action": "approve", "resource": "maintenance"},
    # --- Route / operations
    {"service": "ops", "action": "read", "resource": "routes"},
    {"service": "ops", "action": "schedule", "resource": "routes"},
    {"service": "ops", "action": "assign", "resource": "drivers"},
    {"service": "ops", "action": "approve", "resource": "trips"},
    {"service": "ops", "action": "cancel", "resource": "trips"},
    # --- Bookings / customer
    {"service": "booking", "action": "read", "resource": "bookings"},
    {"service": "booking", "action": "create", "resource": "bookings"},
    {"service": "booking", "action": "update", "resource": "bookings"},
    {"service": "booking", "action": "cancel", "resource": "bookings"},
    # --- Finance
    {"service": "finance", "action": "read", "resource": "pricing"},
    {"service": "finance", "action": "update", "resource": "pricing"},
    {"service": "finance", "action": "read", "resource": "invoices"},
    {"service": "finance", "action": "create", "resource": "invoices"},
    {"service": "finance", "action": "process", "resource": "payments"},
    # --- Reporting
    {"service": "reports", "action": "read", "resource": "dashboards"},
    {"service": "reports", "action": "export", "resource": "data"},
]

PERM_KEY = lambda p: (p["service"], p["action"], p["resource"])


# --------------------------------------------------------------------------------------
# Roles (with inheritance): permissions are flattened when persisted.
# Keep "auth:read:users" on roles used by tests (e.g. 'Reader').
# --------------------------------------------------------------------------------------

ROLES: dict[str, dict] = {
    # C-level
    "CEO": {
        "description": "Chief Executive Officer with full enterprise visibility",
        "parents": ["Admin"],
        "permissions": [
            ("reports", "read", "dashboards"),
            ("reports", "export", "data"),
        ],
    },
    "CFO": {
        "description": "Chief Financial Officer with finance and reporting powers",
        "parents": [],
        "permissions": [
            ("finance", "read", "pricing"),
            ("finance", "update", "pricing"),
            ("finance", "read", "invoices"),
            ("finance", "create", "invoices"),
            ("finance", "process", "payments"),
            ("reports", "read", "dashboards"),
        ],
    },
    "CTO": {
        "description": "Chief Technology Officer with security & auth management",
        "parents": ["Admin"],
        "permissions": [
            ("auth", "manage", "security"),
            ("reports", "read", "dashboards"),
        ],
    },
    # Admin / System roles
    "Admin": {
        "description": "System administrator with full user/role control",
        "parents": [],
        "permissions": [
            ("auth", "read", "users"),
            ("auth", "create", "users"),
            ("auth", "update", "users"),
            ("auth", "delete", "users"),
            ("auth", "read", "roles"),
            ("auth", "create", "roles"),
            ("auth", "update", "roles"),
            ("auth", "delete", "roles"),
            ("auth", "read", "permissions"),
            ("auth", "assign", "roles"),
            ("auth", "assign", "permissions"),
            ("auth", "read", "permissions"),
            ("auth", "create", "permissions"),
            ("auth", "update", "permissions"),
            ("auth", "delete", "permissions"),
            ("auth", "read", "roles"),
            ("crm", "read", "customers"),
            ("crm", "create", "customers"),
            ("crm", "update", "customers"),
            ("crm", "delete", "customers"),
            ("fleet", "read", "vehicles"),
            ("fleet", "create", "vehicles"),
            ("fleet", "update", "vehicles"),
            ("fleet", "delete", "vehicles"),
            ("fleet", "read", "maintenance"),
            ("fleet", "schedule", "maintenance"),
            ("fleet", "approve", "maintenance"),
            ("ops", "read", "routes"),
            ("ops", "schedule", "routes"),
            ("ops", "assign", "drivers"),
            ("ops", "approve", "trips"),
            ("booking", "read", "bookings"),
            ("booking", "create", "bookings"),
            ("booking", "update", "bookings"),
            ("booking", "cancel", "bookings"),
            ("reports", "read", "dashboards"),
            ("reports", "export", "data"),
        ],
    },
    # Management tiers
    "Regional Manager": {
        "description": "Manages regional operations, fleet and routes",
        "parents": [],
        "permissions": [
            ("fleet", "read", "vehicles"),
            ("fleet", "update", "vehicles"),
            ("fleet", "read", "maintenance"),
            ("fleet", "schedule", "maintenance"),
            ("ops", "read", "routes"),
            ("ops", "schedule", "routes"),
            ("ops", "assign", "drivers"),
            ("ops", "approve", "trips"),
            ("booking", "read", "bookings"),
            ("reports", "read", "dashboards"),
        ],
    },
    "Fleet Manager": {
        "description": "Manages fleet and maintenance",
        "parents": [],
        "permissions": [
            ("fleet", "read", "vehicles"),
            ("fleet", "create", "vehicles"),
            ("fleet", "update", "vehicles"),
            ("fleet", "delete", "vehicles"),
            ("fleet", "read", "maintenance"),
            ("fleet", "schedule", "maintenance"),
            ("fleet", "approve", "maintenance"),
            ("reports", "read", "dashboards"),
        ],
    },
    "Operations Supervisor": {
        "description": "Supervises routes, scheduling and trip approvals",
        "parents": [],
        "permissions": [
            ("ops", "read", "routes"),
            ("ops", "schedule", "routes"),
            ("ops", "assign", "drivers"),
            ("ops", "approve", "trips"),
            ("booking", "read", "bookings"),
        ],
    },
    # Operational staff
    "Dispatcher": {
        "description": "Handles daily dispatch and route assignments",
        "parents": [],
        "permissions": [
            ("ops", "read", "routes"),
            ("ops", "assign", "drivers"),
            ("booking", "read", "bookings"),
            ("booking", "update", "bookings"),
            ("ops", "cancel", "trips"),
        ],
    },
    "Maintenance Coordinator": {
        "description": "Schedules and tracks maintenance work",
        "parents": [],
        "permissions": [
            ("fleet", "read", "maintenance"),
            ("fleet", "schedule", "maintenance"),
        ],
    },
    "Customer Service": {
        "description": "Manages bookings and customer requests",
        "parents": [],
        "permissions": [
            ("booking", "read", "bookings"),
            ("booking", "create", "bookings"),
            ("booking", "update", "bookings"),
            ("booking", "cancel", "bookings"),
        ],
    },
    # Field personnel
    "Driver": {
        "description": "Access to assigned routes/trips only",
        "parents": [],
        "permissions": [
            ("ops", "read", "routes"),
        ],
    },
    "Tour Guide": {
        "description": "Access to route info and customer manifests where allowed",
        "parents": [],
        "permissions": [
            ("ops", "read", "routes"),
            ("booking", "read", "bookings"),
        ],
    },
    "Maintenance Technician": {
        "description": "Executes maintenance tasks with read access",
        "parents": [],
        "permissions": [
            ("fleet", "read", "maintenance"),
        ],
    },
    # Finance & Reporting
    "Finance Manager": {
        "description": "Manages pricing, invoices and payments",
        "parents": ["CFO"],  # inherits CFO perms (flattened)
        "permissions": [],
    },
    "Reader": {
        "description": "Read-only access for audits and tests",
        "parents": [],
        "permissions": [
            # IMPORTANT for tests:
            ("auth", "read", "users"),
        ],
    },
}

# --------------------------------------------------------------------------------------
# Demo users
# --------------------------------------------------------------------------------------
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ChangeMe!123")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "Tourist!234")

USERS: list[dict] = [
    {
        "full_name": "System Admin",
        "email": ADMIN_EMAIL,
        "phone": "+212600000001",
        "roles": ["Admin"],
        "is_verified": True,
    },
    {
        "full_name": "Regional Boss",
        "email": "regional.manager@example.com",
        "phone": "+212600000010",
        "roles": ["Regional Manager"],
        "is_verified": True,
    },
    {
        "full_name": "Fleet Lead",
        "email": "fleet.manager@example.com",
        "phone": "+212600000020",
        "roles": ["Fleet Manager"],
        "is_verified": True,
    },
    {
        "full_name": "Dispatch Pro",
        "email": "dispatcher@example.com",
        "phone": "+212600000030",
        "roles": ["Dispatcher"],
        "is_verified": True,
    },
    {
        "full_name": "Ops Supervisor",
        "email": "ops.supervisor@example.com",
        "phone": "+212600000040",
        "roles": ["Operations Supervisor"],
        "is_verified": True,
    },
    {
        "full_name": "Finance Boss",
        "email": "finance.manager@example.com",
        "phone": "+212600000050",
        "roles": ["Finance Manager"],
        "is_verified": True,
    },
    {
        "full_name": "CS Agent",
        "email": "customer.service@example.com",
        "phone": "+212600000060",
        "roles": ["Customer Service"],
        "is_verified": True,
    },
    {
        "full_name": "Driver One",
        "email": "driver@example.com",
        "phone": "+212600000070",
        "roles": ["Driver"],
        "is_verified": True,
    },
    {
        "full_name": "Guide One",
        "email": "tour.guide@example.com",
        "phone": "+212600000080",
        "roles": ["Tour Guide"],
        "is_verified": True,
    },
    {
        "full_name": "Tech One",
        "email": "maintenance.tech@example.com",
        "phone": "+212600000090",
        "roles": ["Maintenance Technician"],
        "is_verified": True,
    },
    {
        "full_name": "Read Only",
        "email": "reader@example.com",
        "phone": "+212600000099",
        "roles": ["Reader"],
        "is_verified": True,
    },
]


# --------------------------------------------------------------------------------------
# Helpers (exact field usage, no guessing)
# --------------------------------------------------------------------------------------


async def _ensure_tables_exist() -> None:
    """
    Ensure all SQLModel tables exist before seeding.
    Uses your project's init_models() which calls SQLModel.metadata.create_all
    on the async engine.
    """
    await init_models()


async def ensure_permission(
    session: AsyncSession,
    service: str,
    action: str,
    resource: str,
    description: Optional[str] = None,  # ignored (model has no description field)
) -> Permission:
    """
    Idempotently ensure a Permission row exists using your model's exact fields:
      - Permission.service_name
      - Permission.action
      - Permission.resource

    NOTE: Your current Permission model does NOT have 'description' — it is ignored.
    """
    stmt = select(Permission).where(
        Permission.service_name == service,
        Permission.action == action,
        Permission.resource == resource,
    )
    res = await session.execute(stmt)
    perm = res.scalar_one_or_none()

    if perm:
        return perm

    perm = Permission(
        service_name=service,
        action=action,
        resource=resource,
    )
    session.add(perm)
    await session.flush()
    logger.info("  + permission %s:%s:%s", service, action, resource)
    return perm


async def ensure_role(
    session: AsyncSession, name: str, description: Optional[str] = None
) -> Role:
    res = await session.execute(select(Role).where(Role.name == name))
    role = res.scalar_one_or_none()
    if role:
        # If description exists on your Role model (it does), set it only if empty
        if description and (role.description is None or role.description.strip() == ""):
            role.description = description
        return role

    role = Role(name=name, description=description)
    session.add(role)
    await session.flush()
    logger.info("  + role %s", name)
    return role


async def attach_role_to_user(session: AsyncSession, user: User, role: Role) -> None:
    """Attach role to user without touching user.roles (avoids lazy load in async)."""
    # If you have a mapped class:
    exists_stmt = select(UserRole).where(
        UserRole.user_id == user.id,
        UserRole.role_id == role.id,
    )
    res = await session.execute(exists_stmt)
    link = res.scalar_one_or_none()
    if link:
        return

    session.add(UserRole(user_id=user.id, role_id=role.id))
    await session.flush()
    logger.info("    -> attach role %s to user %s", role.name, user.email)


async def attach_permission(session, role, perm) -> None:
    # Do NOT touch role.permissions (will lazy-load). Check link directly:
    exists_stmt = select(RolePermission).where(
        RolePermission.role_id == role.id,
        RolePermission.permission_id == perm.id,
    )
    res = await session.execute(exists_stmt)
    link = res.scalar_one_or_none()
    if link:
        return

    # Create association row explicitly
    session.add(RolePermission(role_id=role.id, permission_id=perm.id))
    await session.flush()
    logger.info(
        "    -> attach perm %s:%s:%s to role %s",
        perm.service_name, perm.action, perm.resource, role.name,
    )


async def ensure_user(
    session: AsyncSession,
    *,
    full_name: str,
    email: str,
    phone: str,
    password_plain: str,
    roles: list[Role],
    is_verified: bool = True,
) -> User:
    # Optionally eager-load roles if you still want to read them later without lazy I/O:
    res = await session.execute(
        select(User).where(User.email == email)  # .options(selectinload(User.roles))
    )
    user = res.scalar_one_or_none()

    if user:
        await session.refresh(user)  # refresh columns only (no relationships)
        # Attach requested roles via join table, no access to user.roles
        for r in roles:
            await attach_role_to_user(session, user, r)
        await session.flush()
        return user

    # Create new user
    hashed = get_password_hash(password_plain)
    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        password_hash=hashed,
        is_active=True,
        is_verified=is_verified,
    )
    session.add(user)
    await session.flush()   # ensures user.id is available

    # Link roles via join table (no relationship access)
    for r in roles:
        await attach_role_to_user(session, user, r)

    await session.flush()
    logger.info("  + user %s", email)
    return user


def _collect_role_perms(
    role_key: str, visited: Optional[Set[str]] = None
) -> Set[Tuple[str, str, str]]:
    """Resolve flattened permissions for a role, following parents recursively."""
    if visited is None:
        visited = set()
    if role_key in visited:
        return set()
    visited.add(role_key)

    spec = ROLES[role_key]
    perms: Set[Tuple[str, str, str]] = set(spec.get("permissions", []))
    for parent in spec.get("parents", []):
        perms |= _collect_role_perms(parent, visited)
    return perms


# --------------------------------------------------------------------------------------
# Bootstrap flow
# --------------------------------------------------------------------------------------


async def bootstrap(*, commit: bool = False) -> None:
    # 1) Ensure tables exist
    await _ensure_tables_exist()

    # 2) Use a real async session; commit or rollback as requested
    async for session in get_async_session():
        # Wrap in a transaction
        async with session.begin():
            logger.info("Seeding permissions…")

            # Build the permission map
            perm_map: dict[tuple[str, str, str], Permission] = {}
            for p in PERMISSIONS:
                perm = await ensure_permission(
                    session,
                    p["service"],
                    p["action"],
                    p["resource"],
                    p.get("description"),
                )
                perm_map[(p["service"], p["action"], p["resource"])] = perm

            logger.info("Seeding roles (with flattened inheritance)…")
            role_map: dict[str, Role] = {}

            # Ensure roles exist
            for role_name, spec in ROLES.items():
                role = await ensure_role(session, role_name, spec.get("description"))
                role_map[role_name] = role

            # Attach permissions (flattened via parents)
            for role_name, role in role_map.items():
                flat_perms = _collect_role_perms(role_name)
                for svc, act, res in flat_perms:
                    perm = perm_map.get((svc, act, res))
                    if perm is None:
                        perm = await ensure_permission(session, svc, act, res)
                    await attach_permission(session, role, perm)

            logger.info("Seeding demo users…")
            for user_spec in USERS:
                roles = [role_map[rn] for rn in user_spec["roles"] if rn in role_map]
                await ensure_user(
                    session,
                    full_name=user_spec["full_name"],
                    email=user_spec["email"],
                    phone=user_spec["phone"],
                    password_plain=(
                        ADMIN_PASSWORD
                        if "Admin" in user_spec["roles"]
                        else DEMO_PASSWORD
                    ),
                    roles=roles,
                    is_verified=user_spec.get("is_verified", True),
                )

            if commit:
                logger.info("COMMIT ✅")
            else:
                logger.info("DRY-RUN (rollback) 🧪")
                raise RuntimeError("DRY_RUN_REQUESTED")

        # If we reach here without exception, changes were committed
        return


async def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Bootstrap roles, permissions, and demo users."
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--commit", action="store_true", help="Apply changes")
    g.add_argument(
        "--dry-run", action="store_true", help="Preview changes without committing"
    )
    args = parser.parse_args()

    try:
        await bootstrap(commit=bool(args.commit))
    except RuntimeError as e:
        if str(e) == "DRY_RUN_REQUESTED" and args.dry_run:
            logger.info("Rollback complete (dry-run).")
        else:
            logger.error("Bootstrap failed: %s", e)
            raise


if __name__ == "__main__":
    asyncio.run(_main())
