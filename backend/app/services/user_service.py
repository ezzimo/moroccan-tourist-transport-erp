"""
User service for user management operations (async API, threadpool-backed)
"""

from sqlmodel import Session, select, and_, or_, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from models.user import User, UserRole
from models.role import Role
from models.activity_log import ActivityLog, ActivityActions, ActivityResources
from schemas.user import UserCreate, UserUpdate, UserResponse, UserWithRoles
from utils.security import get_password_hash, generate_random_password
from typing import Optional
from datetime import datetime
import uuid


class UserSearchFilters:
    def __init__(
        self,
        search: Optional[str] = None,
        role_ids: Optional[list[uuid.UUID]] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        is_locked: Optional[bool] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        last_login_after: Optional[datetime] = None,
        last_login_before: Optional[datetime] = None,
        include_deleted: bool = False,
    ):
        self.search = search
        self.role_ids = role_ids or []
        self.is_active = is_active
        self.is_verified = is_verified
        self.is_locked = is_locked
        self.created_after = created_after
        self.created_before = created_before
        self.last_login_after = last_login_after
        self.last_login_before = last_login_before
        self.include_deleted = include_deleted


class UserService:
    def __init__(self, session: Session):
        self.session = session

    # -------------------- Public async wrappers --------------------

    async def create_user(
        self, user_data: UserCreate, actor_id: Optional[uuid.UUID] = None
    ) -> UserResponse:
        return await run_in_threadpool(self._create_user_sync, user_data, actor_id)

    async def get_user(self, user_id: uuid.UUID) -> UserWithRoles:
        return await run_in_threadpool(self._get_user_sync, user_id)

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[UserResponse]:
        return await run_in_threadpool(self._get_users_sync, skip, limit)

    async def search_users(
        self,
        filters: UserSearchFilters,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> dict[str, object]:
        return await run_in_threadpool(
            self._search_users_sync, filters, skip, limit, sort_by, sort_order
        )

    async def update_user(
        self,
        user_id: uuid.UUID,
        user_data: UserUpdate,
        actor_id: Optional[uuid.UUID] = None,
    ) -> UserResponse:
        return await run_in_threadpool(
            self._update_user_sync, user_id, user_data, actor_id
        )

    async def delete_user(
        self,
        user_id: uuid.UUID,
        actor_id: Optional[uuid.UUID] = None,
        hard_delete: bool = False,
    ) -> dict:
        return await run_in_threadpool(
            self._delete_user_sync, user_id, actor_id, hard_delete
        )

    async def assign_roles(
        self,
        user_id: uuid.UUID,
        role_ids: list[uuid.UUID],
        actor_id: Optional[uuid.UUID] = None,
    ) -> dict:
        return await run_in_threadpool(
            self._assign_roles_public_sync, user_id, role_ids, actor_id
        )

    async def lock_user_account(
        self, user_id: uuid.UUID, actor_id: Optional[uuid.UUID] = None
    ) -> dict:
        return await run_in_threadpool(self._lock_user_account_sync, user_id, actor_id)

    async def unlock_user_account(
        self, user_id: uuid.UUID, actor_id: Optional[uuid.UUID] = None
    ) -> dict:
        return await run_in_threadpool(
            self._unlock_user_account_sync, user_id, actor_id
        )

    async def reset_password(
        self,
        user_id: uuid.UUID,
        actor_id: Optional[uuid.UUID] = None,
        new_password: Optional[str] = None,
    ) -> dict:
        return await run_in_threadpool(
            self._reset_password_sync, user_id, actor_id, new_password
        )

    async def bulk_update_status(
        self,
        user_ids: list[uuid.UUID],
        status_updates: dict[str, object],
        actor_id: Optional[uuid.UUID] = None,
    ) -> dict:
        return await run_in_threadpool(
            self._bulk_update_status_sync, user_ids, status_updates, actor_id
        )

    async def get_user_activity(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> list[dict[str, object]]:
        return await run_in_threadpool(self._get_user_activity_sync, user_id, limit)

    # -------------------- Internal sync implementations --------------------

    def _create_user_sync(
        self, user_data: UserCreate, actor_id: Optional[uuid.UUID]
    ) -> UserResponse:
        statement = select(User).where(User.email == user_data.email)
        existing_user = self.session.exec(statement).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=get_password_hash(user_data.password),
            is_verified=getattr(user_data, "is_verified", False),
            must_change_password=getattr(user_data, "must_change_password", False),
            avatar_url=getattr(user_data, "avatar_url", None),
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        if user_data.role_ids:
            self._assign_roles(user.id, user_data.role_ids)

        if actor_id:
            self._log_activity(
                actor_id=actor_id,
                action=ActivityActions.USER_CREATED,
                target_user_id=user.id,
                description=f"Created user account for {user.email}",
                metadata={"role_ids": [str(rid) for rid in (user_data.role_ids or [])]},
            )

        return UserResponse.model_validate(user)

    def _get_user_sync(self, user_id: uuid.UUID) -> UserWithRoles:
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return UserWithRoles.model_validate(user)

    def _get_users_sync(self, skip: int, limit: int) -> list[UserResponse]:
        statement = (
            select(User).where(User.deleted_at.is_(None)).offset(skip).limit(limit)
        )
        users = self.session.exec(statement).all()
        return [UserResponse.model_validate(user) for user in users]

    def _search_users_sync(
        self,
        filters: UserSearchFilters,
        skip: int,
        limit: int,
        sort_by: str,
        sort_order: str,
    ) -> dict[str, object]:
        query = select(User).options(selectinload(User.roles))

        conditions = []
        if not filters.include_deleted:
            conditions.append(User.deleted_at.is_(None))
        if filters.search:
            search_term = f"%{filters.search}%"
            conditions.append(
                or_(
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.phone.ilike(search_term),
                )
            )
        if filters.is_active is not None:
            conditions.append(User.is_active == filters.is_active)
        if filters.is_verified is not None:
            conditions.append(User.is_verified == filters.is_verified)
        if filters.is_locked is not None:
            conditions.append(User.is_locked == filters.is_locked)
        if filters.created_after:
            conditions.append(User.created_at >= filters.created_after)
        if filters.created_before:
            conditions.append(User.created_at <= filters.created_before)
        if filters.last_login_after:
            conditions.append(User.last_login_at >= filters.last_login_after)
        if filters.last_login_before:
            conditions.append(User.last_login_at <= filters.last_login_before)

        if conditions:
            from sqlmodel import and_ as _and

            query = query.where(_and(*conditions))

        if filters.role_ids:
            query = query.join(UserRole).where(UserRole.role_id.in_(filters.role_ids))

        count_query = select(func.count(User.id))
        if conditions:
            from sqlmodel import and_ as _and

            count_query = count_query.where(_and(*conditions))
        if filters.role_ids:
            count_query = count_query.join(UserRole).where(
                UserRole.role_id.in_(filters.role_ids)
            )

        total = self.session.exec(count_query).first()

        if hasattr(User, sort_by):
            sort_column = getattr(User, sort_by)
            query = query.order_by(
                sort_column.desc()
                if sort_order.lower() == "desc"
                else sort_column.asc()
            )

        query = query.offset(skip).limit(limit)
        users = self.session.exec(query).all()

        return {
            "users": [UserWithRoles.model_validate(user) for user in users],
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + len(users) < total,
        }

    def _update_user_sync(
        self, user_id: uuid.UUID, user_data: UserUpdate, actor_id: Optional[uuid.UUID]
    ) -> UserResponse:
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        original_values = {
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_locked": user.is_locked,
        }

        update_data = user_data.model_dump(exclude_unset=True)
        role_ids = update_data.pop("role_ids", None)

        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()

        if role_ids is not None:
            self._assign_roles(user_id, role_ids)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        if actor_id:
            changes = {}
            for field, original_value in original_values.items():
                current_value = getattr(user, field)
                if original_value != current_value:
                    changes[field] = {"from": original_value, "to": current_value}
            if changes or role_ids is not None:
                self._log_activity(
                    actor_id=actor_id,
                    action=ActivityActions.USER_UPDATED,
                    target_user_id=user.id,
                    description=f"Updated user {user.email}",
                    metadata={
                        "changes": changes,
                        "role_ids": [str(rid) for rid in (role_ids or [])],
                    },
                )

        return UserResponse.model_validate(user)

    def _delete_user_sync(
        self, user_id: uuid.UUID, actor_id: Optional[uuid.UUID], hard_delete: bool
    ) -> dict:
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if hard_delete:
            self.session.delete(user)
            action = "user_hard_deleted"
            message = "User permanently deleted"
        else:
            user.soft_delete()
            self.session.add(user)
            action = ActivityActions.USER_DELETED
            message = "User deactivated successfully"

        self.session.commit()

        if actor_id:
            self._log_activity(
                actor_id=actor_id,
                action=action,
                target_user_id=user_id,
                description=f"Deleted user {user.email}",
                metadata={"hard_delete": hard_delete},
            )

        return {"message": message}

    def _assign_roles_public_sync(
        self,
        user_id: uuid.UUID,
        role_ids: list[uuid.UUID],
        actor_id: Optional[uuid.UUID],
    ) -> dict:
        user = self._get_user_sync(user_id)
        current_role_ids = [role.id for role in user.roles]
        self._assign_roles(user_id, role_ids)

        if actor_id:
            self._log_activity(
                actor_id=actor_id,
                action=ActivityActions.ROLE_ASSIGNED,
                target_user_id=user_id,
                description=f"Updated roles for user {user.email}",
                metadata={
                    "previous_roles": [str(rid) for rid in current_role_ids],
                    "new_roles": [str(rid) for rid in role_ids],
                },
            )

        return {"message": "Roles assigned successfully"}

    def _lock_user_account_sync(
        self, user_id: uuid.UUID, actor_id: Optional[uuid.UUID]
    ) -> dict:
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.lock_account()
        self.session.add(user)
        self.session.commit()

        if actor_id:
            self._log_activity(
                actor_id=actor_id,
                action=ActivityActions.USER_LOCKED,
                target_user_id=user_id,
                description=f"Locked user account {user.email}",
            )

        return {"message": "User account locked successfully"}

    def _unlock_user_account_sync(
        self, user_id: uuid.UUID, actor_id: Optional[uuid.UUID]
    ) -> dict:
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.unlock_account()
        self.session.add(user)
        self.session.commit()

        if actor_id:
            self._log_activity(
                actor_id=actor_id,
                action=ActivityActions.USER_UNLOCKED,
                target_user_id=user_id,
                description=f"Unlocked user account {user.email}",
            )

        return {"message": "User account unlocked successfully"}

    def _reset_password_sync(
        self,
        user_id: uuid.UUID,
        actor_id: Optional[uuid.UUID],
        new_password: Optional[str],
    ) -> dict:
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not new_password:
            new_password = generate_random_password()

        user.password_hash = get_password_hash(new_password)
        user.must_change_password = True
        user.updated_at = datetime.utcnow()

        self.session.add(user)
        self.session.commit()

        if actor_id:
            self._log_activity(
                actor_id=actor_id,
                action=ActivityActions.USER_PASSWORD_RESET,
                target_user_id=user_id,
                description=f"Reset password for user {user.email}",
            )

        return {
            "message": "Password reset successfully",
            "temporary_password": new_password,
            "must_change_password": True,
        }

    def _bulk_update_status_sync(
        self,
        user_ids: list[uuid.UUID],
        status_updates: dict[str, object],
        actor_id: Optional[uuid.UUID],
    ) -> dict:
        statement = select(User).where(User.id.in_(user_ids))
        users = self.session.exec(statement).all()
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No users found"
            )

        for user in users:
            for field, value in status_updates.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            user.updated_at = datetime.utcnow()
            self.session.add(user)

        self.session.commit()

        if actor_id:
            action = None
            if status_updates.get("is_active") is True:
                action = ActivityActions.USERS_BULK_ACTIVATED
            elif status_updates.get("is_active") is False:
                action = ActivityActions.USERS_BULK_DEACTIVATED
            elif status_updates.get("deleted_at") is not None:
                action = ActivityActions.USERS_BULK_DELETED

            if action:
                self._log_activity(
                    actor_id=actor_id,
                    action=action,
                    description=f"Bulk updated {len(users)} users",
                    metadata={
                        "user_ids": [str(uid) for uid in user_ids],
                        "updates": status_updates,
                    },
                )

        return {
            "message": f"Successfully updated {len(users)} users",
            "updated_count": len(users),
        }

    def _get_user_activity_sync(
        self, user_id: uuid.UUID, limit: int
    ) -> list[dict[str, object]]:
        statement = (
            select(ActivityLog)
            .where(
                or_(
                    ActivityLog.actor_id == user_id,
                    ActivityLog.target_user_id == user_id,
                )
            )
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
        )
        activities = self.session.exec(statement).all()
        return [
            {
                "id": str(activity.id),
                "action": activity.action,
                "resource": activity.resource,
                "description": activity.description,
                "actor_email": activity.actor_email,
                "target_user_email": activity.target_user_email,
                "metadata": activity.get_metadata(),
                "ip_address": activity.ip_address,
                "created_at": activity.created_at.isoformat(),
            }
            for activity in activities
        ]

    # helpers
    def _assign_roles(self, user_id: uuid.UUID, role_ids: list[uuid.UUID]) -> None:
        statement = select(UserRole).where(UserRole.user_id == user_id)
        existing_roles = self.session.exec(statement).all()
        for role in existing_roles:
            self.session.delete(role)

        for role_id in role_ids:
            role = self.session.exec(select(Role).where(Role.id == role_id)).first()
            if role:
                self.session.add(UserRole(user_id=user_id, role_id=role_id))

        self.session.commit()

    def _log_activity(
        self,
        actor_id: uuid.UUID,
        action: str,
        description: str,
        target_user_id: Optional[uuid.UUID] = None,
        metadata: Optional[dict[str, object]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        actor = self.session.exec(select(User).where(User.id == actor_id)).first()
        actor_email = actor.email if actor else "unknown"

        target_user_email = None
        if target_user_id:
            target_user = self.session.exec(
                select(User).where(User.id == target_user_id)
            ).first()
            target_user_email = target_user.email if target_user else None

        activity = ActivityLog.create_log(
            actor_id=actor_id,
            actor_email=actor_email,
            action=action,
            resource=ActivityResources.USER,
            description=description,
            target_user_id=target_user_id,
            target_user_email=target_user_email,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.session.add(activity)
        self.session.commit()
