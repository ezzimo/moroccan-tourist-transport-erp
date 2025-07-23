"""
Tax report-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from decimal import Decimal
from models.tax_report import ReportPeriod, ReportStatus, TaxType
import uuid


class TaxReportBase(BaseModel):
    tax_type: TaxType
    period_type: ReportPeriod
    period_start: date
    period_end: date
    tax_year: int
    tax_rate: float = 20.0
    notes: Optional[str] = None


class TaxReportCreate(TaxReportBase):
    @validator('period_end')
    def validate_period_end(cls, v, values):
        if 'period_start' in values and v <= values['period_start']:
            raise ValueError('Period end must be after period start')
        return v
    
    @validator('tax_year')
    def validate_tax_year(cls, v):
        current_year = date.today().year
        if v < 2020 or v > current_year + 1:
            raise ValueError(f'Tax year must be between 2020 and {current_year + 1}')
        return v


class TaxReportUpdate(BaseModel):
    status: Optional[ReportStatus] = None
    notes: Optional[str] = None
    reviewer_comments: Optional[str] = None
    submission_reference: Optional[str] = None


class TaxReportResponse(TaxReportBase):
    id: uuid.UUID
    report_number: str
    total_revenue: Decimal
    total_expenses: Decimal
    taxable_income: Decimal
    total_vat_collected: Decimal
    total_vat_paid: Decimal
    net_vat_due: Decimal
    calculated_tax: Decimal
    tax_credits: Decimal
    tax_due: Decimal
    revenue_breakdown: Dict[str, Any]
    expense_breakdown: Dict[str, Any]
    vat_breakdown: Dict[str, Any]
    status: ReportStatus
    generated_at: Optional[datetime]
    submitted_at: Optional[datetime]
    submission_reference: Optional[str]
    prepared_by: Optional[uuid.UUID]
    reviewed_by: Optional[uuid.UUID]
    approved_by: Optional[uuid.UUID]
    report_file_path: Optional[str]
    supporting_documents: List[str] = []
    reviewer_comments: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    period_description: str


class TaxReportGeneration(BaseModel):
    """Schema for generating tax report"""
    tax_type: TaxType
    period_type: ReportPeriod
    period_start: date
    period_end: date
    include_draft_transactions: bool = False
    auto_submit: bool = False
    notes: Optional[str] = None


class VATDeclaration(BaseModel):
    """VAT declaration details"""
    period_start: date
    period_end: date
    sales_vat: Decimal
    purchase_vat: Decimal
    net_vat: Decimal
    sales_breakdown: Dict[str, Decimal]
    purchase_breakdown: Dict[str, Decimal]
    exemptions: Dict[str, Decimal]
    adjustments: Dict[str, Decimal]


class TaxSummary(BaseModel):
    """Tax summary for dashboard"""
    current_period_vat_due: Decimal
    ytd_vat_collected: Decimal
    ytd_vat_paid: Decimal
    ytd_net_vat: Decimal
    pending_submissions: int
    overdue_submissions: int
    next_filing_date: Optional[date]
    estimated_quarterly_tax: Decimal
    by_tax_type: Dict[str, Decimal]
    compliance_status: str