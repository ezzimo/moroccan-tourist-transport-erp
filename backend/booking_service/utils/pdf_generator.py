"""
PDF generation utilities for booking vouchers and receipts
"""
import io
import logging
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ReportLab not available: {e}")
    REPORTLAB_AVAILABLE = False

try:
    import qrcode
    from PIL import Image as PILImage
    QR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"QR code generation not available: {e}")
    QR_AVAILABLE = False


logger = logging.getLogger(__name__)


class PDFGenerator:
    """PDF generation service for booking vouchers and receipts"""
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "ReportLab is required for PDF generation. "
                "Install with: pip install reportlab pillow"
            )
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#f97316')  # Orange color
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#1f2937')  # Dark gray
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
    
    def generate_booking_voucher(self, booking_data: Dict[str, Any]) -> bytes:
        """Generate a booking voucher PDF"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build the PDF content
            story = []
            
            # Header
            story.append(Paragraph("BOOKING VOUCHER", self.styles['CustomTitle']))
            story.append(Spacer(1, 12))
            
            # Company info
            company_info = [
                ["Atlas Tours Morocco", ""],
                ["Casablanca, Morocco", f"Voucher #: {booking_data.get('id', 'N/A')}"],
                ["Phone: +212 522 123 456", f"Date: {datetime.now().strftime('%Y-%m-%d')}"],
                ["Email: info@atlastours.ma", ""]
            ]
            
            company_table = Table(company_info, colWidths=[3*inch, 3*inch])
            company_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(company_table)
            story.append(Spacer(1, 20))
            
            # Booking details
            story.append(Paragraph("Booking Details", self.styles['CustomHeading']))
            
            booking_details = [
                ["Service Type:", booking_data.get('service_type', 'N/A')],
                ["Lead Passenger:", booking_data.get('lead_passenger_name', 'N/A')],
                ["Email:", booking_data.get('lead_passenger_email', 'N/A')],
                ["Phone:", booking_data.get('lead_passenger_phone', 'N/A')],
                ["Passengers:", str(booking_data.get('pax_count', 0))],
                ["Start Date:", booking_data.get('start_date', 'N/A')],
                ["End Date:", booking_data.get('end_date', 'N/A') or 'Same day'],
                ["Status:", booking_data.get('status', 'N/A')],
            ]
            
            details_table = Table(booking_details, colWidths=[2*inch, 4*inch])
            details_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(details_table)
            story.append(Spacer(1, 20))
            
            # Pricing information
            story.append(Paragraph("Pricing Information", self.styles['CustomHeading']))
            
            pricing_data = [
                ["Base Price:", f"{booking_data.get('base_price', 0):.2f} {booking_data.get('currency', 'MAD')}"],
                ["Discount:", f"-{booking_data.get('discount_amount', 0):.2f} {booking_data.get('currency', 'MAD')}"],
                ["Total Amount:", f"{booking_data.get('total_price', 0):.2f} {booking_data.get('currency', 'MAD')}"],
                ["Payment Status:", booking_data.get('payment_status', 'Pending')],
            ]
            
            pricing_table = Table(pricing_data, colWidths=[2*inch, 4*inch])
            pricing_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (-2, -1), (-1, -1), colors.HexColor('#f3f4f6')),
                ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            story.append(pricing_table)
            story.append(Spacer(1, 20))
            
            # Special requests
            if booking_data.get('special_requests'):
                story.append(Paragraph("Special Requests", self.styles['CustomHeading']))
                story.append(Paragraph(booking_data['special_requests'], self.styles['CustomBody']))
                story.append(Spacer(1, 20))
            
            # QR Code (if available)
            if QR_AVAILABLE:
                try:
                    qr_data = f"Booking ID: {booking_data.get('id', 'N/A')}"
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    qr_buffer = io.BytesIO()
                    qr_img.save(qr_buffer, format='PNG')
                    qr_buffer.seek(0)
                    
                    # Add QR code to PDF
                    story.append(Paragraph("Booking QR Code", self.styles['CustomHeading']))
                    # Note: In production, you'd save the QR image temporarily and reference it
                    story.append(Paragraph("QR Code for mobile verification", self.styles['CustomBody']))
                    story.append(Spacer(1, 20))
                except Exception as qr_error:
                    logger.warning(f"QR code generation failed: {qr_error}")
            
            # Footer
            story.append(Spacer(1, 30))
            story.append(Paragraph(
                "Thank you for choosing Atlas Tours Morocco!<br/>"
                "For any questions, please contact us at info@atlastours.ma",
                self.styles['CustomBody']
            ))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate PDF voucher: {str(e)}"
            )
    
    def generate_simple_receipt(self, booking_data: Dict[str, Any]) -> bytes:
        """Generate a simple text-based receipt if ReportLab fails"""
        try:
            receipt_text = f"""
ATLAS TOURS MOROCCO
Booking Receipt

Booking ID: {booking_data.get('id', 'N/A')}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Customer Information:
- Name: {booking_data.get('lead_passenger_name', 'N/A')}
- Email: {booking_data.get('lead_passenger_email', 'N/A')}
- Phone: {booking_data.get('lead_passenger_phone', 'N/A')}

Booking Details:
- Service: {booking_data.get('service_type', 'N/A')}
- Passengers: {booking_data.get('pax_count', 0)}
- Start Date: {booking_data.get('start_date', 'N/A')}
- End Date: {booking_data.get('end_date', 'Same day')}
- Status: {booking_data.get('status', 'N/A')}

Pricing:
- Base Price: {booking_data.get('base_price', 0):.2f} {booking_data.get('currency', 'MAD')}
- Discount: -{booking_data.get('discount_amount', 0):.2f} {booking_data.get('currency', 'MAD')}
- Total: {booking_data.get('total_price', 0):.2f} {booking_data.get('currency', 'MAD')}
- Payment Status: {booking_data.get('payment_status', 'Pending')}

Special Requests:
{booking_data.get('special_requests', 'None')}

Thank you for choosing Atlas Tours Morocco!
Contact: info@atlastours.ma | +212 522 123 456
            """
            return receipt_text.encode('utf-8')
            
        except Exception as e:
            logger.error(f"Simple receipt generation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate receipt: {str(e)}"
            )


# Global PDF generator instance
pdf_generator = None

def get_pdf_generator() -> PDFGenerator:
    """Get PDF generator instance"""
    global pdf_generator
    if pdf_generator is None:
        try:
            pdf_generator = PDFGenerator()
        except ImportError as e:
            logger.error(f"PDF generator initialization failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="PDF generation service unavailable"
            )
    return pdf_generator