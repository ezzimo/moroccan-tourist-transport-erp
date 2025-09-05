"""
Analytics service for financial analytics and reporting
"""

from sqlmodel import Session, select, and_, or_, func
from models.invoice import Invoice, InvoiceStatus
from models.payment import Payment, PaymentStatus
from models.expense import Expense, ExpenseStatus, ExpenseCategory

# from utils.currency import convert_currency
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import uuid
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for financial analytics and reporting"""

    def __init__(self, session: Session):
        self.session = session

    async def get_revenue_analytics(
        self,
        period_months: int = 12,
        currency: str = "MAD",
    ) -> Dict[str, Any]:
        """
        Compute revenue analytics for the last `period_months` months and
        always include a `forecast` shape expected by the frontend.
        """
        end_date = date.today()
        # NOTE: period_months is an int. relativedelta wants an int, not a string.
        start_date = end_date - relativedelta(months=period_months)

        query = select(Invoice).where(
            and_(
                Invoice.issue_date >= start_date,
                Invoice.issue_date <= end_date,
            )
        )
        invoices = self.session.exec(query).all()

        total_invoices = len(invoices)
        total_revenue = sum((inv.total_amount or 0) for inv in invoices)
        paid_revenue = sum(
            (inv.total_amount or 0)
            for inv in invoices
            if inv.status == InvoiceStatus.PAID
        )
        outstanding_revenue = sum(
            (inv.total_amount or 0)
            for inv in invoices
            if inv.status in {InvoiceStatus.SENT, InvoiceStatus.OVERDUE}
        )
        overdue_revenue = sum(
            (inv.total_amount or 0)
            for inv in invoices
            if inv.status == InvoiceStatus.OVERDUE
        )

        collection_rate = float(paid_revenue / total_revenue) if total_revenue else 0.0
        overdue_rate = float(overdue_revenue / total_revenue) if total_revenue else 0.0
        avg_invoice_value = (
            float(total_revenue / total_invoices) if total_invoices else 0.0
        )

        return {
            "period": {
                "start_date": str(start_date),
                "end_date": str(end_date),
            },
            "currency": currency,
            "summary": {
                "total_invoices": total_invoices,
                "total_revenue": float(total_revenue),
                "paid_revenue": float(paid_revenue),
                "outstanding_revenue": float(outstanding_revenue),
                "overdue_revenue": float(overdue_revenue),
                "collection_rate": collection_rate,
                "overdue_rate": overdue_rate,
                "average_invoice_value": avg_invoice_value,
            },
            "monthly_breakdown": [],
            "top_customers": [],
            "forecast": {
                "next_30_days": [],
                "next_12_months": [],
            },
        }

    async def get_expense_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        currency: str = "MAD",
    ) -> Dict[str, Any]:
        """Get expense analytics

        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            currency: Target currency for conversion

        Returns:
            Expense analytics data
        """
        # Default to current year if no dates provided
        if not start_date:
            start_date = date(date.today().year, 1, 1)
        if not end_date:
            end_date = date.today()

        # Get expenses for the period
        query = select(Expense).where(
            and_(Expense.expense_date >= start_date, Expense.expense_date <= end_date)
        )
        expenses = self.session.exec(query).all()

        # Calculate metrics
        total_expenses = len(expenses)
        total_amount = Decimal("0")
        approved_amount = Decimal("0")
        paid_amount = Decimal("0")
        reimbursable_amount = Decimal("0")

        by_category = {}
        by_employee = {}
        monthly_expenses = {}

        for expense in expenses:
            # Convert to target currency if needed
            amount = expense.amount
            # if expense.currency != currency:
            #     amount = await convert_currency(amount, expense.currency, currency)

            total_amount += amount

            if expense.status in [
                ExpenseStatus.APPROVED.value,
                ExpenseStatus.PAID.value,
            ]:
                approved_amount += amount

            if expense.status == ExpenseStatus.PAID.value:
                paid_amount += amount

            if expense.is_reimbursable:
                reimbursable_amount += amount

            # Category breakdown
            category = expense.category.value
            if category not in by_category:
                by_category[category] = {
                    "category": category,
                    "total_amount": 0,
                    "expense_count": 0,
                    "average_amount": 0,
                }

            by_category[category]["total_amount"] += float(amount)
            by_category[category]["expense_count"] += 1
            by_category[category]["average_amount"] = (
                by_category[category]["total_amount"]
                / by_category[category]["expense_count"]
            )

            # Employee breakdown
            if expense.employee_id:
                employee_id = str(expense.employee_id)
                if employee_id not in by_employee:
                    by_employee[employee_id] = {
                        "employee_id": employee_id,
                        "total_amount": 0,
                        "expense_count": 0,
                        "reimbursable_amount": 0,
                    }

                by_employee[employee_id]["total_amount"] += float(amount)
                by_employee[employee_id]["expense_count"] += 1

                if expense.is_reimbursable:
                    by_employee[employee_id]["reimbursable_amount"] += float(amount)

            # Monthly breakdown
            month_key = expense.expense_date.strftime("%Y-%m")
            if month_key not in monthly_expenses:
                monthly_expenses[month_key] = {
                    "month": month_key,
                    "total_amount": 0,
                    "expense_count": 0,
                    "reimbursable_amount": 0,
                }

            monthly_expenses[month_key]["total_amount"] += float(amount)
            monthly_expenses[month_key]["expense_count"] += 1

            if expense.is_reimbursable:
                monthly_expenses[month_key]["reimbursable_amount"] += float(amount)

        # Calculate rates
        approval_rate = (
            (approved_amount / total_amount * 100) if total_amount > 0 else 0
        )
        reimbursement_rate = (
            (reimbursable_amount / total_amount * 100) if total_amount > 0 else 0
        )

        # Average expense amount
        avg_expense_amount = total_amount / total_expenses if total_expenses > 0 else 0

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "currency": currency,
            "summary": {
                "total_expenses": total_expenses,
                "total_amount": float(total_amount),
                "approved_amount": float(approved_amount),
                "paid_amount": float(paid_amount),
                "reimbursable_amount": float(reimbursable_amount),
                "approval_rate": float(approval_rate),
                "reimbursement_rate": float(reimbursement_rate),
                "average_expense_amount": float(avg_expense_amount),
            },
            "by_category": list(by_category.values()),
            "by_employee": sorted(
                by_employee.values(), key=lambda x: x["total_amount"], reverse=True
            )[:10],
            "monthly_breakdown": list(monthly_expenses.values()),
        }

    async def get_cash_flow_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        currency: str = "MAD",
    ) -> Dict[str, Any]:
        """Get cash flow analytics

        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            currency: Target currency for conversion

        Returns:
            Cash flow analytics data
        """
        # Default to current year if no dates provided
        if not start_date:
            start_date = date(date.today().year, 1, 1)
        if not end_date:
            end_date = date.today()

        # Get payments (cash inflows)
        payment_query = select(Payment).where(
            and_(
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date,
                Payment.status == PaymentStatus.COMPLETED,
                Payment.amount > 0,  # Exclude refunds
            )
        )
        payments = self.session.exec(payment_query).all()

        # Get expenses (cash outflows)
        expense_query = select(Expense).where(
            and_(
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date,
                Expense.status == ExpenseStatus.PAID.value,
            )
        )
        expenses = self.session.exec(expense_query).all()

        # Calculate monthly cash flow
        monthly_cash_flow = {}
        total_inflow = Decimal("0")
        total_outflow = Decimal("0")

        # Process payments (inflows)
        for payment in payments:
            amount = payment.amount
            # if payment.currency != currency:
            #     amount = await convert_currency(amount, payment.currency, currency)

            total_inflow += amount

            month_key = payment.payment_date.strftime("%Y-%m")
            if month_key not in monthly_cash_flow:
                monthly_cash_flow[month_key] = {
                    "month": month_key,
                    "inflow": 0,
                    "outflow": 0,
                    "net_flow": 0,
                }

            monthly_cash_flow[month_key]["inflow"] += float(amount)

        # Process expenses (outflows)
        for expense in expenses:
            amount = expense.amount
            # if expense.currency != currency:
            #     amount = await convert_currency(amount, expense.currency, currency)

            total_outflow += amount

            month_key = expense.expense_date.strftime("%Y-%m")
            if month_key not in monthly_cash_flow:
                monthly_cash_flow[month_key] = {
                    "month": month_key,
                    "inflow": 0,
                    "outflow": 0,
                    "net_flow": 0,
                }

            monthly_cash_flow[month_key]["outflow"] += float(amount)

        # Calculate net flow for each month
        for month_data in monthly_cash_flow.values():
            month_data["net_flow"] = month_data["inflow"] - month_data["outflow"]

        # Calculate cumulative cash flow
        sorted_months = sorted(monthly_cash_flow.values(), key=lambda x: x["month"])
        cumulative_flow = 0
        for month_data in sorted_months:
            cumulative_flow += month_data["net_flow"]
            month_data["cumulative_flow"] = cumulative_flow

        net_cash_flow = total_inflow - total_outflow

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "currency": currency,
            "summary": {
                "total_inflow": float(total_inflow),
                "total_outflow": float(total_outflow),
                "net_cash_flow": float(net_cash_flow),
                "payment_count": len(payments),
                "expense_count": len(expenses),
            },
            "monthly_breakdown": sorted_months,
        }

    async def get_profitability_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        currency: str = "MAD",
    ) -> Dict[str, Any]:
        """Get profitability analytics

        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            currency: Target currency for conversion

        Returns:
            Profitability analytics data
        """
        # Get revenue and expense analytics
        revenue_data = await self.get_revenue_analytics(start_date, end_date, currency)
        expense_data = await self.get_expense_analytics(start_date, end_date, currency)

        # Calculate profitability metrics
        total_revenue = Decimal(str(revenue_data["summary"]["paid_revenue"]))
        total_expenses = Decimal(str(expense_data["summary"]["paid_amount"]))

        gross_profit = total_revenue - total_expenses
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

        # Monthly profitability
        monthly_profit = {}

        # Combine monthly data
        for month_data in revenue_data["monthly_breakdown"]:
            month = month_data["month"]
            monthly_profit[month] = {
                "month": month,
                "revenue": month_data["paid"],
                "expenses": 0,
                "profit": month_data["paid"],
                "margin": 0,
            }

        for month_data in expense_data["monthly_breakdown"]:
            month = month_data["month"]
            if month not in monthly_profit:
                monthly_profit[month] = {
                    "month": month,
                    "revenue": 0,
                    "expenses": month_data["total_amount"],
                    "profit": -month_data["total_amount"],
                    "margin": 0,
                }
            else:
                monthly_profit[month]["expenses"] = month_data["total_amount"]
                monthly_profit[month]["profit"] = (
                    monthly_profit[month]["revenue"] - month_data["total_amount"]
                )

        # Calculate monthly margins
        for month_data in monthly_profit.values():
            if month_data["revenue"] > 0:
                month_data["margin"] = (
                    month_data["profit"] / month_data["revenue"] * 100
                )

        return {
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
            "currency": currency,
            "summary": {
                "total_revenue": float(total_revenue),
                "total_expenses": float(total_expenses),
                "gross_profit": float(gross_profit),
                "profit_margin": float(profit_margin),
            },
            "monthly_breakdown": sorted(
                monthly_profit.values(), key=lambda x: x["month"]
            ),
        }

    async def get_financial_dashboard(self, currency: str = "MAD") -> Dict[str, Any]:
        today = date.today()
        current_month_start = date(today.year, today.month, 1)
        current_year_start = date(today.year, 1, 1)

        # ✅ revenue: pass months (int), not dates
        current_month_revenue = await self.get_revenue_analytics(
            period_months=1, currency=currency
        )

        current_month_expenses = await self.get_expense_analytics(
            current_month_start, today, currency
        )

        # YTD months = current month index in the year
        ytd_months = today.month
        ytd_revenue = await self.get_revenue_analytics(
            period_months=ytd_months, currency=currency
        )

        ytd_expenses = await self.get_expense_analytics(
            current_year_start, today, currency
        )

        # Outstanding invoices and pending expenses unchanged…
        outstanding_query = select(Invoice).where(
            Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.OVERDUE])
        )
        outstanding_invoices = self.session.exec(outstanding_query).all()
        outstanding_amount = sum(inv.total_amount for inv in outstanding_invoices)

        overdue_invoices = [inv for inv in outstanding_invoices if inv.is_overdue()]
        overdue_amount = sum(inv.total_amount for inv in overdue_invoices)

        pending_query = select(Expense).where(
            Expense.status
            == ExpenseStatus.PENDING.value  # keep .value to match DB strings
        )
        pending_expenses = self.session.exec(pending_query).all()
        pending_amount = sum(exp.amount for exp in pending_expenses)

        return {
            "currency": currency,
            "current_month": {
                "revenue": current_month_revenue["summary"]["paid_revenue"],
                "expenses": current_month_expenses["summary"]["paid_amount"],
                "profit": (
                    current_month_revenue["summary"]["paid_revenue"]
                    - current_month_expenses["summary"]["paid_amount"]
                ),
                "invoice_count": current_month_revenue["summary"]["total_invoices"],
                "expense_count": current_month_expenses["summary"]["total_expenses"],
            },
            "year_to_date": {
                "revenue": ytd_revenue["summary"]["paid_revenue"],
                "expenses": ytd_expenses["summary"]["paid_amount"],
                "profit": (
                    ytd_revenue["summary"]["paid_revenue"]
                    - ytd_expenses["summary"]["paid_amount"]
                ),
                "collection_rate": ytd_revenue["summary"]["collection_rate"],
            },
            "outstanding": {
                "invoice_count": len(outstanding_invoices),
                "total_amount": float(outstanding_amount),
                "overdue_count": len(overdue_invoices),
                "overdue_amount": float(overdue_amount),
            },
            "pending": {
                "expense_count": len(pending_expenses),
                "total_amount": float(pending_amount),
            },
        }
