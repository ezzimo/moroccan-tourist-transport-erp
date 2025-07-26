"""
Invoice service for invoice management operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.invoice import Invoice, InvoiceStatus
from models.invoice_item import InvoiceItem
from schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceResponse
)
from utils.invoice_generator import InvoicePDFGenerator, generate_invoice_pdf
# from utils.currency import convert_currency, get_exchange_rate
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
import logging

logger = logging.getLogger(__name__)


class InvoiceService:
    """Service for handling invoice operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.pdf_generator = InvoicePDFGenerator()
    
    async def create_invoice(self, invoice_data: InvoiceCreate) -> InvoiceResponse:
        """Create a new invoice
        
        Args:
            invoice_data: Invoice creation data
            
        Returns:
            Created invoice
            
        Raises:
            HTTPException: If validation fails
        """
        # Generate invoice number
        invoice_number = await self._generate_invoice_number()
        
        # Calculate totals
        subtotal = sum(item.quantity * item.unit_price for item in invoice_data.items)
        tax_amount = subtotal * (invoice_data.tax_rate / 100) if invoice_data.tax_rate else Decimal('0')
        discount_amount = subtotal * (invoice_data.discount_rate / 100) if invoice_data.discount_rate else Decimal('0')
        total_amount = subtotal + tax_amount - discount_amount
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            customer_id=invoice_data.customer_id,
            booking_id=invoice_data.booking_id,
            issue_date=invoice_data.issue_date or date.today(),
            due_date=invoice_data.due_date or (date.today() + timedelta(days=30)),
            currency=invoice_data.currency,
            subtotal=subtotal,
            tax_rate=invoice_data.tax_rate or Decimal('0'),
            tax_amount=tax_amount,
            discount_rate=invoice_data.discount_rate or Decimal('0'),
            discount_amount=discount_amount,
            total_amount=total_amount,
            status=InvoiceStatus.DRAFT,
            notes=invoice_data.notes
        )
        
        self.session.add(invoice)
        self.session.flush()  # Get invoice ID
        
        # Create invoice items
        for item_data in invoice_data.items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                description=item_data.description,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                total_price=item_data.quantity * item_data.unit_price,
                tax_rate=item_data.tax_rate or Decimal('0')
            )
            self.session.add(item)
        
        self.session.commit()
        self.session.refresh(invoice)
        
        logger.info(f"Created invoice {invoice.invoice_number}")
        return self._to_response(invoice)
    
    async def get_invoice(self, invoice_id: uuid.UUID) -> InvoiceResponse:
        """Get invoice by ID
        
        Args:
            invoice_id: Invoice UUID
            
        Returns:
            Invoice details
            
        Raises:
            HTTPException: If invoice not found
        """
        invoice = self.session.get(Invoice, invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        return self._to_response(invoice)
    
    async def get_invoices(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[uuid.UUID] = None,
        status: Optional[InvoiceStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        overdue_only: bool = False
    ) -> List[InvoiceResponse]:
        """Get invoices with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            customer_id: Filter by customer ID
            status: Filter by invoice status
            start_date: Filter invoices from this date
            end_date: Filter invoices until this date
            overdue_only: Show only overdue invoices
            
        Returns:
            List of invoices
        """
        query = select(Invoice)
        
        # Apply filters
        conditions = []
        
        if customer_id:
            conditions.append(Invoice.customer_id == customer_id)
        
        if status:
            conditions.append(Invoice.status == status)
        
        if start_date:
            conditions.append(Invoice.issue_date >= start_date)
        
        if end_date:
            conditions.append(Invoice.issue_date <= end_date)
        
        if overdue_only:
            conditions.extend([
                Invoice.due_date < date.today(),
                Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.OVERDUE])
            ])
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Invoice.issue_date.desc()).offset(skip).limit(limit)
        invoices = self.session.exec(query).all()
        
        return [self._to_response(invoice) for invoice in invoices]
    
    async def update_invoice(
        self, 
        invoice_id: uuid.UUID, 
        invoice_data: InvoiceUpdate
    ) -> InvoiceResponse:
        """Update invoice information
        
        Args:
            invoice_id: Invoice UUID
            invoice_data: Update data
            
        Returns:
            Updated invoice
            
        Raises:
            HTTPException: If invoice not found or cannot be updated
        """
        invoice = self.session.get(Invoice, invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Check if invoice can be updated
        if invoice.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update invoice with status {invoice.status}"
            )
        
        # Update fields
        update_data = invoice_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != "items":  # Handle items separately
                setattr(invoice, field, value)
        
        # Recalculate totals if items updated
        if "items" in update_data:
            # Delete existing items
            self.session.exec(
                select(InvoiceItem).where(InvoiceItem.invoice_id == invoice_id)
            ).delete()
            
            # Add new items
            subtotal = Decimal('0')
            for item_data in update_data["items"]:
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=item_data.description,
                    quantity=item_data.quantity,
                    unit_price=item_data.unit_price,
                    total_price=item_data.quantity * item_data.unit_price,
                    tax_rate=item_data.tax_rate or Decimal('0')
                )
                self.session.add(item)
                subtotal += item.total_price
            
            # Recalculate totals
            invoice.subtotal = subtotal
            invoice.tax_amount = subtotal * (invoice.tax_rate / 100)
            invoice.discount_amount = subtotal * (invoice.discount_rate / 100)
            invoice.total_amount = subtotal + invoice.tax_amount - invoice.discount_amount
        
        invoice.updated_at = datetime.utcnow()
        
        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)
        
        logger.info(f"Updated invoice {invoice.invoice_number}")
        return self._to_response(invoice)
    
    async def send_invoice(self, invoice_id: uuid.UUID) -> dict:
        """Send invoice to customer
        
        Args:
            invoice_id: Invoice UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If invoice not found or cannot be sent
        """
        invoice = self.session.get(Invoice, invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        if invoice.status != InvoiceStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft invoices can be sent"
            )
        
        # Generate PDF
        pdf_path = await generate_invoice_pdf(invoice)
        
        # Update status
        invoice.status = InvoiceStatus.SENT
        invoice.sent_at = datetime.utcnow()
        invoice.pdf_path = pdf_path
        invoice.updated_at = datetime.utcnow()
        
        self.session.add(invoice)
        self.session.commit()
        
        # TODO: Send email with PDF attachment
        
        logger.info(f"Sent invoice {invoice.invoice_number}")
        return {"message": "Invoice sent successfully"}
    
    async def mark_paid(
        self, 
        invoice_id: uuid.UUID, 
        payment_date: Optional[date] = None,
        payment_method: Optional[str] = None
    ) -> dict:
        """Mark invoice as paid
        
        Args:
            invoice_id: Invoice UUID
            payment_date: Date of payment
            payment_method: Payment method used
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If invoice not found or cannot be marked as paid
        """
        invoice = self.session.get(Invoice, invoice_id)
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
        
        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = payment_date or date.today()
        invoice.payment_method = payment_method
        invoice.updated_at = datetime.utcnow()
        
        self.session.add(invoice)
        self.session.commit()
        
        logger.info(f"Marked invoice {invoice.invoice_number} as paid")
        return {"message": "Invoice marked as paid"}
    
    async def cancel_invoice(self, invoice_id: uuid.UUID, reason: Optional[str] = None) -> dict:
        """Cancel an invoice
        
        Args:
            invoice_id: Invoice UUID
            reason: Cancellation reason
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If invoice not found or cannot be cancelled
        """
        invoice = self.session.get(Invoice, invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        if invoice.status == InvoiceStatus.PAID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel paid invoice"
            )
        
        invoice.status = InvoiceStatus.CANCELLED
        invoice.cancelled_at = datetime.utcnow()
        if reason:
            invoice.notes = f"{invoice.notes or ''}\nCancelled: {reason}"
        invoice.updated_at = datetime.utcnow()
        
        self.session.add(invoice)
        self.session.commit()
        
        logger.info(f"Cancelled invoice {invoice.invoice_number}")
        return {"message": "Invoice cancelled successfully"}
    
    async def get_overdue_invoices(self) -> List[InvoiceResponse]:
        """Get overdue invoices
        
        Returns:
            List of overdue invoices
        """
        return await self.get_invoices(overdue_only=True, limit=1000)
    
    async def get_invoice_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get invoice analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Analytics data
        """
        query = select(Invoice)
        
        conditions = []
        if start_date:
            conditions.append(Invoice.issue_date >= start_date)
        if end_date:
            conditions.append(Invoice.issue_date <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        invoices = self.session.exec(query).all()
        
        # Calculate metrics
        total_invoices = len(invoices)
        total_amount = sum(inv.total_amount for inv in invoices)
        paid_invoices = len([inv for inv in invoices if inv.status == InvoiceStatus.PAID])
        paid_amount = sum(inv.total_amount for inv in invoices if inv.status == InvoiceStatus.PAID)
        overdue_invoices = len([inv for inv in invoices if inv.is_overdue()])
        overdue_amount = sum(inv.total_amount for inv in invoices if inv.is_overdue())
        
        # Average payment time
        paid_with_dates = [inv for inv in invoices if inv.status == InvoiceStatus.PAID and inv.paid_at]
        avg_payment_days = None
        if paid_with_dates:
            payment_days = [(inv.paid_at - inv.issue_date).days for inv in paid_with_dates]
            avg_payment_days = sum(payment_days) / len(payment_days)
        
        return {
            "total_invoices": total_invoices,
            "total_amount": float(total_amount),
            "paid_invoices": paid_invoices,
            "paid_amount": float(paid_amount),
            "overdue_invoices": overdue_invoices,
            "overdue_amount": float(overdue_amount),
            "collection_rate": (paid_amount / total_amount * 100) if total_amount > 0 else 0,
            "average_payment_days": avg_payment_days,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def _generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        # Get current year and month
        now = datetime.now()
        prefix = f"INV-{now.year}{now.month:02d}"
        
        # Get last invoice number for this month
        last_invoice = self.session.exec(
            select(Invoice)
            .where(Invoice.invoice_number.like(f"{prefix}%"))
            .order_by(Invoice.invoice_number.desc())
        ).first()
        
        if last_invoice:
            # Extract sequence number and increment
            last_seq = int(last_invoice.invoice_number.split('-')[-1])
            seq = last_seq + 1
        else:
            seq = 1
        
        return f"{prefix}-{seq:04d}"
    
    def _to_response(self, invoice: Invoice) -> InvoiceResponse:
        """Convert invoice model to response schema"""
        return InvoiceResponse(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            customer_id=invoice.customer_id,
            booking_id=invoice.booking_id,
            issue_date=invoice.issue_date,
            due_date=invoice.due_date,
            currency=invoice.currency,
            subtotal=invoice.subtotal,
            tax_rate=invoice.tax_rate,
            tax_amount=invoice.tax_amount,
            discount_rate=invoice.discount_rate,
            discount_amount=invoice.discount_amount,
            total_amount=invoice.total_amount,
            status=invoice.status,
            notes=invoice.notes,
            pdf_path=invoice.pdf_path,
            sent_at=invoice.sent_at,
            paid_at=invoice.paid_at,
            cancelled_at=invoice.cancelled_at,
            payment_method=invoice.payment_method,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
            is_overdue=invoice.is_overdue(),
            days_overdue=invoice.days_overdue(),
            items=invoice.items or []
        )