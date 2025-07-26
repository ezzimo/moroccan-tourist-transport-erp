"""
Expense service for expense management operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.expense import Expense, ExpenseStatus, ExpenseCategory
from schemas.expense import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse
)
# from utils.currency import convert_currency
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
import logging

logger = logging.getLogger(__name__)


class ExpenseService:
    """Service for handling expense operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_expense(self, expense_data: ExpenseCreate) -> ExpenseResponse:
        """Create a new expense
        
        Args:
            expense_data: Expense creation data
            
        Returns:
            Created expense
            
        Raises:
            HTTPException: If validation fails
        """
        # Generate expense reference
        expense_reference = await self._generate_expense_reference()
        
        # Create expense
        expense = Expense(
            expense_reference=expense_reference,
            category=expense_data.category,
            description=expense_data.description,
            amount=expense_data.amount,
            currency=expense_data.currency,
            expense_date=expense_data.expense_date or date.today(),
            vendor=expense_data.vendor,
            receipt_number=expense_data.receipt_number,
            status=ExpenseStatus.PENDING,
            notes=expense_data.notes,
            employee_id=expense_data.employee_id,
            project_id=expense_data.project_id,
            is_reimbursable=expense_data.is_reimbursable
        )
        
        self.session.add(expense)
        self.session.commit()
        self.session.refresh(expense)
        
        logger.info(f"Created expense {expense.expense_reference}")
        return self._to_response(expense)
    
    async def get_expense(self, expense_id: uuid.UUID) -> ExpenseResponse:
        """Get expense by ID
        
        Args:
            expense_id: Expense UUID
            
        Returns:
            Expense details
            
        Raises:
            HTTPException: If expense not found
        """
        expense = self.session.get(Expense, expense_id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        return self._to_response(expense)
    
    async def get_expenses(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[ExpenseCategory] = None,
        status: Optional[ExpenseStatus] = None,
        employee_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        reimbursable_only: bool = False
    ) -> List[ExpenseResponse]:
        """Get expenses with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            category: Filter by expense category
            status: Filter by expense status
            employee_id: Filter by employee ID
            project_id: Filter by project ID
            start_date: Filter expenses from this date
            end_date: Filter expenses until this date
            reimbursable_only: Show only reimbursable expenses
            
        Returns:
            List of expenses
        """
        query = select(Expense)
        
        # Apply filters
        conditions = []
        
        if category:
            conditions.append(Expense.category == category)
        
        if status:
            conditions.append(Expense.status == status)
        
        if employee_id:
            conditions.append(Expense.employee_id == employee_id)
        
        if project_id:
            conditions.append(Expense.project_id == project_id)
        
        if start_date:
            conditions.append(Expense.expense_date >= start_date)
        
        if end_date:
            conditions.append(Expense.expense_date <= end_date)
        
        if reimbursable_only:
            conditions.append(Expense.is_reimbursable == True)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Expense.expense_date.desc()).offset(skip).limit(limit)
        expenses = self.session.exec(query).all()
        
        return [self._to_response(expense) for expense in expenses]
    
    async def update_expense(
        self, 
        expense_id: uuid.UUID, 
        expense_data: ExpenseUpdate
    ) -> ExpenseResponse:
        """Update expense information
        
        Args:
            expense_id: Expense UUID
            expense_data: Update data
            
        Returns:
            Updated expense
            
        Raises:
            HTTPException: If expense not found or cannot be updated
        """
        expense = self.session.get(Expense, expense_id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        # Check if expense can be updated
        if expense.status in [ExpenseStatus.APPROVED, ExpenseStatus.PAID]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update expense with status {expense.status}"
            )
        
        # Update fields
        update_data = expense_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expense, field, value)
        
        expense.updated_at = datetime.utcnow()
        
        self.session.add(expense)
        self.session.commit()
        self.session.refresh(expense)
        
        logger.info(f"Updated expense {expense.expense_reference}")
        return self._to_response(expense)
    
    async def approve_expense(self, expense_id: uuid.UUID, approved_by: uuid.UUID) -> dict:
        """Approve an expense
        
        Args:
            expense_id: Expense UUID
            approved_by: User who approved the expense
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If expense not found or cannot be approved
        """
        expense = self.session.get(Expense, expense_id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        if expense.status != ExpenseStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve expense with status {expense.status}"
            )
        
        expense.status = ExpenseStatus.APPROVED
        expense.approved_by = approved_by
        expense.approved_at = datetime.utcnow()
        expense.updated_at = datetime.utcnow()
        
        self.session.add(expense)
        self.session.commit()
        
        logger.info(f"Approved expense {expense.expense_reference}")
        return {"message": "Expense approved successfully"}
    
    async def reject_expense(
        self, 
        expense_id: uuid.UUID, 
        rejected_by: uuid.UUID,
        reason: Optional[str] = None
    ) -> dict:
        """Reject an expense
        
        Args:
            expense_id: Expense UUID
            rejected_by: User who rejected the expense
            reason: Rejection reason
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If expense not found or cannot be rejected
        """
        expense = self.session.get(Expense, expense_id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        if expense.status != ExpenseStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reject expense with status {expense.status}"
            )
        
        expense.status = ExpenseStatus.REJECTED
        expense.rejected_by = rejected_by
        expense.rejected_at = datetime.utcnow()
        if reason:
            expense.notes = f"{expense.notes or ''}\nRejected: {reason}"
        expense.updated_at = datetime.utcnow()
        
        self.session.add(expense)
        self.session.commit()
        
        logger.info(f"Rejected expense {expense.expense_reference}")
        return {"message": "Expense rejected successfully"}
    
    async def mark_paid(self, expense_id: uuid.UUID, payment_date: Optional[date] = None) -> dict:
        """Mark expense as paid
        
        Args:
            expense_id: Expense UUID
            payment_date: Date of payment
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If expense not found or cannot be marked as paid
        """
        expense = self.session.get(Expense, expense_id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        if expense.status != ExpenseStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only mark approved expenses as paid"
            )
        
        expense.status = ExpenseStatus.PAID
        expense.paid_at = payment_date or date.today()
        expense.updated_at = datetime.utcnow()
        
        self.session.add(expense)
        self.session.commit()
        
        logger.info(f"Marked expense {expense.expense_reference} as paid")
        return {"message": "Expense marked as paid"}
    
    async def get_pending_expenses(self) -> List[ExpenseResponse]:
        """Get pending expenses for approval
        
        Returns:
            List of pending expenses
        """
        return await self.get_expenses(status=ExpenseStatus.PENDING, limit=1000)
    
    async def get_expense_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        employee_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get expense analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            employee_id: Filter by specific employee
            
        Returns:
            Analytics data
        """
        query = select(Expense)
        
        conditions = []
        if start_date:
            conditions.append(Expense.expense_date >= start_date)
        if end_date:
            conditions.append(Expense.expense_date <= end_date)
        if employee_id:
            conditions.append(Expense.employee_id == employee_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        expenses = self.session.exec(query).all()
        
        # Calculate metrics
        total_expenses = len(expenses)
        total_amount = sum(exp.amount for exp in expenses)
        approved_expenses = len([exp for exp in expenses if exp.status == ExpenseStatus.APPROVED])
        approved_amount = sum(exp.amount for exp in expenses if exp.status == ExpenseStatus.APPROVED)
        paid_expenses = len([exp for exp in expenses if exp.status == ExpenseStatus.PAID])
        paid_amount = sum(exp.amount for exp in expenses if exp.status == ExpenseStatus.PAID)
        
        # By category
        by_category = {}
        for expense in expenses:
            category = expense.category.value
            by_category[category] = by_category.get(category, 0) + float(expense.amount)
        
        # Reimbursable vs non-reimbursable
        reimbursable_amount = sum(exp.amount for exp in expenses if exp.is_reimbursable)
        non_reimbursable_amount = total_amount - reimbursable_amount
        
        # Average expense amount
        avg_expense = total_amount / total_expenses if total_expenses > 0 else 0
        
        return {
            "total_expenses": total_expenses,
            "total_amount": float(total_amount),
            "approved_expenses": approved_expenses,
            "approved_amount": float(approved_amount),
            "paid_expenses": paid_expenses,
            "paid_amount": float(paid_amount),
            "approval_rate": (approved_expenses / total_expenses * 100) if total_expenses > 0 else 0,
            "average_expense": float(avg_expense),
            "by_category": by_category,
            "reimbursable_amount": float(reimbursable_amount),
            "non_reimbursable_amount": float(non_reimbursable_amount),
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def get_employee_expenses(
        self,
        employee_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get expense summary for a specific employee
        
        Args:
            employee_id: Employee UUID
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            Employee expense summary
        """
        expenses = await self.get_expenses(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        total_amount = sum(exp.amount for exp in expenses)
        reimbursable_amount = sum(exp.amount for exp in expenses if exp.is_reimbursable)
        pending_amount = sum(exp.amount for exp in expenses if exp.status == ExpenseStatus.PENDING)
        
        return {
            "employee_id": str(employee_id),
            "total_expenses": len(expenses),
            "total_amount": float(total_amount),
            "reimbursable_amount": float(reimbursable_amount),
            "pending_amount": float(pending_amount),
            "expenses": expenses
        }
    
    async def _generate_expense_reference(self) -> str:
        """Generate unique expense reference"""
        now = datetime.now()
        prefix = f"EXP-{now.year}{now.month:02d}"
        
        # Get last expense reference for this month
        last_expense = self.session.exec(
            select(Expense)
            .where(Expense.expense_reference.like(f"{prefix}%"))
            .order_by(Expense.expense_reference.desc())
        ).first()
        
        if last_expense:
            # Extract sequence number and increment
            last_seq = int(last_expense.expense_reference.split('-')[-1])
            seq = last_seq + 1
        else:
            seq = 1
        
        return f"{prefix}-{seq:04d}"
    
    def _to_response(self, expense: Expense) -> ExpenseResponse:
        """Convert expense model to response schema"""
        return ExpenseResponse(
            id=expense.id,
            expense_reference=expense.expense_reference,
            category=expense.category,
            description=expense.description,
            amount=expense.amount,
            currency=expense.currency,
            expense_date=expense.expense_date,
            vendor=expense.vendor,
            receipt_number=expense.receipt_number,
            status=expense.status,
            notes=expense.notes,
            employee_id=expense.employee_id,
            project_id=expense.project_id,
            is_reimbursable=expense.is_reimbursable,
            approved_by=expense.approved_by,
            approved_at=expense.approved_at,
            rejected_by=expense.rejected_by,
            rejected_at=expense.rejected_at,
            paid_at=expense.paid_at,
            receipt_path=expense.receipt_path,
            created_at=expense.created_at,
            updated_at=expense.updated_at
        )