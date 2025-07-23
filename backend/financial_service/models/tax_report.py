"""
Tax report model for tax compliance
"""
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric
from typing import Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid
import json


class ReportPeriod(str, Enum):
    """Report period enumeration"""
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"


class ReportStatus(str, Enum):
    """Report status enumeration"""
    DRAFT = "Draft"
    GENERATED = "Generated"
    REVIEWED = "Reviewed"
    SUBMITTED = "Submitted"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class TaxType(str, Enum):
    """Tax type enumeration"""
    VAT = "VAT"
    INCOME_TAX = "Income Tax"
    CORPORATE_TAX = "Corporate Tax"
    WITHHOLDING_TAX = "Withholding Tax"


class TaxReport(SQLModel, table=True):
    """Tax report model for tax compliance and submissions"""
    __tablename__ = "tax_reports"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Report Identification
    report_number: str = Field(unique=True, max_length=50, index=True)
    tax_type: TaxType = Field(index=True)
    
    # Period Information
    period_type: ReportPeriod = Field(index=True)
    period_start: date = Field(index=True)
    period_end: date = Field(index=True)
    tax_year: int = Field(index=True)
    
    # Financial Totals
    total_revenue: Decimal = Field(default=0, sa_column=Column(Numeric(15, 2)))
    total_expenses: Decimal = Field(default=0, sa_column=Column(Numeric(15, 2)))
    taxable_income: Decimal = Field(default=0, sa_column=Column(Numeric(15, 2)))
    
    # VAT Specific
    total_vat_collected: Decimal = Field(default=0, sa_column=Column(Numeric(12, 2)))
    total_vat_paid: Decimal = Field(default=0, sa_column=Column(Numeric(12, 2)))
    net_vat_due: Decimal = Field(default=0, sa_column=Column(Numeric(12, 2)))
    
    # Tax Calculations
    tax_rate: float = Field(default=20.0)
    calculated_tax: Decimal = Field(default=0, sa_column=Column(Numeric(12, 2)))
    tax_credits: Decimal = Field(default=0, sa_column=Column(Numeric(12, 2)))
    tax_due: Decimal = Field(default=0, sa_column=Column(Numeric(12, 2)))
    
    # Detailed Breakdown (JSON)
    revenue_breakdown: str = Field(default="{}")  # JSON string
    expense_breakdown: str = Field(default="{}")  # JSON string
    vat_breakdown: str = Field(default="{}")     # JSON string
    
    # Status and Submission
    status: ReportStatus = Field(default=ReportStatus.DRAFT, index=True)
    generated_at: Optional[datetime] = Field(default=None)
    submitted_at: Optional[datetime] = Field(default=None)
    submission_reference: Optional[str] = Field(default=None, max_length=100)
    
    # Approval Workflow
    prepared_by: Optional[uuid.UUID] = Field(default=None)
    reviewed_by: Optional[uuid.UUID] = Field(default=None)
    approved_by: Optional[uuid.UUID] = Field(default=None)
    
    # File References
    report_file_path: Optional[str] = Field(default=None, max_length=500)
    supporting_documents: Optional[str] = Field(default=None, max_length=1000)  # JSON array
    
    # Notes and Comments
    notes: Optional[str] = Field(default=None, max_length=2000)
    reviewer_comments: Optional[str] = Field(default=None, max_length=1000)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    def get_revenue_breakdown_dict(self) -> Dict[str, Any]:
        """Parse revenue breakdown from JSON string"""
        try:
            return json.loads(self.revenue_breakdown)
        except:
            return {}
    
    def set_revenue_breakdown_dict(self, breakdown: Dict[str, Any]):
        """Set revenue breakdown as JSON string"""
        self.revenue_breakdown = json.dumps(breakdown)
    
    def get_expense_breakdown_dict(self) -> Dict[str, Any]:
        """Parse expense breakdown from JSON string"""
        try:
            return json.loads(self.expense_breakdown)
        except:
            return {}
    
    def set_expense_breakdown_dict(self, breakdown: Dict[str, Any]):
        """Set expense breakdown as JSON string"""
        self.expense_breakdown = json.dumps(breakdown)
    
    def get_vat_breakdown_dict(self) -> Dict[str, Any]:
        """Parse VAT breakdown from JSON string"""
        try:
            return json.loads(self.vat_breakdown)
        except:
            return {}
    
    def set_vat_breakdown_dict(self, breakdown: Dict[str, Any]):
        """Set VAT breakdown as JSON string"""
        self.vat_breakdown = json.dumps(breakdown)
    
    def calculate_net_vat(self):
        """Calculate net VAT due (collected - paid)"""
        self.net_vat_due = self.total_vat_collected - self.total_vat_paid
    
    def calculate_tax_due(self):
        """Calculate total tax due"""
        self.tax_due = self.calculated_tax - self.tax_credits
        if self.tax_due < 0:
            self.tax_due = Decimal(0)
    
    def get_period_description(self) -> str:
        """Get human-readable period description"""
        if self.period_type == ReportPeriod.MONTHLY:
            return f"{self.period_start.strftime('%B %Y')}"
        elif self.period_type == ReportPeriod.QUARTERLY:
            quarter = ((self.period_start.month - 1) // 3) + 1
            return f"Q{quarter} {self.tax_year}"
        else:
            return f"Year {self.tax_year}"