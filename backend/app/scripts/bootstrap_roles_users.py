"""
Bootstrap roles, permissions, and demo users for the auth_service.

- Idempotent (safe to run multiple times)
- Async (uses the service's AsyncSession)
- Domain-aware for Moroccan Tourist Transport ERP
- Flattens role inheritance at write time (children receive parent perms)
- Uses existing models (User, Role, Permission) and relationships
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
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Service internals
from database_async import get_async_session
from utils.security import get_password_hash
from models.permission import Permission
from models.role import Role
from models.user import User

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
    {
        "service": "auth",
        "action": "read",
        "resource": "users",
        "description": "List and read users",
    },
    {
        "service": "auth",
        "action": "create",
        "resource": "users",
        "description": "Create users",
    },
    {
        "service": "auth",
        "action": "update",
        "resource": "users",
        "description": "Update users",
    },
    {
        "service": "auth",
        "action": "delete",
        "resource": "users",
        "description": "Delete users",
    },
    {
        "service": "auth",
        "action": "read",
        "resource": "roles",
        "description": "List and read roles",
    },
    {
        "service": "auth",
        "action": "create",
        "resource": "roles",
        "description": "Create roles",
    },
    {
        "service": "auth",
        "action": "update",
        "resource": "roles",
        "description": "Update roles",
    },
    {
        "service": "auth",
        "action": "delete",
        "resource": "roles",
        "description": "Delete roles",
    },
    {
        "service": "auth",
        "action": "read",
        "resource": "permissions",
        "description": "List and read permissions",
    },
    {
        "service": "auth",
        "action": "assign",
        "resource": "roles",
        "description": "Assign roles to users",
    },
    {
        "service": "auth",
        "action": "manage",
        "resource": "security",
        "description": "Security operations (blacklist/logout/OTP policy)",
    },
    # --- Fleet management
    {
        "service": "fleet",
        "action": "read",
        "resource": "vehicles",
        "description": "View vehicles",
    },
    {
        "service": "fleet",
        "action": "create",
        "resource": "vehicles",
        "description": "Add vehicles",
    },
    {
        "service": "fleet",
        "action": "update",
        "resource": "vehicles",
        "description": "Update vehicles",
    },
    {
        "service": "fleet",
        "action": "delete",
        "resource": "vehicles",
        "description": "Remove vehicles",
    },
    {
        "service": "fleet",
        "action": "read",
        "resource": "maintenance",
        "description": "View maintenance records",
    },
    {
        "service": "fleet",
        "action": "schedule",
        "resource": "maintenance",
        "description": "Schedule maintenance",
    },
    {
        "service": "fleet",
        "action": "approve",
        "resource": "maintenance",
        "description": "Approve maintenance",
    },
    # --- Route / operations
    {
        "service": "ops",
        "action": "read",
        "resource": "routes",
        "description": "View routes",
    },
    {
        "service": "ops",
        "action": "schedule",
        "resource": "routes",
        "description": "Schedule routes",
    },
    {
        "service": "ops",
        "action": "assign",
        "resource": "drivers",
        "description": "Assign drivers",
    },
    {
        "service": "ops",
        "action": "approve",
        "resource": "trips",
        "description": "Approve trips",
    },
    {
        "service": "ops",
        "action": "cancel",
        "resource": "trips",
        "description": "Cancel trips",
    },
    # --- Bookings / customer
    {
        "service": "booking",
        "action": "read",
        "resource": "bookings",
        "description": "View bookings",
    },
    {
        "service": "booking",
        "action": "create",
        "resource": "bookings",
        "description": "Create bookings",
    },
    {
        "service": "booking",
        "action": "update",
        "resource": "bookings",
        "description": "Modify bookings",
    },
    {
        "service": "booking",
        "action": "cancel",
        "resource": "bookings",
        "description": "Cancel bookings",
    },
    # --- Finance
    {
        "service": "finance",
        "action": "read",
        "resource": "pricing",
        "description": "View pricing/tariffs",
    },
    {
        "service": "finance",
        "action": "update",
        "resource": "pricing",
        "description": "Modify rates",
    },
    {
        "service": "finance",
        "action": "read",
        "resource": "invoices",
        "description": "View invoices",
    },
    {
        "service": "finance",
        "action": "create",
        "resource": "invoices",
        "description": "Issue invoices",
    },
    {
        "service": "finance",
        "action": "process",
        "resource": "payments",
        "description": "Process payments",
    },
    # --- Reporting
    {
        "service": "reports",
        "action": "read",
        "resource": "dashboards",
        "description": "View dashboards",
    },
    {
        "service": "reports",
        "action": "export",
        "resource": "data",
        "description": "Export data",
    },
]

# Map for quick lookup by (service, action, resource)
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
# Demo users (OPTIONAL). Adjust emails/passwords via env variables as needed.
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
# Helpers (idempotent upserts)
# --------------------------------------------------------------------------------------


def _resolve_permission_columns():
    """
    Map to the actual ORM column attributes regardless of naming differences.
    Expected columns: service (aka domain/namespace/module), action, resource.
    Optionally: description.
    """
    svc_col = (
        getattr(Permission, "service", None)
        or getattr(Permission, "domain", None)
        or getattr(Permission, "namespace", None)
        or getattr(Permission, "module", None)
    )
    act_col = getattr(Permission, "action", None) or getattr(Permission, "verb", None)
    res_col = (
        getattr(Permission, "resource", None)
        or getattr(Permission, "entity", None)
        or getattr(Permission, "object", None)
    )
    if not (svc_col and act_col and res_col):
        raise RuntimeError(
            "Permission ORM model does not expose expected columns "
            "(service/domain/namespace/module, action/verb, "
            "resource/entity/object). "
            "Verify you imported the ORM model, not a Pydantic schema."
        )
    desc_col = getattr(Permission, "description", None)  # optional
    return svc_col, act_col, res_col, desc_col


def _build_permission_kwargs(
    service: str, action: str, resource: str, description: str | None
) -> dict:
    """
    Build constructor kwargs matching the ORM model's field names.
    """
    kwargs: dict = {}
    # figure actual column names on the class
    svc_name = (
        "service"
        if hasattr(Permission, "service")
        else "domain"
        if hasattr(Permission, "domain")
        else "namespace"
        if hasattr(Permission, "namespace")
        else "module"
        if hasattr(Permission, "module")
        else None
    )
    act_name = (
        "action"
        if hasattr(Permission, "action")
        else "verb"
        if hasattr(Permission, "verb")
        else None
    )
    res_name = (
        "resource"
        if hasattr(Permission, "resource")
        else "entity"
        if hasattr(Permission, "entity")
        else "object"
        if hasattr(Permission, "object")
        else None
    )

    if not (svc_name and act_name and res_name):
        raise RuntimeError(
            "Could not determine Permission constructor field names; "
            "check the ORM model fields."
        )

    kwargs[svc_name] = service
    kwargs[act_name] = action
    kwargs[res_name] = resource

    if description is not None and hasattr(Permission, "description"):
        kwargs["description"] = description

    return kwargs


async def ensure_permission(
    session: AsyncSession,
    service: str,
    action: str,
    resource: str,
    description: str | None = None,
) -> Permission:
    """
    Idempotently ensure a Permission row exists for (service, action, resource).
    - Works with naming variants (service/domain/namespace/module, action/verb, resource/entity/object).
    - Optionally updates description if the column exists and is empty.
    """
    svc_col, act_col, res_col, desc_col = _resolve_permission_columns()

    # Look up existing
    result = await session.execute(
        select(Permission).where(
            svc_col == service,
            act_col == action,
            res_col == resource,
        )
    )
    perm: Permission | None = result.scalar_one_or_none()

    if perm:
        # Only set description if column exists and it's currently empty
        if description and desc_col is not None:
            current = getattr(perm, "description", None)
            if not current:
                setattr(perm, "description", description)
        return perm

    # Create new
    kwargs = _build_permission_kwargs(service, action, resource, description)
    perm = Permission(**kwargs)
    session.add(perm)
    await session.flush()  # get PKs if needed by callers

    try:
        logger.info(
            "  + permission %s:%s:%s",
            service,
            action,
            resource,
        )
    except Exception:
        pass

    return perm


async def ensure_role(
    session: AsyncSession, name: str, description: Optional[str] = None
) -> Role:
    res = await session.execute(select(Role).where(Role.name == name))
    role = res.scalar_one_or_none()
    if role:
        if (
            description
            and getattr(role, "description", None) in (None, "")
            and hasattr(role, "description")
        ):
            role.description = description
        return role

    role = Role(name=name)
    if description and hasattr(role, "description"):
        role.description = description
    session.add(role)
    await session.flush()
    logger.info("  + role %s", name)
    return role


async def attach_permission(
    session: AsyncSession, role: Role, perm: Permission
) -> None:
    # relies on Role.permissions relationship; avoids duplicates
    await session.refresh(role)
    perms = set(
        (p.service, p.action, p.resource) for p in getattr(role, "permissions", [])
    )
    key = (perm.service, perm.action, perm.resource)
    if key in perms:
        return
    getattr(role, "permissions").append(perm)
    await session.flush()
    logger.info(
        "    -> attach perm %s:%s:%s to role %s",
        perm.service,
        perm.action,
        perm.resource,
        role.name,
    )


async def ensure_user(
    session: AsyncSession,
    *,
    full_name: str,
    email: str,
    phone: str,
    password_plain: str,
    roles: Iterable[Role],
    is_verified: bool = True,
) -> User:
    res = await session.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()
    if user:
        # idempotent: ensure role membership
        await session.refresh(user)
        assigned = {r.name for r in getattr(user, "roles", [])}
        for r in roles:
            if r.name not in assigned:
                getattr(user, "roles").append(r)
                logger.info("    -> attach role %s to user %s", r.name, email)
        await session.flush()
        return user

    hashed = get_password_hash(password_plain)
    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        password_hash=(
            hashed if hasattr(User, "password_hash") else hashed
        ),  # your model likely uses password_hash
        is_active=True,
        is_verified=is_verified,
    )
    # Fallback if model uses `hashed_password` instead:
    if hasattr(user, "hashed_password") and not hasattr(user, "password_hash"):
        user.hashed_password = hashed

    session.add(user)
    await session.flush()
    # attach roles
    await session.refresh(user)
    for r in roles:
        getattr(user, "roles").append(r)
        logger.info("    -> attach role %s to user %s", r.name, email)
    await session.flush()
    logger.info("  + user %s", email)
    return user


def _collect_role_perms(
    role_key: str, visited: Optional[set[str]] = None
) -> set[tuple[str, str, str]]:
    """Resolve flattened permissions for a role, following parents recursively."""
    if visited is None:
        visited = set()
    if role_key in visited:
        return set()
    visited.add(role_key)

    spec = ROLES[role_key]
    perms = set(spec.get("permissions", []))
    for parent in spec.get("parents", []):
        perms |= _collect_role_perms(parent, visited)
    return perms


async def bootstrap(*, commit: bool = False) -> None:
    # Read-only session if not committing? We still need a real session, but we’ll roll back at the end if dry-run.
    async for session in get_async_session():
        # Wrap all changes in a single transaction:
        async with session.begin():
            logger.info("Seeding permissions…")
            # Create all base permissions first
            perm_map: dict[tuple[str, str, str], Permission] = {}
            for p in PERMISSIONS:
                perm = await ensure_permission(
                    session,
                    p["service"],
                    p["action"],
                    p["resource"],
                    p.get("description"),
                )
                perm_map[PERM_KEY(p)] = perm

            logger.info("Seeding roles (with flattened inheritance)…")
            role_map: dict[str, Role] = {}
            # Ensure all roles exist
            for role_name, spec in ROLES.items():
                role = await ensure_role(session, role_name, spec.get("description"))
                role_map[role_name] = role

            # Attach permissions (flattened via parents)
            for role_name, role in role_map.items():
                flat_perms = _collect_role_perms(role_name)
                # ensure the referenced perms exist in perm_map
                for svc, act, res in flat_perms:
                    # If a perm wasn't declared explicitly in PERMISSIONS, create it now to stay robust
                    if (svc, act, res) not in perm_map:
                        perm_map[(svc, act, res)] = await ensure_permission(
                            session, svc, act, res
                        )
                    await attach_permission(session, role, perm_map[(svc, act, res)])

            logger.info("Seeding demo users…")
            # Build role lookup for assignments
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

            # Commit or rollback based on flag
            if commit:
                logger.info("COMMIT ✅")
            else:
                logger.info("DRY-RUN (rollback) 🧪")
                raise RuntimeError("DRY_RUN_REQUESTED")

        # If we get here, transaction was committed (no exception)
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
        # DRY_RUN_REQUESTED triggers rollback path
        if str(e) == "DRY_RUN_REQUESTED" and args.dry_run:
            logger.info("Rollback complete (dry-run).")
        else:
            logger.error("Bootstrap failed: %s", e)
            raise


if __name__ == "__main__":
    asyncio.run(_main())
