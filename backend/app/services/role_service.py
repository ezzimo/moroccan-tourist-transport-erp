"""
Role and Permission service for RBAC operations (async API, threadpool-backed)
"""

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from models.role import Role, RolePermission
from models.permission import Permission
from schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleWithPermissions,
    PermissionCreate,
    PermissionResponse,
)
from datetime import datetime
import uuid


class RoleService:
    def __init__(self, session: Session):
        self.session = session

    # Public async wrappers
    async def create_role(self, role_data: RoleCreate) -> RoleResponse:
        return await run_in_threadpool(self._create_role_sync, role_data)

    async def get_role(self, role_id: uuid.UUID) -> RoleWithPermissions:
        return await run_in_threadpool(self._get_role_sync, role_id)

    async def get_roles(
        self, skip: int = 0, limit: int = 100
    ) -> list[RoleWithPermissions]:
        return await run_in_threadpool(self._get_roles_sync, skip, limit)

    async def update_role(
        self, role_id: uuid.UUID, role_data: RoleUpdate
    ) -> RoleResponse:
        return await run_in_threadpool(self._update_role_sync, role_id, role_data)

    async def delete_role(self, role_id: uuid.UUID) -> dict:
        return await run_in_threadpool(self._delete_role_sync, role_id)

    async def create_permission(
        self, permission_data: PermissionCreate
    ) -> PermissionResponse:
        return await run_in_threadpool(self._create_permission_sync, permission_data)

    async def get_permissions(
        self, skip: int = 0, limit: int = 100
    ) -> list[PermissionResponse]:
        return await run_in_threadpool(self._get_permissions_sync, skip, limit)

    async def delete_permission(self, permission_id: uuid.UUID) -> dict:
        return await run_in_threadpool(self._delete_permission_sync, permission_id)

    # Internal sync implementations
    def _create_role_sync(self, role_data: RoleCreate) -> RoleResponse:
        statement = select(Role).where(Role.name == role_data.name)
        existing_role = self.session.exec(statement).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already exists",
            )

        role = Role(name=role_data.name, description=role_data.description)
        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)

        if role_data.permission_ids:
            self._assign_permissions(role.id, role_data.permission_ids)

        return RoleResponse.model_validate(role)

    def _get_role_sync(self, role_id: uuid.UUID) -> RoleWithPermissions:
        statement = select(Role).where(Role.id == role_id)
        role = self.session.exec(statement).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        return RoleWithPermissions.model_validate(role)

    def _get_roles_sync(self, skip: int, limit: int) -> list[RoleWithPermissions]:
        statement = (
            select(Role)
            .options(selectinload(Role.permissions))
            .offset(skip)
            .limit(limit)
        )
        roles = self.session.exec(statement).all()
        return [RoleWithPermissions.model_validate(role) for role in roles]

    def _update_role_sync(
        self, role_id: uuid.UUID, role_data: RoleUpdate
    ) -> RoleResponse:
        statement = select(Role).where(Role.id == role_id)
        role = self.session.exec(statement).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        update_data = role_data.model_dump(exclude_unset=True)
        permission_ids = update_data.pop("permission_ids", None)

        for field, value in update_data.items():
            setattr(role, field, value)

        role.updated_at = datetime.utcnow()

        if permission_ids is not None:
            self._assign_permissions(role_id, permission_ids)

        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)
        return RoleResponse.model_validate(role)

    def _delete_role_sync(self, role_id: uuid.UUID) -> dict:
        statement = select(Role).where(Role.id == role_id)
        role = self.session.exec(statement).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        self.session.delete(role)
        self.session.commit()
        return {"message": "Role deleted successfully"}

    def _create_permission_sync(
        self, permission_data: PermissionCreate
    ) -> PermissionResponse:
        statement = select(Permission).where(
            Permission.service_name == permission_data.service_name,
            Permission.action == permission_data.action,
            Permission.resource == permission_data.resource,
        )
        existing_permission = self.session.exec(statement).first()
        if existing_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already exists",
            )

        permission = Permission(**permission_data.model_dump())
        self.session.add(permission)
        self.session.commit()
        self.session.refresh(permission)
        return PermissionResponse.model_validate(permission)

    def _get_permissions_sync(self, skip: int, limit: int) -> list[PermissionResponse]:
        statement = select(Permission).offset(skip).limit(limit)
        permissions = self.session.exec(statement).all()
        return [PermissionResponse.model_validate(perm) for perm in permissions]

    def _delete_permission_sync(self, permission_id: uuid.UUID) -> dict:
        statement = select(Permission).where(Permission.id == permission_id)
        permission = self.session.exec(statement).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
            )
        self.session.delete(permission)
        self.session.commit()
        return {"message": "Permission deleted successfully"}

    def _assign_permissions(
        self, role_id: uuid.UUID, permission_ids: list[uuid.UUID]
    ) -> None:
        statement = select(RolePermission).where(RolePermission.role_id == role_id)
        existing_permissions = self.session.exec(statement).all()
        for perm in existing_permissions:
            self.session.delete(perm)

        for permission_id in permission_ids:
            perm_statement = select(Permission).where(Permission.id == permission_id)
            permission = self.session.exec(perm_statement).first()
            if permission:
                self.session.add(
                    RolePermission(role_id=role_id, permission_id=permission_id)
                )

        self.session.commit()
