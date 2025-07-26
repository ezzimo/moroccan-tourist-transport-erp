"""
Payment service for payment processing operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.payment import Payment, PaymentStatus, PaymentMethod
from models.invoice import Invoice, InvoiceStatus
from schemas.payment import (
    PaymentCreate, PaymentUpdate, PaymentResponse
)
# from utils.currency import convert_currency
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
import logging

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for handling payment operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_payment(self, payment_data: PaymentCreate) -> PaymentResponse:
        """Create a new payment
        
        Args:
            payment_data: Payment creation data
            
        Returns:
            Created payment
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate invoice if provided
        invoice = None
        if payment_data.invoice_id:
            invoice = self.session.get(Invoice, payment_data.invoice_id)
            if not invoice:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invoice not found"
                )
            
            if invoice.status == InvoiceStatus.PAID:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invoice is already paid"
                )
        
        # Generate payment reference
        payment_reference = await self._generate_payment_reference()
        
        # Create payment
        payment = Payment(
            payment_reference=payment_reference,
            invoice_id=payment_data.invoice_id,
            customer_id=payment_data.customer_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            payment_method=payment_data.payment_method,
            payment_date=payment_data.payment_date or date.today(),
            status=PaymentStatus.PENDING,
            description=payment_data.description,
            transaction_id=payment_data.transaction_id,
            gateway_response=payment_data.gateway_response
        )
        
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        
        logger.info(f"Created payment {payment.payment_reference}")
        return self._to_response(payment)
    
    async def get_payment(self, payment_id: uuid.UUID) -> PaymentResponse:
        """Get payment by ID
        
        Args:
            payment_id: Payment UUID
            
        Returns:
            Payment details
            
        Raises:
            HTTPException: If payment not found
        """
        payment = self.session.get(Payment, payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        return self._to_response(payment)
    
    async def get_payments(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[uuid.UUID] = None,
        invoice_id: Optional[uuid.UUID] = None,
        status: Optional[PaymentStatus] = None,
        payment_method: Optional[PaymentMethod] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[PaymentResponse]:
        """Get payments with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            customer_id: Filter by customer ID
            invoice_id: Filter by invoice ID
            status: Filter by payment status
            payment_method: Filter by payment method
            start_date: Filter payments from this date
            end_date: Filter payments until this date
            
        Returns:
            List of payments
        """
        query = select(Payment)
        
        # Apply filters
        conditions = []
        
        if customer_id:
            conditions.append(Payment.customer_id == customer_id)
        
        if invoice_id:
            conditions.append(Payment.invoice_id == invoice_id)
        
        if status:
            conditions.append(Payment.status == status)
        
        if payment_method:
            conditions.append(Payment.payment_method == payment_method)
        
        if start_date:
            conditions.append(Payment.payment_date >= start_date)
        
        if end_date:
            conditions.append(Payment.payment_date <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Payment.payment_date.desc()).offset(skip).limit(limit)
        payments = self.session.exec(query).all()
        
        return [self._to_response(payment) for payment in payments]
    
    async def update_payment(
        self, 
        payment_id: uuid.UUID, 
        payment_data: PaymentUpdate
    ) -> PaymentResponse:
        """Update payment information
        
        Args:
            payment_id: Payment UUID
            payment_data: Update data
            
        Returns:
            Updated payment
            
        Raises:
            HTTPException: If payment not found or cannot be updated
        """
        payment = self.session.get(Payment, payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Check if payment can be updated
        if payment.status in [PaymentStatus.COMPLETED, PaymentStatus.REFUNDED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update payment with status {payment.status}"
            )
        
        # Update fields
        update_data = payment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(payment, field, value)
        
        payment.updated_at = datetime.utcnow()
        
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        
        logger.info(f"Updated payment {payment.payment_reference}")
        return self._to_response(payment)
    
    async def confirm_payment(self, payment_id: uuid.UUID) -> dict:
        """Confirm a payment
        
        Args:
            payment_id: Payment UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If payment not found or cannot be confirmed
        """
        payment = self.session.get(Payment, payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        if payment.status != PaymentStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot confirm payment with status {payment.status}"
            )
        
        payment.status = PaymentStatus.COMPLETED
        payment.confirmed_at = datetime.utcnow()
        payment.updated_at = datetime.utcnow()
        
        # Update related invoice if exists
        if payment.invoice_id:
            invoice = self.session.get(Invoice, payment.invoice_id)
            if invoice and invoice.status != InvoiceStatus.PAID:
                # Check if payment covers full invoice amount
                total_payments = self.session.exec(
                    select(func.sum(Payment.amount))
                    .where(
                        and_(
                            Payment.invoice_id == payment.invoice_id,
                            Payment.status == PaymentStatus.COMPLETED
                        )
                    )
                ).first() or Decimal('0')
                
                if total_payments >= invoice.total_amount:
                    invoice.status = InvoiceStatus.PAID
                    invoice.paid_at = payment.payment_date
                    invoice.payment_method = payment.payment_method.value
                    self.session.add(invoice)
        
        self.session.add(payment)
        self.session.commit()
        
        logger.info(f"Confirmed payment {payment.payment_reference}")
        return {"message": "Payment confirmed successfully"}
    
    async def cancel_payment(self, payment_id: uuid.UUID, reason: Optional[str] = None) -> dict:
        """Cancel a payment
        
        Args:
            payment_id: Payment UUID
            reason: Cancellation reason
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If payment not found or cannot be cancelled
        """
        payment = self.session.get(Payment, payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        if payment.status != PaymentStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel payment with status {payment.status}"
            )
        
        payment.status = PaymentStatus.CANCELLED
        payment.cancelled_at = datetime.utcnow()
        if reason:
            payment.description = f"{payment.description or ''}\nCancelled: {reason}"
        payment.updated_at = datetime.utcnow()
        
        self.session.add(payment)
        self.session.commit()
        
        logger.info(f"Cancelled payment {payment.payment_reference}")
        return {"message": "Payment cancelled successfully"}
    
    async def refund_payment(
        self, 
        payment_id: uuid.UUID, 
        refund_amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> dict:
        """Refund a payment
        
        Args:
            payment_id: Payment UUID
            refund_amount: Amount to refund (full amount if not specified)
            reason: Refund reason
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If payment not found or cannot be refunded
        """
        payment = self.session.get(Payment, payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        if payment.status != PaymentStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only refund completed payments"
            )
        
        refund_amount = refund_amount or payment.amount
        
        if refund_amount > payment.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund amount cannot exceed payment amount"
            )
        
        # Create refund payment record
        refund_reference = await self._generate_payment_reference("REF")
        
        refund_payment = Payment(
            payment_reference=refund_reference,
            invoice_id=payment.invoice_id,
            customer_id=payment.customer_id,
            amount=-refund_amount,  # Negative amount for refund
            currency=payment.currency,
            payment_method=payment.payment_method,
            payment_date=date.today(),
            status=PaymentStatus.COMPLETED,
            description=f"Refund for {payment.payment_reference}: {reason or 'No reason provided'}",
            parent_payment_id=payment.id
        )
        
        self.session.add(refund_payment)
        
        # Update original payment status if fully refunded
        if refund_amount == payment.amount:
            payment.status = PaymentStatus.REFUNDED
            payment.refunded_at = datetime.utcnow()
            payment.updated_at = datetime.utcnow()
            self.session.add(payment)
        
        self.session.commit()
        
        logger.info(f"Refunded payment {payment.payment_reference} - Amount: {refund_amount}")
        return {
            "message": "Payment refunded successfully",
            "refund_reference": refund_reference,
            "refund_amount": float(refund_amount)
        }
    
    async def get_payment_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get payment analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Analytics data
        """
        query = select(Payment)
        
        conditions = []
        if start_date:
            conditions.append(Payment.payment_date >= start_date)
        if end_date:
            conditions.append(Payment.payment_date <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        payments = self.session.exec(query).all()
        
        # Calculate metrics
        total_payments = len(payments)
        total_amount = sum(p.amount for p in payments if p.amount > 0)  # Exclude refunds
        completed_payments = len([p for p in payments if p.status == PaymentStatus.COMPLETED])
        completed_amount = sum(p.amount for p in payments if p.status == PaymentStatus.COMPLETED and p.amount > 0)
        
        # Payment methods breakdown
        by_method = {}
        for payment in payments:
            if payment.amount > 0:  # Exclude refunds
                method = payment.payment_method.value
                by_method[method] = by_method.get(method, 0) + float(payment.amount)
        
        # Success rate
        success_rate = (completed_payments / total_payments * 100) if total_payments > 0 else 0
        
        # Average payment amount
        avg_payment = completed_amount / completed_payments if completed_payments > 0 else 0
        
        return {
            "total_payments": total_payments,
            "total_amount": float(total_amount),
            "completed_payments": completed_payments,
            "completed_amount": float(completed_amount),
            "success_rate": success_rate,
            "average_payment": float(avg_payment),
            "by_payment_method": by_method,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def _generate_payment_reference(self, prefix: str = "PAY") -> str:
        """Generate unique payment reference"""
        now = datetime.now()
        date_part = f"{now.year}{now.month:02d}{now.day:02d}"
        
        # Get last payment reference for today
        last_payment = self.session.exec(
            select(Payment)
            .where(Payment.payment_reference.like(f"{prefix}-{date_part}%"))
            .order_by(Payment.payment_reference.desc())
        ).first()
        
        if last_payment:
            # Extract sequence number and increment
            last_seq = int(last_payment.payment_reference.split('-')[-1])
            seq = last_seq + 1
        else:
            seq = 1
        
        return f"{prefix}-{date_part}-{seq:04d}"
    
    def _to_response(self, payment: Payment) -> PaymentResponse:
        """Convert payment model to response schema"""
        return PaymentResponse(
            id=payment.id,
            payment_reference=payment.payment_reference,
            invoice_id=payment.invoice_id,
            customer_id=payment.customer_id,
            amount=payment.amount,
            currency=payment.currency,
            payment_method=payment.payment_method,
            payment_date=payment.payment_date,
            status=payment.status,
            description=payment.description,
            transaction_id=payment.transaction_id,
            gateway_response=payment.gateway_response,
            confirmed_at=payment.confirmed_at,
            cancelled_at=payment.cancelled_at,
            refunded_at=payment.refunded_at,
            parent_payment_id=payment.parent_payment_id,
            created_at=payment.created_at,
            updated_at=payment.updated_at
        )