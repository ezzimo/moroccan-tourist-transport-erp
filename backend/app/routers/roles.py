"""
Role and Permission management routes (async, services threadpool-backed)
"""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from services.role_service import RoleService
from schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleWithPermissions,
    PermissionCreate,
    PermissionResponse,
)
from utils.dependencies import require_permission
import uuid

router = APIRouter(prefix="/roles", tags=["Role Management"])


@router.post("/", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "create", "roles")),
):
    role_service = RoleService(session)
    return await role_service.create_role(role_data)


@router.get("/", response_model=list[RoleWithPermissions])
async def get_roles(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "read", "roles")),
):
    role_service = RoleService(session)
    return await role_service.get_roles(skip=skip, limit=limit)


@router.get("/{role_id}", response_model=RoleWithPermissions)
async def get_role(
    role_id: uuid.UUID,
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "read", "roles")),
):
    role_service = RoleService(session)
    return await role_service.get_role(role_id)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: uuid.UUID,
    role_data: RoleUpdate,
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "update", "roles")),
):
    role_service = RoleService(session)
    return await role_service.update_role(role_id, role_data)


@router.delete("/{role_id}")
async def delete_role(
    role_id: uuid.UUID,
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "delete", "roles")),
):
    role_service = RoleService(session)
    return await role_service.delete_role(role_id)


@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreate,
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "create", "permissions")),
):
    role_service = RoleService(session)
    return await role_service.create_permission(permission_data)


@router.get("/permissions", response_model=list[PermissionResponse])
async def get_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "read", "permissions")),
):
    role_service = RoleService(session)
    return await role_service.get_permissions(skip=skip, limit=limit)


@router.delete("/permissions/{permission_id}")
async def delete_permission(
    permission_id: uuid.UUID,
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "delete", "permissions")),
):
    role_service = RoleService(session)
    return await role_service.delete_permission(permission_id)
