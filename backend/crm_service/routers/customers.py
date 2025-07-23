"""
Customer management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from services.customer_service import CustomerService
from schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerSummary, CustomerSearch
)
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import uuid


router = APIRouter(prefix="/customers", tags=["Customer Management"])


@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "create", "customers"))
):
    """Create a new customer"""
    customer_service = CustomerService(session)
    return await customer_service.create_customer(customer_data)


@router.get("/", response_model=PaginatedResponse[CustomerResponse])
async def get_customers(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    contact_type: Optional[str] = Query(None, description="Filter by contact type"),
    region: Optional[str] = Query(None, description="Filter by region"),
    loyalty_status: Optional[str] = Query(None, description="Filter by loyalty status"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "read", "customers"))
):
    """Get list of customers with optional search and filters"""
    customer_service = CustomerService(session)
    
    # Build search criteria
    search = None
    if any([query, contact_type, region, loyalty_status, tags, is_active is not None]):
        search = CustomerSearch(
            query=query,
            contact_type=contact_type,
            region=region,
            loyalty_status=loyalty_status,
            tags=tags,
            is_active=is_active
        )
    
    customers, total = await customer_service.get_customers(pagination, search)
    
    return PaginatedResponse.create(
        items=customers,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "read", "customers"))
):
    """Get customer by ID"""
    customer_service = CustomerService(session)
    return await customer_service.get_customer(customer_id)


@router.get("/{customer_id}/summary", response_model=CustomerSummary)
async def get_customer_summary(
    customer_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "read", "customers"))
):
    """Get comprehensive customer summary with statistics"""
    customer_service = CustomerService(session)
    return await customer_service.get_customer_summary(customer_id)


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: uuid.UUID,
    customer_data: CustomerUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "update", "customers"))
):
    """Update customer information"""
    customer_service = CustomerService(session)
    return await customer_service.update_customer(customer_id, customer_data)


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "delete", "customers"))
):
    """Delete customer (soft delete)"""
    customer_service = CustomerService(session)
    return await customer_service.delete_customer(customer_id)