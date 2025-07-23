"""
Invoice service for invoice management operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.invoice import Invoice, InvoiceStatus, PaymentStatus
from models.invoice_item import InvoiceItem
from schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceSummary,
    InvoiceSearch, InvoiceGeneration, InvoiceItemResponse
)
from utils.pagination import PaginationParams, paginate_query
from utils.invoice_generator import InvoiceGenerator, InvoiceNumberGenerator
from utils.currency import CurrencyConverter
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import redis
import uuid
import httpx
from io import BytesIO


class InvoiceService:
    """Service for handling invoice operations"""
    
    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client
        self.currency_converter = CurrencyConverter(redis_client)
        self.invoice_generator = InvoiceGenerator(session)
    
    async def create_invoice(self, invoice_data: InvoiceCreate, created_by: uuid.UUID) -> InvoiceResponse:
        """Create a new invoice"""
        # Generate invoice number
        invoice_number = InvoiceNumberGenerator.generate()
        
        # Calculate due date if not provided
        due_date = invoice_data.due_date
        if not due_date:
            from config import settings
            due_date = date.today() + timedelta(days=settings.invoice_due_days)
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            booking_id=invoice_data.booking_id,
            customer_id=invoice_data.customer_id,
            customer_name=invoice_data.customer_name,
            customer_email=invoice_data.customer_email,
            customer_address=invoice_data.customer_address,
            customer_tax_id=invoice_data.customer_tax_id,
            currency=invoice_data.currency,
            tax_rate=invoice_data.tax_rate,
            tax_inclusive=invoice_data.tax_inclusive,
            due_date=due_date,
            payment_terms=invoice_data.payment_terms,
            description=invoice_data.description,
            notes=invoice_data.notes,
            discount_amount=invoice_data.discount_amount,
            created_by=created_by
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
                tax_rate=item_data.tax_rate,
                item_code=item_data.item_code,
                category=item_data.category
            )
            item.calculate_total()
            self.session.add(item)
        
        self.session.commit()
        self.session.refresh(invoice)
        
        # Calculate totals
        invoice.calculate_totals()
        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)
        
        return self._create_invoice_response(invoice)
    
    async def generate_from_booking(
        self, 
        generation_data: InvoiceGeneration, 
        created_by: uuid.UUID
    ) -> InvoiceResponse:
        """Generate invoice from booking"""
        # Get booking information
        booking_data = await self._get_booking_info(generation_data.booking_id)
        
        if not booking_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Check if invoice already exists for this booking
        existing_invoice = self.session.exec(
            select(Invoice).where(Invoice.booking_id == generation_data.booking_id)
        ).first()
        
        if existing_invoice:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice already exists for this booking"
            )
        
        # Generate invoice
        invoice = await self.invoice_generator.generate_from_booking(booking_data)
        invoice.created_by = created_by
        
        if generation_data.due_date:
            invoice.due_date = generation_data.due_date
        if generation_data.payment_terms:
            invoice.payment_terms = generation_data.payment_terms
        if generation_data.notes:
            invoice.notes = generation_data.notes
        
        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)
        
        # Send immediately if requested
        if generation_data.send_immediately:
            await self.send_invoice(invoice.id)
        
        return self._create_invoice_response(invoice)
    
    async def get_invoice(self, invoice_id: uuid.UUID) -> InvoiceResponse:
        """Get invoice by ID"""
        statement = select(Invoice).where(Invoice.id == invoice_id)
        invoice = self.session.exec(statement).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        return self._create_invoice_response(invoice)
    
    async def get_invoices(
        self, 
        pagination: PaginationParams,
        search: Optional[InvoiceSearch] = None
    ) -> Tuple[List[InvoiceResponse], int]:
        """Get list of invoices with optional search"""
        query = select(Invoice)
        
        # Apply search filters
        if search:
            conditions = []
            
            if search.query:
                search_term = f"%{search.query}%"
                conditions.append(
                    or_(
                        Invoice.invoice_number.ilike(search_term),
                        Invoice.customer_name.ilike(search_term),
                        Invoice.customer_email.ilike(search_term),
                        Invoice.description.ilike(search_term)
                    )
                )
            
            if search.customer_id:
                conditions.append(Invoice.customer_id == search.customer_id)
            
            if search.booking_id:
                conditions.append(Invoice.booking_id == search.booking_id)
            
            if search.status:
                conditions.append(Invoice.status == search.status)
            
            if search.payment_status:
                conditions.append(Invoice.payment_status == search.payment_status)
            
            if search.currency:
                conditions.append(Invoice.currency == search.currency)
            
            if search.issue_date_from:
                conditions.append(Invoice.issue_date >= search.issue_date_from)
            
            if search.issue_date_to:
                conditions.append(Invoice.issue_date <= search.issue_date_to)
            
            if search.due_date_from:
                conditions.append(Invoice.due_date >= search.due_date_from)
            
            if search.due_date_to:
                conditions.append(Invoice.due_date <= search.due_date_to)
            
            if search.amount_min:
                conditions.append(Invoice.total_amount >= search.amount_min)
            
            if search.amount_max:
                conditions.append(Invoice.total_amount <= search.amount_max)
            
            if search.is_overdue is not None:
                if search.is_overdue:
                    conditions.append(
                        and_(
                            Invoice.payment_status != PaymentStatus.PAID,
                            Invoice.due_date < date.today()
                        )
                    )
                else:
                    conditions.append(
                        or_(
                            Invoice.payment_status == PaymentStatus.PAID,
                            Invoice.due_date >= date.today()
                        )
                    )
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Order by issue date (newest first)
        query = query.order_by(Invoice.issue_date.desc())
        
        invoices, total = paginate_query(self.session, query, pagination)
        
        return [self._create_invoice_response(invoice) for invoice in invoices], total
    
    async def update_invoice(self, invoice_id: uuid.UUID, invoice_data: InvoiceUpdate) -> InvoiceResponse:
        """Update invoice information"""
        statement = select(Invoice).where(Invoice.id == invoice_id)
        invoice = self.session.exec(statement).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Check if invoice can be modified
        if invoice.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify paid or cancelled invoice"
            )
        
        # Update fields
        update_data = invoice_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        invoice.updated_at = datetime.utcnow()
        
        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)
        
        return self._create_invoice_response(invoice)
    
    async def send_invoice(self, invoice_id: uuid.UUID) -> InvoiceResponse:
        """Send invoice to customer"""
        statement = select(Invoice).where(Invoice.id == invoice_id)
        invoice = self.session.exec(statement).first()
        
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
        
        # Update invoice status
        invoice.status = InvoiceStatus.SENT
        invoice.sent_date = date.today()
        invoice.updated_at = datetime.utcnow()
        
        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)
        
        # TODO: Send email notification to customer
        
        return self._create_invoice_response(invoice)
    
    async def cancel_invoice(
        self, 
        invoice_id: uuid.UUID, 
        reason: str, 
        cancelled_by: uuid.UUID
    ) -> InvoiceResponse:
        """Cancel an invoice"""
        statement = select(Invoice).where(Invoice.id == invoice_id)
        invoice = self.session.exec(statement).first()
        
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
        
        # Update invoice status
        invoice.status = InvoiceStatus.CANCELLED
        invoice.payment_status = PaymentStatus.FAILED
        invoice.notes = f"{invoice.notes or ''}\n\nCancelled: {reason}".strip()
        invoice.updated_at = datetime.utcnow()
        
        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)
        
        return self._create_invoice_response(invoice)
    
    async def get_invoice_summary(self, days: int = 30) -> InvoiceSummary:
        """Get invoice summary statistics"""
        start_date = date.today() - timedelta(days=days)
        
        # Total invoices
        total_stmt = select(func.count(Invoice.id)).where(
            Invoice.issue_date >= start_date
        )
        total_invoices = self.session.exec(total_stmt).one()
        
        # Total amounts
        amount_stmt = select(
            func.sum(Invoice.total_amount),
            func.sum(Invoice.total_amount).filter(Invoice.payment_status == PaymentStatus.PAID),
            func.sum(Invoice.total_amount).filter(Invoice.payment_status != PaymentStatus.PAID)
        ).where(Invoice.issue_date >= start_date)
        
        total_amount, paid_amount, outstanding_amount = self.session.exec(amount_stmt).one()
        
        # Overdue amount
        overdue_stmt = select(func.sum(Invoice.total_amount)).where(
            and_(
                Invoice.payment_status != PaymentStatus.PAID,
                Invoice.due_date < date.today()
            )
        )
        overdue_amount = self.session.exec(overdue_stmt).one() or Decimal(0)
        
        # By status
        status_stmt = select(
            Invoice.status, func.count(Invoice.id)
        ).where(
            Invoice.issue_date >= start_date
        ).group_by(Invoice.status)
        
        by_status = {}
        for status_val, count in self.session.exec(status_stmt):
            by_status[status_val.value] = count
        
        # By currency
        currency_stmt = select(
            Invoice.currency, func.sum(Invoice.total_amount)
        ).where(
            Invoice.issue_date >= start_date
        ).group_by(Invoice.currency)
        
        by_currency = {}
        for currency, amount in self.session.exec(currency_stmt):
            by_currency[currency] = amount or Decimal(0)
        
        return InvoiceSummary(
            total_invoices=total_invoices,
            total_amount=total_amount or Decimal(0),
            paid_amount=paid_amount or Decimal(0),
            outstanding_amount=outstanding_amount or Decimal(0),
            overdue_amount=overdue_amount,
            by_status=by_status,
            by_currency=by_currency,
            average_payment_days=None  # TODO: Calculate from payment data
        )
    
    async def get_overdue_invoices(self) -> List[InvoiceResponse]:
        """Get all overdue invoices"""
        statement = select(Invoice).where(
            and_(
                Invoice.payment_status != PaymentStatus.PAID,
                Invoice.due_date < date.today()
            )
        ).order_by(Invoice.due_date)
        
        invoices = self.session.exec(statement).all()
        
        return [self._create_invoice_response(invoice) for invoice in invoices]
    
    async def bulk_send_invoices(self, invoice_ids: List[uuid.UUID]) -> dict:
        """Send multiple invoices at once"""
        statement = select(Invoice).where(Invoice.id.in_(invoice_ids))
        invoices = self.session.exec(statement).all()
        
        sent_count = 0
        for invoice in invoices:
            if invoice.status == InvoiceStatus.DRAFT:
                invoice.status = InvoiceStatus.SENT
                invoice.sent_date = date.today()
                invoice.updated_at = datetime.utcnow()
                self.session.add(invoice)
                sent_count += 1
        
        self.session.commit()
        
        return {
            "message": f"Successfully sent {sent_count} invoices",
            "sent_count": sent_count,
            "total_requested": len(invoice_ids)
        }
    
    async def generate_invoice_pdf(self, invoice: InvoiceResponse) -> BytesIO:
        """Generate PDF for invoice"""
        # TODO: Implement PDF generation using reportlab
        # This is a placeholder implementation
        pdf_content = f"Invoice {invoice.invoice_number}\nAmount: {invoice.total_amount} {invoice.currency}"
        
        buffer = BytesIO()
        buffer.write(pdf_content.encode())
        buffer.seek(0)
        
        return buffer
    
    async def _get_booking_info(self, booking_id: uuid.UUID) -> Optional[dict]:
        """Get booking information from booking service"""
        try:
            from config import settings
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.booking_service_url}/api/v1/bookings/{booking_id}"
                )
                if response.status_code == 200:
                    return response.json()
        except:
            pass
        return None
    
    def _create_invoice_response(self, invoice: Invoice) -> InvoiceResponse:
        """Create invoice response with calculated fields"""
        # Get invoice items
        items_stmt = select(InvoiceItem).where(InvoiceItem.invoice_id == invoice.id)
        items = self.session.exec(items_stmt).all()
        
        item_responses = []
        for item in items:
            item_responses.append(InvoiceItemResponse(
                id=item.id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_amount=item.total_amount,
                tax_rate=item.tax_rate,
                tax_amount=item.tax_amount,
                item_code=item.item_code,
                category=item.category
            ))
        
        return InvoiceResponse(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            booking_id=invoice.booking_id,
            customer_id=invoice.customer_id,
            customer_name=invoice.customer_name,
            customer_email=invoice.customer_email,
            customer_address=invoice.customer_address,
            customer_tax_id=invoice.customer_tax_id,
            subtotal=invoice.subtotal,
            tax_amount=invoice.tax_amount,
            discount_amount=invoice.discount_amount,
            total_amount=invoice.total_amount,
            currency=invoice.currency,
            tax_rate=invoice.tax_rate,
            tax_inclusive=invoice.tax_inclusive,
            status=invoice.status,
            payment_status=invoice.payment_status,
            issue_date=invoice.issue_date,
            due_date=invoice.due_date,
            sent_date=invoice.sent_date,
            paid_date=invoice.paid_date,
            payment_terms=invoice.payment_terms,
            payment_method=invoice.payment_method,
            description=invoice.description,
            notes=invoice.notes,
            created_by=invoice.created_by,
            approved_by=invoice.approved_by,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
            items=item_responses,
            paid_amount=invoice.get_paid_amount(),
            outstanding_amount=invoice.get_outstanding_amount(),
            is_overdue=invoice.is_overdue(),
            days_overdue=invoice.get_days_overdue()
        )