"""
User management routes (async, services threadpool-backed)
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
from sqlmodel import Session
from database import get_session
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
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "create", "users")),
):
    user_service = UserService(session)
    return await user_service.create_user(user_data, actor_id=current_user.id)


@router.get("/", response_model=list[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "read", "users")),
):
    user_service = UserService(session)
    return await user_service.get_users(skip=skip, limit=limit)


@router.get("/search", response_model=dict[str, object])
async def search_users(
    search: Optional[str] = Query(
        None, description="Search term for name, email, or phone"
    ),
    role_ids: Optional[str] = Query(None, description="Comma-separated role IDs"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verified status"),
    is_locked: Optional[bool] = Query(None, description="Filter by locked status"),
    created_after: Optional[datetime] = Query(
        None, description="Filter users created after this date"
    ),
    created_before: Optional[datetime] = Query(
        None, description="Filter users created before this date"
    ),
    last_login_after: Optional[datetime] = Query(
        None, description="Filter users with last login after this date"
    ),
    last_login_before: Optional[datetime] = Query(
        None, description="Filter users with last login before this date"
    ),
    include_deleted: bool = Query(False, description="Include soft-deleted users"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "read", "users")),
):
    role_id_list: list[uuid.UUID] = []
    if role_ids:
        try:
            role_id_list = [
                uuid.UUID(rid.strip()) for rid in role_ids.split(",") if rid.strip()
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

    user_service = UserService(session)
    return await user_service.search_users(
        filters=filters, skip=skip, limit=limit, sort_by=sort_by, sort_order=sort_order
    )


@router.get("/{user_id}", response_model=UserWithRoles)
async def get_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "read", "users")),
):
    user_service = UserService(session)
    return await user_service.get_user(user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "update", "users")),
):
    user_service = UserService(session)
    return await user_service.update_user(user_id, user_data, actor_id=current_user.id)


@router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    hard_delete: bool = Query(False, description="Permanently delete user"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "delete", "users")),
):
    user_service = UserService(session)
    return await user_service.delete_user(
        user_id, actor_id=current_user.id, hard_delete=hard_delete
    )


@router.put("/{user_id}/roles")
async def assign_roles(
    user_id: uuid.UUID,
    role_data: dict[str, list[str]],
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "update", "users")),
):
    try:
        role_ids = [uuid.UUID(rid) for rid in role_data.get("role_ids", [])]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role ID format"
        )

    user_service = UserService(session)
    return await user_service.assign_roles(user_id, role_ids, actor_id=current_user.id)


@router.put("/{user_id}/status")
async def update_user_status(
    user_id: uuid.UUID,
    status_data: dict[str, object],
    session: Session = Depends(get_session),
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

    user_service = UserService(session)
    return await user_service.bulk_update_status(
        [user_id], status_data, actor_id=current_user.id
    )


@router.post("/{user_id}/reset-password")
async def reset_password(
    user_id: uuid.UUID,
    password_data: Optional[dict[str, str]] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "update", "users")),
):
    new_password = password_data.get("new_password") if password_data else None
    user_service = UserService(session)
    return await user_service.reset_password(
        user_id, actor_id=current_user.id, new_password=new_password
    )


@router.post("/{user_id}/lock")
async def lock_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "update", "users")),
):
    user_service = UserService(session)
    return await user_service.lock_user_account(user_id, actor_id=current_user.id)


@router.post("/{user_id}/unlock")
async def unlock_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "update", "users")),
):
    user_service = UserService(session)
    return await user_service.unlock_user_account(user_id, actor_id=current_user.id)


@router.get("/{user_id}/activity")
async def get_user_activity(
    user_id: uuid.UUID,
    limit: int = Query(
        50, ge=1, le=500, description="Number of activity records to return"
    ),
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "read", "users")),
):
    user_service = UserService(session)
    return await user_service.get_user_activity(user_id, limit=limit)


@router.put("/bulk-status")
async def bulk_update_status(
    bulk_data: BulkUserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "update", "users")),
):
    user_service = UserService(session)
    return await user_service.bulk_update_status(
        bulk_data.user_ids, bulk_data.status_updates, actor_id=current_user.id
    )


@router.get("/export")
async def export_users(
    format: str = Query("csv", pattern="^(csv|json)$", description="Export format"),
    include_deleted: bool = Query(False, description="Include soft-deleted users"),
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "read", "users")),
):
    filters = UserSearchFilters(include_deleted=include_deleted)
    user_service = UserService(session)
    result = await user_service.search_users(filters=filters, skip=0, limit=10000)
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

    users_data = [user.model_dump() for user in users]
    json_data = json.dumps(users_data, indent=2, default=str)
    return StreamingResponse(
        io.BytesIO(json_data.encode()),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=users_export.json"},
    )


@router.post("/import")
async def import_users(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("auth", "create", "users")),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported",
        )

    try:
        content = await file.read()
        csv_content = content.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(csv_content))

        user_service = UserService(session)
        created_users = []
        errors = []

        for row_num, row in enumerate(csv_reader, start=2):
            try:
                required = ["full_name", "email", "phone", "password"]
                missing = [field for field in required if not row.get(field)]
                if missing:
                    errors.append(
                        f"Row {row_num}: Missing fields: {', '.join(missing)}"
                    )
                    continue

                user_data = UserCreate(
                    full_name=row["full_name"],
                    email=row["email"],
                    phone=row["phone"],
                    password=row["password"],
                    is_verified=row.get("is_verified", "false").lower() == "true",
                    must_change_password=row.get("must_change_password", "true").lower()
                    == "true",
                )

                user = await user_service.create_user(
                    user_data, actor_id=current_user.id
                )
                created_users.append(user)

            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")

        return {
            "message": f"Import completed. Created {len(created_users)} users.",
            "created_count": len(created_users),
            "error_count": len(errors),
            "errors": errors[:10],
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process CSV file: {str(e)}",
        )
