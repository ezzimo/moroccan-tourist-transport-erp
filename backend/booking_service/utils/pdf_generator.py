"""
PDF generation utilities for booking vouchers and documents
Uses lazy imports to avoid startup crashes when reportlab is missing
"""
from typing import Any, Dict, BinaryIO
from datetime import datetime
import io


def _import_reportlab():
    """Lazy import of reportlab components"""
    try:
        from reportlab.lib.pagesizes import letter, A4  # type: ignore
        from reportlab.pdfgen import canvas            # type: ignore
        from reportlab.lib.units import cm             # type: ignore
        from reportlab.lib.colors import black, blue   # type: ignore
        from reportlab.lib.styles import getSampleStyleSheet  # type: ignore
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer  # type: ignore
        
        return {
            "letter": letter,
            "A4": A4,
            "canvas": canvas,
            "cm": cm,
            "black": black,
            "blue": blue,
            "getSampleStyleSheet": getSampleStyleSheet,
            "SimpleDocTemplate": SimpleDocTemplate,
            "Paragraph": Paragraph,
            "Spacer": Spacer,
        }
    except ImportError as e:
        raise ImportError("reportlab is not installed") from e


def have_reportlab() -> bool:
    """Check if reportlab is available"""
    try:
        _import_reportlab()
        return True
    except ImportError:
        return False


def generate_booking_voucher(booking: Dict[str, Any], stream: BinaryIO) -> None:
    """
    Generate a booking voucher PDF
    
    Args:
        booking: Booking data dictionary
        stream: Binary stream to write PDF to
    
    Raises:
        ImportError: If reportlab is not available
    """
    libs = _import_reportlab()
    
    # Extract reportlab components
    A4 = libs["A4"]
    canvas_class = libs["canvas"]
    cm = libs["cm"]
    black = libs["black"]
    blue = libs["blue"]
    
    # Create PDF canvas
    c = canvas_class.Canvas(stream, pagesize=A4)
    width, height = A4
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(blue)
    c.drawString(2*cm, height - 3*cm, "BOOKING VOUCHER")
    
    # Company info
    c.setFont("Helvetica", 12)
    c.setFillColor(black)
    c.drawString(2*cm, height - 4*cm, "Moroccan Tourist Transport ERP")
    c.drawString(2*cm, height - 4.5*cm, "Professional Tourism Services")
    
    # Booking details
    y_position = height - 6*cm
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, y_position, "Booking Details")
    y_position -= 1*cm
    
    c.setFont("Helvetica", 11)
    
    # Booking information
    booking_info = [
        ("Booking ID:", booking.get("id", "N/A")),
        ("Service Type:", booking.get("service_type", "N/A")),
        ("Lead Passenger:", booking.get("lead_passenger_name", "N/A")),
        ("Email:", booking.get("lead_passenger_email", "N/A")),
        ("Phone:", booking.get("lead_passenger_phone", "N/A")),
        ("Passengers:", str(booking.get("pax_count", 0))),
        ("Start Date:", booking.get("start_date", "N/A")),
        ("End Date:", booking.get("end_date", "N/A") if booking.get("end_date") else "Same day"),
        ("Total Price:", f"{booking.get('total_price', 0)} {booking.get('currency', 'MAD')}"),
        ("Status:", booking.get("status", "N/A")),
        ("Payment Status:", booking.get("payment_status", "N/A")),
    ]
    
    for label, value in booking_info:
        c.drawString(2*cm, y_position, f"{label}")
        c.drawString(6*cm, y_position, str(value))
        y_position -= 0.6*cm
    
    # Special requests
    if booking.get("special_requests"):
        y_position -= 0.5*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, y_position, "Special Requests:")
        y_position -= 0.6*cm
        
        c.setFont("Helvetica", 10)
        # Simple text wrapping for special requests
        special_requests = booking["special_requests"]
        max_width = 15*cm
        words = special_requests.split()
        line = ""
        
        for word in words:
            test_line = f"{line} {word}".strip()
            if c.stringWidth(test_line, "Helvetica", 10) < max_width:
                line = test_line
            else:
                if line:
                    c.drawString(2*cm, y_position, line)
                    y_position -= 0.5*cm
                line = word
        
        if line:
            c.drawString(2*cm, y_position, line)
            y_position -= 0.5*cm
    
    # Footer
    y_position = 3*cm
    c.setFont("Helvetica", 9)
    c.setFillColor(blue)
    c.drawString(2*cm, y_position, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(2*cm, y_position - 0.5*cm, "Thank you for choosing our services!")
    
    # Terms and conditions
    c.setFillColor(black)
    c.setFont("Helvetica", 8)
    terms_y = 2*cm
    c.drawString(2*cm, terms_y, "Terms & Conditions: This voucher is valid for the specified dates and services only.")
    c.drawString(2*cm, terms_y - 0.4*cm, "Please present this voucher at the time of service. Changes subject to availability.")
    
    # Save the PDF
    c.showPage()
    c.save()


def generate_booking_confirmation(booking: Dict[str, Any]) -> bytes:
    """
    Generate booking confirmation PDF and return as bytes
    
    Args:
        booking: Booking data dictionary
        
    Returns:
        bytes: PDF content as bytes
        
    Raises:
        ImportError: If reportlab is not available
    """
    buffer = io.BytesIO()
    generate_booking_voucher(booking, buffer)
    buffer.seek(0)
    return buffer.getvalue()


def generate_invoice_pdf(invoice: Dict[str, Any], stream: BinaryIO) -> None:
    """
    Generate an invoice PDF (placeholder implementation)
    
    Args:
        invoice: Invoice data dictionary
        stream: Binary stream to write PDF to
        
    Raises:
        ImportError: If reportlab is not available
    """
    libs = _import_reportlab()
    
    # Extract reportlab components
    A4 = libs["A4"]
    canvas_class = libs["canvas"]
    cm = libs["cm"]
    black = libs["black"]
    blue = libs["blue"]
    
    # Create PDF canvas
    c = canvas_class.Canvas(stream, pagesize=A4)
    width, height = A4
    
    # Simple invoice layout
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(blue)
    c.drawString(2*cm, height - 3*cm, "INVOICE")
    
    c.setFont("Helvetica", 12)
    c.setFillColor(black)
    c.drawString(2*cm, height - 5*cm, f"Invoice Number: {invoice.get('invoice_number', 'N/A')}")
    c.drawString(2*cm, height - 5.5*cm, f"Customer: {invoice.get('customer_name', 'N/A')}")
    c.drawString(2*cm, height - 6*cm, f"Total Amount: {invoice.get('total_amount', 0)} {invoice.get('currency', 'MAD')}")
    
    c.showPage()
    c.save()