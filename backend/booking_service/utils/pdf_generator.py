"""
Lazy PDF generator for booking vouchers using ReportLab.
Uses lazy import pattern to avoid startup crashes when reportlab is missing.
"""
import io
import logging
from typing import BinaryIO, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Global flag set once we attempt to import
_reportlab_available: Optional[bool] = None


def have_reportlab() -> bool:
    """Check if ReportLab is available (cached check)"""
    global _reportlab_available
    
    if _reportlab_available is not None:
        return _reportlab_available
    
    try:
        import reportlab
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        _reportlab_available = True
        logger.info("ReportLab successfully imported and available")
        return True
    except ImportError as e:
        _reportlab_available = False
        logger.warning("ReportLab not available: %s", e)
        return False


def generate_booking_voucher(booking: Dict[str, Any], stream: BinaryIO) -> None:
    """
    Generate a booking voucher PDF and write to stream.
    
    Args:
        booking: Booking data dictionary
        stream: Binary stream to write PDF to
        
    Raises:
        ImportError: If ReportLab is not available
        Exception: If PDF generation fails
    """
    if not have_reportlab():
        raise ImportError("ReportLab is not installed")
    
    try:
        # Import here to avoid startup issues
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor
        
        # Create PDF
        c = canvas.Canvas(stream, pagesize=letter)
        width, height = letter
        
        # Colors
        primary_color = HexColor('#f97316')  # Orange
        text_color = HexColor('#1f2937')     # Gray-800
        
        # Header
        c.setFillColor(primary_color)
        c.rect(0, height - 2*inch, width, 2*inch, fill=1)
        
        c.setFillColor(HexColor('#ffffff'))
        c.setFont("Helvetica-Bold", 24)
        c.drawString(inch, height - 1.2*inch, "BOOKING VOUCHER")
        
        c.setFont("Helvetica", 12)
        c.drawString(inch, height - 1.5*inch, "Moroccan Tourist Transport ERP")
        
        # Booking details
        c.setFillColor(text_color)
        y_position = height - 3*inch
        
        # Basic booking info
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, y_position, f"Booking Reference: {booking.get('id', 'N/A')}")
        y_position -= 0.3*inch
        
        c.setFont("Helvetica", 12)
        details = [
            f"Service Type: {booking.get('service_type', 'N/A')}",
            f"Customer: {booking.get('lead_passenger_name', 'N/A')}",
            f"Email: {booking.get('lead_passenger_email', 'N/A')}",
            f"Phone: {booking.get('lead_passenger_phone', 'N/A')}",
            f"Passengers: {booking.get('pax_count', 'N/A')}",
            f"Start Date: {booking.get('start_date', 'N/A')}",
            f"End Date: {booking.get('end_date', 'Not specified')}",
            f"Status: {booking.get('status', 'N/A')}",
            f"Total Price: {booking.get('total_price', 'N/A')} {booking.get('currency', 'MAD')}",
        ]
        
        for detail in details:
            c.drawString(inch, y_position, detail)
            y_position -= 0.25*inch
        
        # Special requests
        if booking.get('special_requests'):
            y_position -= 0.2*inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(inch, y_position, "Special Requests:")
            y_position -= 0.2*inch
            c.setFont("Helvetica", 10)
            
            # Wrap text for special requests
            requests_text = str(booking['special_requests'])
            max_chars = 80
            lines = [requests_text[i:i+max_chars] for i in range(0, len(requests_text), max_chars)]
            
            for line in lines[:5]:  # Limit to 5 lines
                c.drawString(inch, y_position, line)
                y_position -= 0.15*inch
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(inch, inch, f"Generated on: {booking.get('created_at', 'N/A')}")
        c.drawString(inch, inch - 0.15*inch, "Thank you for choosing our services!")
        
        # Save PDF
        c.save()
        logger.info("PDF voucher generated successfully for booking %s", booking.get('id'))
        
    except Exception as e:
        logger.error("Failed to generate PDF voucher for booking %s: %s", booking.get('id'), e)
        raise