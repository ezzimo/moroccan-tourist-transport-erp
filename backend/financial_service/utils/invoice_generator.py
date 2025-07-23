"""
Invoice generation utilities
"""
from decimal import Decimal
from datetime import date, timedelta
from config import settings
from models.invoice import Invoice, InvoiceStatus
from models.invoice_item import InvoiceItem
from typing import Dict, Any, Optional
import uuid


class InvoiceNumberGenerator:
    """Generate unique invoice numbers"""
    
    @staticmethod
    def generate(year: int = None, sequence: int = None) -> str:
        """Generate invoice number in format: INV-YYYY-NNNNNN"""
        if year is None:
            year = date.today().year
        
        if sequence is None:
            # In production, get sequence from database
            sequence = 1
        
        return f"INV-{year}-{sequence:06d}"


class InvoiceGenerator:
    """Generate invoices from booking data"""
    
    def __init__(self, session):
        self.session = session
    
    async def generate_from_booking(self, booking_data: Dict[str, Any]) -> Invoice:
        """Generate invoice from booking information"""
        # Extract booking details
        booking_id = booking_data.get("id")
        customer_id = booking_data.get("customer_id")
        total_amount = Decimal(str(booking_data.get("total_price", 0)))
        currency = booking_data.get("currency", settings.default_currency)
        
        # Get customer information (would call CRM service in production)
        customer_info = await self._get_customer_info(customer_id)
        
        # Generate invoice number
        invoice_number = InvoiceNumberGenerator.generate()
        
        # Calculate due date
        due_date = date.today() + timedelta(days=settings.invoice_due_days)
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            booking_id=booking_id,
            customer_id=customer_id,
            customer_name=customer_info.get("name", "Unknown Customer"),
            customer_email=customer_info.get("email", ""),
            customer_address=customer_info.get("address"),
            customer_tax_id=customer_info.get("tax_id"),
            currency=currency,
            tax_rate=settings.vat_rate,
            due_date=due_date,
            description=f"Services for booking {booking_id}",
            status=InvoiceStatus.DRAFT
        )
        
        # Create invoice items from booking items
        items = await self._create_invoice_items(booking_data, invoice.id)
        invoice.invoice_items = items
        
        # Calculate totals
        invoice.calculate_totals()
        
        return invoice
    
    async def _get_customer_info(self, customer_id: uuid.UUID) -> Dict[str, Any]:
        """Get customer information from CRM service"""
        # Mock implementation - in production, call CRM service
        return {
            "name": "Sample Customer",
            "email": "customer@example.com",
            "address": "Casablanca, Morocco",
            "tax_id": None
        }
    
    async def _create_invoice_items(self, booking_data: Dict[str, Any], invoice_id: uuid.UUID) -> list:
        """Create invoice items from booking data"""
        items = []
        
        # Main service item
        main_item = InvoiceItem(
            invoice_id=invoice_id,
            description=f"Tour Service - {booking_data.get('service_type', 'Tour')}",
            quantity=Decimal("1"),
            unit_price=Decimal(str(booking_data.get("base_price", 0))),
            tax_rate=settings.vat_rate,
            category="Tour Services"
        )
        main_item.calculate_total()
        items.append(main_item)
        
        # Additional items from reservation items (if any)
        reservation_items = booking_data.get("reservation_items", [])
        for res_item in reservation_items:
            item = InvoiceItem(
                invoice_id=invoice_id,
                description=res_item.get("name", "Additional Service"),
                quantity=Decimal(str(res_item.get("quantity", 1))),
                unit_price=Decimal(str(res_item.get("unit_price", 0))),
                tax_rate=settings.vat_rate,
                category=res_item.get("type", "Additional Services")
            )
            item.calculate_total()
            items.append(item)
        
        return items