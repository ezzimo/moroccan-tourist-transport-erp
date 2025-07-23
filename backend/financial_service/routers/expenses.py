"""
Expense management routes
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from sqlmodel import Session
from database import get_session, get_redis
from services.expense_service import ExpenseService
from schemas.expense import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseSummary,
    ExpenseSearch, ExpenseApproval
)
from models.expense import ExpenseCategory, ExpenseStatus, CostCenter
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid


router = APIRouter(prefix="/expenses", tags=["Expense Management"])


@router.post("/", response_model=ExpenseResponse)
async def create_expense(
    expense_data: ExpenseCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "create", "expenses"))
):
    """Create a new expense"""
    expense_service = ExpenseService(session, redis_client)
    return await expense_service.create_expense(expense_data, current_user.user_id)


@router.post("/upload", response_model=ExpenseResponse)
async def create_expense_with_receipt(
    category: ExpenseCategory = Form(...),
    cost_center: CostCenter = Form(...),
    department: str = Form(...),
    amount: float = Form(...),
    currency: str = Form("MAD"),
    description: str = Form(...),
    expense_date: str = Form(...),
    vendor_name: Optional[str] = Form(None),
    vendor_tax_id: Optional[str] = Form(None),
    tax_amount: Optional[float] = Form(0.0),
    tax_rate: Optional[float] = Form(None),
    is_tax_deductible: bool = Form(True),
    invoice_number: Optional[str] = Form(None),
    reference_number: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string
    receipt_file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "create", "expenses"))
):
    """Create expense with receipt upload"""
    from datetime import datetime
    from decimal import Decimal
    
    # Parse date
    try:
        expense_date_parsed = datetime.strptime(expense_date, "%Y-%m-%d").date()
    except ValueError:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid expense_date format. Use YYYY-MM-DD"
        )
    
    # Parse tags
    tags_list = []
    if tags:
        try:
            import json
            tags_list = json.loads(tags)
        except:
            pass
    
    # Create expense data
    expense_data = ExpenseCreate(
        category=category,
        cost_center=cost_center,
        department=department,
        amount=Decimal(str(amount)),
        currency=currency,
        description=description,
        expense_date=expense_date_parsed,
        vendor_name=vendor_name,
        vendor_tax_id=vendor_tax_id,
        tax_amount=Decimal(str(tax_amount)) if tax_amount else None,
        tax_rate=tax_rate,
        is_tax_deductible=is_tax_deductible,
        invoice_number=invoice_number,
        reference_number=reference_number,
        notes=notes,
        tags=tags_list
    )
    
    expense_service = ExpenseService(session, redis_client)
    return await expense_service.create_expense_with_receipt(
        expense_data, receipt_file, current_user.user_id
    )


@router.get("/", response_model=PaginatedResponse[ExpenseResponse])
async def get_expenses(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[ExpenseCategory] = Query(None, description="Filter by category"),
    cost_center: Optional[CostCenter] = Query(None, description="Filter by cost center"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[ExpenseStatus] = Query(None, description="Filter by status"),
    currency: Optional[str] = Query(None, description="Filter by currency"),
    expense_date_from: Optional[str] = Query(None, description="Filter by expense date from (YYYY-MM-DD)"),
    expense_date_to: Optional[str] = Query(None, description="Filter by expense date to (YYYY-MM-DD)"),
    vendor_name: Optional[str] = Query(None, description="Filter by vendor"),
    submitted_by: Optional[uuid.UUID] = Query(None, description="Filter by submitter"),
    is_tax_deductible: Optional[bool] = Query(None, description="Filter by tax deductible"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "expenses"))
):
    """Get list of expenses with optional search and filters"""
    expense_service = ExpenseService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([query, category, cost_center, department, status, currency, 
            expense_date_from, expense_date_to, vendor_name, submitted_by, is_tax_deductible is not None]):
        from datetime import datetime
        from fastapi import HTTPException, status as http_status
        
        expense_date_from_parsed = None
        expense_date_to_parsed = None
        
        if expense_date_from:
            try:
                expense_date_from_parsed = datetime.strptime(expense_date_from, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Invalid expense_date_from format. Use YYYY-MM-DD"
                )
        
        if expense_date_to:
            try:
                expense_date_to_parsed = datetime.strptime(expense_date_to, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Invalid expense_date_to format. Use YYYY-MM-DD"
                )
        
        search = ExpenseSearch(
            query=query,
            category=category,
            cost_center=cost_center,
            department=department,
            status=status,
            currency=currency,
            expense_date_from=expense_date_from_parsed,
            expense_date_to=expense_date_to_parsed,
            vendor_name=vendor_name,
            submitted_by=submitted_by,
            is_tax_deductible=is_tax_deductible
        )
    
    expenses, total = await expense_service.get_expenses(pagination, search)
    
    return PaginatedResponse.create(
        items=expenses,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/summary", response_model=ExpenseSummary)
async def get_expense_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days for summary"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "expenses"))
):
    """Get expense summary statistics"""
    expense_service = ExpenseService(session, redis_client)
    return await expense_service.get_expense_summary(days)


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "expenses"))
):
    """Get expense by ID"""
    expense_service = ExpenseService(session, redis_client)
    return await expense_service.get_expense(expense_id)


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: uuid.UUID,
    expense_data: ExpenseUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "update", "expenses"))
):
    """Update expense information"""
    expense_service = ExpenseService(session, redis_client)
    return await expense_service.update_expense(expense_id, expense_data)


@router.post("/{expense_id}/approve", response_model=ExpenseResponse)
async def approve_expense(
    expense_id: uuid.UUID,
    approval: ExpenseApproval,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "approve", "expenses"))
):
    """Approve or reject an expense"""
    expense_service = ExpenseService(session, redis_client)
    return await expense_service.approve_expense(expense_id, approval, current_user.user_id)


@router.post("/{expense_id}/submit", response_model=ExpenseResponse)
async def submit_expense(
    expense_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "update", "expenses"))
):
    """Submit expense for approval"""
    expense_service = ExpenseService(session, redis_client)
    return await expense_service.submit_expense(expense_id, current_user.user_id)


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "delete", "expenses"))
):
    """Delete expense"""
    expense_service = ExpenseService(session, redis_client)
    return await expense_service.delete_expense(expense_id)


@router.get("/pending/approval", response_model=List[ExpenseResponse])
async def get_pending_expenses(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "expenses"))
):
    """Get expenses pending approval"""
    expense_service = ExpenseService(session, redis_client)
    return await expense_service.get_pending_expenses()


@router.post("/bulk-approve")
async def bulk_approve_expenses(
    expense_ids: List[uuid.UUID],
    approval: ExpenseApproval,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "approve", "expenses"))
):
    """Bulk approve multiple expenses"""
    expense_service = ExpenseService(session, redis_client)
    return await expense_service.bulk_approve_expenses(expense_ids, approval, current_user.user_id)