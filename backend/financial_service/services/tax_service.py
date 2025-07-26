"""
Tax service for tax calculation and reporting operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.tax_report import TaxReport, TaxType
from models.invoice import Invoice, InvoiceStatus
from models.expense import Expense, ExpenseStatus
from schemas.tax_report import (
    TaxReportCreate, TaxReportUpdate, TaxReportResponse
)
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
import logging

logger = logging.getLogger(__name__)


class TaxService:
    """Service for handling tax operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def calculate_vat(
        self,
        start_date: date,
        end_date: date,
        vat_rate: Decimal = Decimal('20.0')  # Morocco VAT rate
    ) -> Dict[str, Any]:
        """Calculate VAT for a period
        
        Args:
            start_date: Period start date
            end_date: Period end date
            vat_rate: VAT rate percentage
            
        Returns:
            VAT calculation details
        """
        # Get invoices for the period
        invoice_query = select(Invoice).where(
            and_(
                Invoice.issue_date >= start_date,
                Invoice.issue_date <= end_date,
                Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PAID])
            )
        )
        invoices = self.session.exec(invoice_query).all()
        
        # Calculate output VAT (VAT on sales)
        output_vat = Decimal('0')
        total_sales = Decimal('0')
        
        for invoice in invoices:
            if invoice.tax_rate and invoice.tax_rate > 0:
                output_vat += invoice.tax_amount
                total_sales += invoice.subtotal
        
        # Get expenses for the period (input VAT)
        expense_query = select(Expense).where(
            and_(
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date,
                Expense.status.in_([ExpenseStatus.APPROVED, ExpenseStatus.PAID])
            )
        )
        expenses = self.session.exec(expense_query).all()
        
        # Calculate input VAT (VAT on purchases)
        input_vat = Decimal('0')
        total_purchases = Decimal('0')
        
        for expense in expenses:
            # Assume VAT is included in expense amount
            vat_inclusive_amount = expense.amount
            vat_exclusive_amount = vat_inclusive_amount / (1 + vat_rate / 100)
            expense_vat = vat_inclusive_amount - vat_exclusive_amount
            
            input_vat += expense_vat
            total_purchases += vat_exclusive_amount
        
        # Calculate net VAT liability
        net_vat = output_vat - input_vat
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "vat_rate": float(vat_rate),
            "sales": {
                "total_sales": float(total_sales),
                "output_vat": float(output_vat),
                "invoice_count": len(invoices)
            },
            "purchases": {
                "total_purchases": float(total_purchases),
                "input_vat": float(input_vat),
                "expense_count": len(expenses)
            },
            "net_vat_liability": float(net_vat),
            "vat_refund_due": float(-net_vat) if net_vat < 0 else 0,
            "vat_payment_due": float(net_vat) if net_vat > 0 else 0
        }
    
    async def calculate_income_tax(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Calculate income tax for a period
        
        Args:
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            Income tax calculation details
        """
        # Get revenue (from invoices)
        invoice_query = select(Invoice).where(
            and_(
                Invoice.issue_date >= start_date,
                Invoice.issue_date <= end_date,
                Invoice.status == InvoiceStatus.PAID
            )
        )
        invoices = self.session.exec(invoice_query).all()
        total_revenue = sum(inv.subtotal for inv in invoices)
        
        # Get deductible expenses
        expense_query = select(Expense).where(
            and_(
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date,
                Expense.status == ExpenseStatus.PAID
            )
        )
        expenses = self.session.exec(expense_query).all()
        total_expenses = sum(exp.amount for exp in expenses)
        
        # Calculate taxable income
        taxable_income = total_revenue - total_expenses
        
        # Morocco corporate tax rates (simplified)
        tax_rate = Decimal('31.0')  # 31% for companies
        if taxable_income <= 300000:  # MAD 300,000
            tax_rate = Decimal('10.0')  # 10% for small businesses
        elif taxable_income <= 1000000:  # MAD 1,000,000
            tax_rate = Decimal('20.0')  # 20% for medium businesses
        
        income_tax = max(Decimal('0'), taxable_income * tax_rate / 100)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "revenue": {
                "total_revenue": float(total_revenue),
                "invoice_count": len(invoices)
            },
            "expenses": {
                "total_expenses": float(total_expenses),
                "expense_count": len(expenses)
            },
            "taxable_income": float(taxable_income),
            "tax_rate": float(tax_rate),
            "income_tax_due": float(income_tax)
        }
    
    async def create_tax_report(self, report_data: TaxReportCreate) -> TaxReportResponse:
        """Create a new tax report
        
        Args:
            report_data: Tax report creation data
            
        Returns:
            Created tax report
        """
        # Calculate tax based on type
        if report_data.tax_type == TaxType.VAT:
            calculation = await self.calculate_vat(
                report_data.period_start,
                report_data.period_end
            )
            tax_amount = Decimal(str(calculation["net_vat_liability"]))
        elif report_data.tax_type == TaxType.INCOME_TAX:
            calculation = await self.calculate_income_tax(
                report_data.period_start,
                report_data.period_end
            )
            tax_amount = Decimal(str(calculation["income_tax_due"]))
        else:
            tax_amount = Decimal('0')
            calculation = {}
        
        # Generate report reference
        report_reference = await self._generate_report_reference(report_data.tax_type)
        
        # Create tax report
        tax_report = TaxReport(
            report_reference=report_reference,
            tax_type=report_data.tax_type,
            period_start=report_data.period_start,
            period_end=report_data.period_end,
            tax_amount=tax_amount,
            status="DRAFT",
            calculation_details=calculation,
            notes=report_data.notes
        )
        
        self.session.add(tax_report)
        self.session.commit()
        self.session.refresh(tax_report)
        
        logger.info(f"Created tax report {tax_report.report_reference}")
        return self._to_response(tax_report)
    
    async def get_tax_report(self, report_id: uuid.UUID) -> TaxReportResponse:
        """Get tax report by ID
        
        Args:
            report_id: Tax report UUID
            
        Returns:
            Tax report details
            
        Raises:
            HTTPException: If tax report not found
        """
        tax_report = self.session.get(TaxReport, report_id)
        if not tax_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax report not found"
            )
        
        return self._to_response(tax_report)
    
    async def get_tax_reports(
        self,
        skip: int = 0,
        limit: int = 100,
        tax_type: Optional[TaxType] = None,
        status: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[TaxReportResponse]:
        """Get tax reports with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            tax_type: Filter by tax type
            status: Filter by status
            year: Filter by year
            
        Returns:
            List of tax reports
        """
        query = select(TaxReport)
        
        # Apply filters
        conditions = []
        
        if tax_type:
            conditions.append(TaxReport.tax_type == tax_type)
        
        if status:
            conditions.append(TaxReport.status == status)
        
        if year:
            start_of_year = date(year, 1, 1)
            end_of_year = date(year, 12, 31)
            conditions.append(
                and_(
                    TaxReport.period_start >= start_of_year,
                    TaxReport.period_end <= end_of_year
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(TaxReport.period_end.desc()).offset(skip).limit(limit)
        tax_reports = self.session.exec(query).all()
        
        return [self._to_response(report) for report in tax_reports]
    
    async def submit_tax_report(self, report_id: uuid.UUID) -> dict:
        """Submit tax report to authorities
        
        Args:
            report_id: Tax report UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If tax report not found or cannot be submitted
        """
        tax_report = self.session.get(TaxReport, report_id)
        if not tax_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax report not found"
            )
        
        if tax_report.status != "DRAFT":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft reports can be submitted"
            )
        
        tax_report.status = "SUBMITTED"
        tax_report.submitted_at = datetime.utcnow()
        tax_report.updated_at = datetime.utcnow()
        
        self.session.add(tax_report)
        self.session.commit()
        
        logger.info(f"Submitted tax report {tax_report.report_reference}")
        return {"message": "Tax report submitted successfully"}
    
    async def get_tax_summary(self, year: int) -> Dict[str, Any]:
        """Get annual tax summary
        
        Args:
            year: Year for summary
            
        Returns:
            Annual tax summary
        """
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        # Get all tax reports for the year
        reports = await self.get_tax_reports(year=year, limit=1000)
        
        # Calculate VAT summary
        vat_calculation = await self.calculate_vat(start_date, end_date)
        
        # Calculate income tax summary
        income_tax_calculation = await self.calculate_income_tax(start_date, end_date)
        
        # Summary by quarter
        quarterly_summary = {}
        for quarter in range(1, 5):
            q_start = date(year, (quarter - 1) * 3 + 1, 1)
            if quarter == 4:
                q_end = date(year, 12, 31)
            else:
                q_end = date(year, quarter * 3, 28)  # Simplified
            
            q_vat = await self.calculate_vat(q_start, q_end)
            quarterly_summary[f"Q{quarter}"] = {
                "period": f"{q_start.isoformat()} to {q_end.isoformat()}",
                "vat_liability": q_vat["net_vat_liability"],
                "sales": q_vat["sales"]["total_sales"],
                "purchases": q_vat["purchases"]["total_purchases"]
            }
        
        return {
            "year": year,
            "vat_summary": vat_calculation,
            "income_tax_summary": income_tax_calculation,
            "quarterly_breakdown": quarterly_summary,
            "total_reports": len(reports),
            "submitted_reports": len([r for r in reports if r.status == "SUBMITTED"]),
            "total_tax_liability": float(
                Decimal(str(vat_calculation["net_vat_liability"])) + 
                Decimal(str(income_tax_calculation["income_tax_due"]))
            )
        }
    
    async def _generate_report_reference(self, tax_type: TaxType) -> str:
        """Generate unique tax report reference"""
        now = datetime.now()
        type_prefix = "VAT" if tax_type == TaxType.VAT else "INC"
        prefix = f"{type_prefix}-{now.year}{now.month:02d}"
        
        # Get last report reference for this month and type
        last_report = self.session.exec(
            select(TaxReport)
            .where(
                and_(
                    TaxReport.report_reference.like(f"{prefix}%"),
                    TaxReport.tax_type == tax_type
                )
            )
            .order_by(TaxReport.report_reference.desc())
        ).first()
        
        if last_report:
            # Extract sequence number and increment
            last_seq = int(last_report.report_reference.split('-')[-1])
            seq = last_seq + 1
        else:
            seq = 1
        
        return f"{prefix}-{seq:04d}"
    
    def _to_response(self, tax_report: TaxReport) -> TaxReportResponse:
        """Convert tax report model to response schema"""
        return TaxReportResponse(
            id=tax_report.id,
            report_reference=tax_report.report_reference,
            tax_type=tax_report.tax_type,
            period_start=tax_report.period_start,
            period_end=tax_report.period_end,
            tax_amount=tax_report.tax_amount,
            status=tax_report.status,
            calculation_details=tax_report.calculation_details,
            notes=tax_report.notes,
            submitted_at=tax_report.submitted_at,
            created_at=tax_report.created_at,
            updated_at=tax_report.updated_at
        )