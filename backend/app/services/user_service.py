"""
Async User service
"""

from sqlmodel import Session, select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
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
    """Service for handling user operations"""

    def __init__(self, session: Session):
        self.session = session

    # --- small helpers to keep DB work off the event loop ---
    async def _exec(self, stmt):
        return await run_in_threadpool(self.session.exec, stmt)

    async def _add(self, obj):
        return await run_in_threadpool(self.session.add, obj)

    async def _commit(self):
        return await run_in_threadpool(self.session.commit)

    async def _refresh(self, obj):
        return await run_in_threadpool(self.session.refresh, obj)

    async def create_user(
        self, user_data: UserCreate, actor_id: Optional[uuid.UUID] = None
    ) -> UserResponse:
        stmt = select(User).where(User.email == user_data.email)
        existing = (await self._exec(stmt)).first()
        if existing:
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
        await self._add(user)
        await self._commit()
        await self._refresh(user)
        return UserResponse.model_validate(user)

    async def get_user(self, user_id: uuid.UUID) -> UserWithRoles:
        stmt = select(User).where(User.id == user_id)
        user = (await self._exec(stmt)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserWithRoles.model_validate(user)

    async def get_users(
        self, skip: int = 0, limit: int = 100
    ) -> list[UserResponse]:
        stmt = (
            select(User)
            .where(User.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        users = (await self._exec(stmt)).all()
        return [UserResponse.model_validate(u) for u in users]

    async def search_users(
        self,
        filters: UserSearchFilters,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> dict[str, object]:
        query = select(User).options(selectinload(User.roles))
        conditions = []

        if not filters.include_deleted:
            conditions.append(User.deleted_at.is_(None))

        if filters.search:
            st = f"%{filters.search}%"
            conditions.append(
                or_(
                    User.full_name.ilike(st), User.email.ilike(st), User.phone.ilike(st)
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
            query = query.where(and_(*conditions))

        if filters.role_ids:
            query = query.join(UserRole).where(UserRole.role_id.in_(filters.role_ids))

        count_query = select(func.count(User.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        if filters.role_ids:
            count_query = count_query.join(UserRole).where(
                UserRole.role_id.in_(filters.role_ids)
            )

        total = (await self.session.exec(count_query)).scalar_one()

        if hasattr(User, sort_by):
            col = getattr(User, sort_by)
            query = query.order_by(
                col.desc() if sort_order.lower() == "desc" else col.asc()
            )

        query = query.offset(skip).limit(limit)
        users = (await self.session.exec(query)).all()

        return {
            "users": [UserWithRoles.model_validate(u) for u in users],
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + len(users)) < total,
        }

    async def update_user(
        self,
        user_id: uuid.UUID,
        user_data: UserUpdate,
        actor_id: Optional[uuid.UUID] = None,
    ) -> UserResponse:
        res = await self.session.exec(select(User).where(User.id == user_id))
        user = res.first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        original = {
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_locked": user.is_locked,
        }

        update_data = user_data.model_dump(exclude_unset=True)
        role_ids = update_data.pop("role_ids", None)
        for k, v in update_data.items():
            setattr(user, k, v)

        user.updated_at = datetime.utcnow()

        if role_ids is not None:
            await self._assign_roles(user_id, role_ids)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        if actor_id:
            changes = {}
            for k, ov in original.items():
                cv = getattr(user, k)
                if ov != cv:
                    changes[k] = {"from": ov, "to": cv}
            if changes or role_ids is not None:
                await self._log_activity(
                    actor_id=actor_id,
                    action=ActivityActions.USER_UPDATED,
                    target_user_id=user.id,
                    description=f"Updated user {user.email}",
                    metadata={
                        "changes": changes,
                        "role_ids": [str(r) for r in (role_ids or [])],
                    },
                )

        return UserResponse.model_validate(user)

    async def delete_user(
        self,
        user_id: uuid.UUID,
        actor_id: Optional[uuid.UUID] = None,
        hard_delete: bool = False,
    ) -> dict:
        res = await self.session.exec(select(User).where(User.id == user_id))
        user = res.first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if hard_delete:
            await self.session.delete(user)
            action = "user_hard_deleted"
            message = "User permanently deleted"
        else:
            user.soft_delete()
            self.session.add(user)
            action = ActivityActions.USER_DELETED
            message = "User deactivated successfully"

        await self.session.commit()

        if actor_id:
            await self._log_activity(
                actor_id=actor_id,
                action=action,
                target_user_id=user_id,
                description=f"Deleted user {user.email}",
                metadata={"hard_delete": hard_delete},
            )

        return {"message": message}

    async def assign_roles(
        self,
        user_id: uuid.UUID,
        role_ids: list[uuid.UUID],
        actor_id: Optional[uuid.UUID] = None,
    ) -> dict:
        user = await self.get_user(user_id)
        current_role_ids = [r.id for r in user.roles]
        await self._assign_roles(user_id, role_ids)

        if actor_id:
            await self._log_activity(
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

    async def lock_user_account(
        self, user_id: uuid.UUID, actor_id: Optional[uuid.UUID] = None
    ) -> dict:
        res = await self.session.exec(select(User).where(User.id == user_id))
        user = res.first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.lock_account()
        self.session.add(user)
        await self.session.commit()

        if actor_id:
            await self._log_activity(
                actor_id=actor_id,
                action=ActivityActions.USER_LOCKED,
                target_user_id=user_id,
                description=f"Locked user account {user.email}",
            )
        return {"message": "User account locked successfully"}

    async def unlock_user_account(
        self, user_id: uuid.UUID, actor_id: Optional[uuid.UUID] = None
    ) -> dict:
        res = await self.session.exec(select(User).where(User.id == user_id))
        user = res.first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.unlock_account()
        self.session.add(user)
        await self.session.commit()

        if actor_id:
            await self._log_activity(
                actor_id=actor_id,
                action=ActivityActions.USER_UNLOCKED,
                target_user_id=user_id,
                description=f"Unlocked user account {user.email}",
            )
        return {"message": "User account unlocked successfully"}

    async def reset_password(
        self,
        user_id: uuid.UUID,
        actor_id: Optional[uuid.UUID] = None,
        new_password: Optional[str] = None,
    ) -> dict:
        res = await self.session.exec(select(User).where(User.id == user_id))
        user = res.first()
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
        await self.session.commit()

        if actor_id:
            await self._log_activity(
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

    async def bulk_update_status(
        self,
        user_ids: list[uuid.UUID],
        status_updates: dict[str, object],
        actor_id: Optional[uuid.UUID] = None,
    ) -> dict:
        res = await self.session.exec(select(User).where(User.id.in_(user_ids)))
        users = res.all()
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

        await self.session.commit()

        if actor_id:
            action = None
            if status_updates.get("is_active") is True:
                action = ActivityActions.USERS_BULK_ACTIVATED
            elif status_updates.get("is_active") is False:
                action = ActivityActions.USERS_BULK_DEACTIVATED
            elif status_updates.get("deleted_at") is not None:
                action = ActivityActions.USERS_BULK_DELETED

            if action:
                await self._log_activity(
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

    async def get_user_activity(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> list[dict[str, object]]:
        stmt = (
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
        activities = (await self.session.exec(stmt)).all()
        return [
            {
                "id": str(a.id),
                "action": a.action,
                "resource": a.resource,
                "description": a.description,
                "actor_email": a.actor_email,
                "target_user_email": a.target_user_email,
                "metadata": a.get_metadata(),
                "ip_address": a.ip_address,
                "created_at": a.created_at.isoformat(),
            }
            for a in activities
        ]

    async def _assign_roles(self, user_id: uuid.UUID, role_ids: list[uuid.UUID]):
        res = await self.session.exec(
            select(UserRole).where(UserRole.user_id == user_id)
        )
        existing_roles = res.all()
        for r in existing_roles:
            await self.session.delete(r)

        for rid in role_ids:
            check = await self.session.exec(select(Role).where(Role.id == rid))
            if check.first():
                self.session.add(UserRole(user_id=user_id, role_id=rid))
        await self.session.commit()

    async def _log_activity(
        self,
        actor_id: uuid.UUID,
        action: str,
        description: str,
        target_user_id: Optional[uuid.UUID] = None,
        metadata: Optional[dict[str, object]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        actor = (
            await self.session.exec(select(User).where(User.id == actor_id))
        ).first()
        actor_email = actor.email if actor else "unknown"

        target_user_email = None
        if target_user_id:
            tu = (
                await self.session.exec(select(User).where(User.id == target_user_id))
            ).first()
            target_user_email = tu.email if tu else None

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
        await self.session.commit()
