"""
User routes (async)
"""

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Request,
    HTTPException,
    status,
    UploadFile,
    File,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database_async import get_async_session
from services.user_service import UserService, UserSearchFilters
from schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithRoles,
    BulkUserUpdate,
)
from utils.dependencies import require_permission, get_current_user
from models.user import User
from typing import Optional
from datetime import datetime
import uuid
import csv
import io
import json

router = APIRouter(prefix="/users", tags=["User Management"])


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "create", "users")),
):
    service = UserService(session)
    return await service.create_user(user_data, actor_id=current_user.id)


@router.get("/", response_model=list[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_async_session),
    _: None = Depends(require_permission("auth", "read", "users")),
):
    service = UserService(session)
    return await service.get_users(skip=skip, limit=limit)


@router.get("/search", response_model=dict[str, object])
async def search_users(
    search: Optional[str] = Query(None),
    role_ids: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    is_locked: Optional[bool] = Query(None),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    last_login_after: Optional[datetime] = Query(None),
    last_login_before: Optional[datetime] = Query(None),
    include_deleted: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    session: AsyncSession = Depends(get_async_session),
    _: None = Depends(require_permission("auth", "read", "users")),
):
    role_id_list: list[uuid.UUID] = []
    if role_ids:
        try:
            role_id_list = [
                uuid.UUID(r.strip()) for r in role_ids.split(",") if r.strip()
            ]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role ID format"
            )

    filters = UserSearchFilters(
        search=search,
        role_ids=role_id_list,
        is_active=is_active,
        is_verified=is_verified,
        is_locked=is_locked,
        created_after=created_after,
        created_before=created_before,
        last_login_after=last_login_after,
        last_login_before=last_login_before,
        include_deleted=include_deleted,
    )
    service = UserService(session)
    return await service.search_users(
        filters=filters, skip=skip, limit=limit, sort_by=sort_by, sort_order=sort_order
    )


@router.get("/{user_id}", response_model=UserWithRoles)
async def get_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    _: None = Depends(require_permission("auth", "read", "users")),
):
    service = UserService(session)
    return await service.get_user(user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "update", "users")),
):
    service = UserService(session)
    return await service.update_user(user_id, user_data, actor_id=current_user.id)


@router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    hard_delete: bool = Query(False),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "delete", "users")),
):
    service = UserService(session)
    return await service.delete_user(
        user_id, actor_id=current_user.id, hard_delete=hard_delete
    )


@router.put("/{user_id}/roles")
async def assign_roles(
    user_id: uuid.UUID,
    role_data: dict[str, list[str]],
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "update", "users")),
):
    try:
        role_ids = [uuid.UUID(rid) for rid in role_data.get("role_ids", [])]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role ID format"
        )

    service = UserService(session)
    return await service.assign_roles(user_id, role_ids, actor_id=current_user.id)


@router.put("/{user_id}/status")
async def update_user_status(
    user_id: uuid.UUID,
    status_data: dict[str, object],
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "update", "users")),
):
    allowed_fields = {"is_active", "is_locked", "is_verified", "must_change_password"}
    invalid = set(status_data.keys()) - allowed_fields
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status fields: {', '.join(invalid)}",
        )

    service = UserService(session)
    return await service.bulk_update_status(
        [user_id], status_data, actor_id=current_user.id
    )


@router.post("/{user_id}/reset-password")
async def reset_password(
    user_id: uuid.UUID,
    password_data: Optional[dict[str, str]] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "update", "users")),
):
    new_password = None
    if password_data:
        new_password = password_data.get("new_password")

    service = UserService(session)
    return await service.reset_password(
        user_id, actor_id=current_user.id, new_password=new_password
    )


@router.post("/{user_id}/lock")
async def lock_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "update", "users")),
):
    service = UserService(session)
    return await service.lock_user_account(user_id, actor_id=current_user.id)


@router.post("/{user_id}/unlock")
async def unlock_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "update", "users")),
):
    service = UserService(session)
    return await service.unlock_user_account(user_id, actor_id=current_user.id)


@router.get("/{user_id}/activity")
async def get_user_activity(
    user_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=500),
    session: AsyncSession = Depends(get_async_session),
    _: None = Depends(require_permission("auth", "read", "users")),
):
    service = UserService(session)
    return await service.get_user_activity(user_id, limit=limit)


@router.put("/bulk-status")
async def bulk_update_status(
    bulk_data: BulkUserUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "update", "users")),
):
    service = UserService(session)
    return await service.bulk_update_status(
        bulk_data.user_ids, bulk_data.status_updates, actor_id=current_user.id
    )


@router.get("/export")
async def export_users(
    format: str = Query("csv", pattern="^(csv|json)$"),
    include_deleted: bool = Query(False),
    session: AsyncSession = Depends(get_async_session),
    _: None = Depends(require_permission("auth", "read", "users")),
):
    filters = UserSearchFilters(include_deleted=include_deleted)
    service = UserService(session)
    result = await service.search_users(filters=filters, skip=0, limit=10000)
    users = result["users"]

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "ID",
                "Full Name",
                "Email",
                "Phone",
                "Is Active",
                "Is Verified",
                "Is Locked",
                "Must Change Password",
                "Created At",
                "Last Login At",
            ]
        )
        for user in users:
            writer.writerow(
                [
                    str(user.id),
                    user.full_name,
                    user.email,
                    user.phone,
                    user.is_active,
                    user.is_verified,
                    user.is_locked,
                    user.must_change_password,
                    user.created_at,
                    user.last_login_at,
                ]
            )
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=users_export.csv"},
        )

    users_data = [u.model_dump() for u in users]
    json_data = json.dumps(users_data, indent=2, default=str)
    return StreamingResponse(
        io.BytesIO(json_data.encode()),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=users_export.json"},
    )
