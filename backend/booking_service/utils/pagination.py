"""
Pagination utilities
"""
from fastapi import Query
from pydantic import BaseModel
from typing import List, TypeVar, Generic
from sqlmodel import Session, select, func
from config import settings

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size, description="Page size")
    
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
        pages = (total + size - 1) // size  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )


def paginate_query(session: Session, query, pagination: PaginationParams):
    """Apply pagination to SQLModel query"""
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()
    
    # Apply pagination
    paginated_query = query.offset(pagination.offset).limit(pagination.size)
    items = session.exec(paginated_query).all()
    
    return items, total