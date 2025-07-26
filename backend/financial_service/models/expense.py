"""
Expense model for cost tracking
"""
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric
from typing import List, Optional
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid


class ExpenseCategory(str, Enum):
    """Expense category enumeration"""
    FUEL = "Fuel"
    MAINTENANCE = "Maintenance"
    INSURANCE = "Insurance"
    SALARIES = "Salaries"
    OFFICE_SUPPLIES = "Office Supplies"
    MARKETING = "Marketing"
    UTILITIES = "Utilities"
    RENT = "Rent"
    TRAVEL = "Travel"
    TRAINING = "Training"
    LEGAL = "Legal"
    ACCOUNTING = "Accounting"
    TECHNOLOGY = "Technology"
    EQUIPMENT = "Equipment"
    OTHER = "Other"


class ExpenseStatus(str, Enum):
    """Expense status enumeration"""
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PAID = "Paid"


class CostCenter(str, Enum):
    """Cost center enumeration"""
    OPERATIONS = "Operations"
    SALES = "Sales"
    MARKETING = "Marketing"
    ADMINISTRATION = "Administration"
    HR = "HR"
    IT = "IT"
    FINANCE = "Finance"
    FLEET = "Fleet"
    TOURS = "Tours"


class Expense(SQLModel, table=True):
    """Expense model for cost tracking and management"""
    __tablename__ = "expenses"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Expense Details
    expense_number: str = Field(unique=True, max_length=50, index=True)
    category: ExpenseCategory = Field(index=True)
    cost_center: CostCenter = Field(index=True)
    department: str = Field(max_length=100, index=True)
    
    # Financial Information
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    currency: str = Field(default="MAD", max_length=3)
    exchange_rate: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 4)))
    amount_in_base_currency: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    
    # Tax Information
    tax_amount: Optional[Decimal] = Field(default=0, sa_column=Column(Numeric(10, 2)))
    tax_rate: Optional[float] = Field(default=None)
    is_tax_deductible: bool = Field(default=True)
    
    # Description and Details
    description: str = Field(max_length=500)
    vendor_name: Optional[str] = Field(default=None, max_length=255)
    vendor_tax_id: Optional[str] = Field(default=None, max_length=50)
    
    # Dates
    expense_date: date = Field(index=True)
    due_date: Optional[date] = Field(default=None)
    paid_date: Optional[date] = Field(default=None)
    
    # Status and Approval
    status: ExpenseStatus = Field(default=ExpenseStatus.DRAFT, index=True)
    submitted_by: Optional[uuid.UUID] = Field(default=None, index=True)
    approved_by: Optional[uuid.UUID] = Field(default=None)
    rejected_reason: Optional[str] = Field(default=None, max_length=500)
    
    # Documentation
    receipt_url: Optional[str] = Field(default=None, max_length=500)
    invoice_number: Optional[str] = Field(default=None, max_length=100)
    reference_number: Optional[str] = Field(default=None, max_length=100)
    
    # Additional Information
    notes: Optional[str] = Field(default=None, max_length=1000)
    tags: Optional[str] = Field(default=None, max_length=200)  # JSON string
    
    # Recurring Expense
    is_recurring: bool = Field(default=False)
    recurring_frequency: Optional[str] = Field(default=None, max_length=20)  # monthly, quarterly, yearly
    
    # Project/Asset Association
    project_id: Optional[uuid.UUID] = Field(default=None, index=True)
    asset_id: Optional[uuid.UUID] = Field(default=None, index=True)  # Vehicle, equipment, etc.
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    def calculate_base_currency_amount(self, base_currency: str = "MAD"):
        """Calculate amount in base currency using exchange rate"""
        if self.currency == base_currency:
            self.amount_in_base_currency = self.amount
        elif self.exchange_rate:
            self.amount_in_base_currency = self.amount * self.exchange_rate
    
    def get_tags_list(self) -> List[str]:
        """Parse tags from JSON string"""
        if not self.tags:
            return []
        try:
            import json
            return json.loads(self.tags)
        except:
            return []
    
    def set_tags_list(self, tags: List[str]):
        """Set tags as JSON string"""
        import json
        self.tags = json.dumps(tags) if tags else None
    
    def is_overdue(self) -> bool:
        """Check if expense payment is overdue"""
        return (
            self.status in [ExpenseStatus.APPROVED] and
            self.due_date and
            date.today() > self.due_date
        )
    
    def get_total_with_tax(self) -> Decimal:
        """Get total amount including tax"""
        return self.amount + (self.tax_amount or 0)