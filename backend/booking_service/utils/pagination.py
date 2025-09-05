"""
Pagination utilities
"""

from __future__ import annotations

from fastapi import Query
from pydantic import BaseModel
from typing import Generic, List, TypeVar
from sqlmodel import Session, select, func

from ..config import settings

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters"""

    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Page size",
    )

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: List[T], total: int, page: int, size: int):
        """Create paginated response"""
        pages = (total + size - 1) // size if total else 0  # ceiling division
        return cls(items=items, total=total, page=page, size=size, pages=pages)


def _scalar_one_compat(exec_result) -> int:
    """
    Compatibility helper:
    - SQLAlchemy Result:     use .scalar_one()
    - SQLAlchemy ScalarResult: use .one()
    Always returns an int.
    """
    if hasattr(exec_result, "scalar_one"):  # Result
        value = exec_result.scalar_one()
    else:  # ScalarResult
        value = exec_result.one()
    return int(value or 0)


def paginate_query(session: Session, query, pagination: PaginationParams):
    """
    Apply pagination to a SQLModel select() query.

    - Returns ORM instances for `items` (not Row objects).
    - `total` is a plain int.
    """
    # Efficient count over a subquery without ORDER BY
    count_stmt = select(func.count()).select_from(query.order_by(None).subquery())
    total: int = _scalar_one_compat(session.exec(count_stmt))

    # Apply pagination and fetch ORM objects
    paginated_stmt = query.offset(pagination.offset).limit(pagination.size)
    items: List[T] = session.exec(paginated_stmt).all()

    return items, total
