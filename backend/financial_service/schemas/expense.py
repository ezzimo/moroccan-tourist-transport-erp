"""
Expense-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from models.expense import ExpenseCategory, ExpenseStatus, CostCenter
import uuid


class ExpenseBase(BaseModel):
    category: ExpenseCategory
    cost_center: CostCenter
    department: str
    amount: Decimal
    currency: str = "MAD"
    description: str
    vendor_name: Optional[str] = None
    vendor_tax_id: Optional[str] = None
    expense_date: date
    due_date: Optional[date] = None
    tax_amount: Optional[Decimal] = Decimal("0.0")
    tax_rate: Optional[float] = None
    is_tax_deductible: bool = True
    invoice_number: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    tags: Optional[List[str]] = []
    exchange_rate: Optional[Decimal] = None
    is_recurring: bool = False
    recurring_frequency: Optional[str] = None
    project_id: Optional[uuid.UUID] = None
    asset_id: Optional[uuid.UUID] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Expense amount must be greater than 0')
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        allowed_currencies = ["MAD", "EUR", "USD"]
        if v not in allowed_currencies:
            raise ValueError(f'Currency must be one of {allowed_currencies}')
        return v
    
    @validator('due_date')
    def validate_due_date(cls, v, values):
        if v and 'expense_date' in values and v < values['expense_date']:
            raise ValueError('Due date cannot be before expense date')
        return v


class ExpenseUpdate(BaseModel):
    category: Optional[ExpenseCategory] = None
    cost_center: Optional[CostCenter] = None
    department: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_tax_id: Optional[str] = None
    expense_date: Optional[date] = None
    due_date: Optional[date] = None
    status: Optional[ExpenseStatus] = None
    tax_amount: Optional[Decimal] = None
    tax_rate: Optional[float] = None
    is_tax_deductible: Optional[bool] = None
    invoice_number: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    receipt_url: Optional[str] = None
    paid_date: Optional[date] = None


class ExpenseResponse(ExpenseBase):
    id: uuid.UUID
    expense_number: str
    exchange_rate: Optional[Decimal]
    amount_in_base_currency: Optional[Decimal]
    status: ExpenseStatus
    submitted_by: Optional[uuid.UUID]
    approved_by: Optional[uuid.UUID]
    rejected_reason: Optional[str]
    receipt_url: Optional[str]
    tags: List[str] = []
    is_recurring: bool
    recurring_frequency: Optional[str]
    project_id: Optional[uuid.UUID]
    asset_id: Optional[uuid.UUID]
    paid_date: Optional[date]
    created_at: datetime
    updated_at: Optional[datetime]
    total_with_tax: Decimal
    is_overdue: bool


class ExpenseSummary(BaseModel):
    """Expense summary for dashboard"""
    total_expenses: int
    total_amount: Decimal
    by_category: Dict[str, Decimal]
    by_cost_center: Dict[str, Decimal]
    by_department: Dict[str, Decimal]
    by_status: Dict[str, int]
    by_currency: Dict[str, Decimal]
    pending_approval_amount: Decimal
    overdue_amount: Decimal
    tax_deductible_amount: Decimal


class ExpenseSearch(BaseModel):
    """Expense search criteria"""
    query: Optional[str] = None
    category: Optional[ExpenseCategory] = None
    cost_center: Optional[CostCenter] = None
    department: Optional[str] = None
    status: Optional[ExpenseStatus] = None
    currency: Optional[str] = None
    expense_date_from: Optional[date] = None
    expense_date_to: Optional[date] = None
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    vendor_name: Optional[str] = None
    submitted_by: Optional[uuid.UUID] = None
    is_tax_deductible: Optional[bool] = None
    is_overdue: Optional[bool] = None


class ExpenseApproval(BaseModel):
    """Schema for expense approval/rejection"""
    status: ExpenseStatus
    notes: Optional[str] = None
    rejected_reason: Optional[str] = None


class ExpenseUpload(BaseModel):
    """Schema for expense with receipt upload"""
    expense_data: ExpenseCreate
    receipt_file: Optional[str] = None  # Base64 encoded file or file path