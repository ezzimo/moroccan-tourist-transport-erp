"""
Invoice PDF generation utilities
"""
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime, date
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import logging

logger = logging.getLogger(__name__)


class InvoicePDFGenerator:
    """Professional invoice PDF generator for Moroccan tourist transport"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for invoice"""
        # Company header style
        self.styles.add(ParagraphStyle(
            name='CompanyHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Invoice title style
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkred
        ))
        
        # Address style
        self.styles.add(ParagraphStyle(
            name='Address',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            alignment=TA_LEFT
        ))
    
    def generate_invoice_pdf(self, invoice_data: Dict[str, Any]) -> bytes:
        """Generate invoice PDF from invoice data
        
        Args:
            invoice_data: Dictionary containing invoice information
            
        Returns:
            PDF content as bytes
        """
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
            
            # Build PDF content
            story = []
            
            # Company header
            story.append(Paragraph(
                "Moroccan Tourist Transport Company",
                self.styles['CompanyHeader']
            ))
            
            # Invoice title and number
            story.append(Paragraph(
                f"INVOICE #{invoice_data.get('invoice_number', 'N/A')}",
                self.styles['InvoiceTitle']
            ))
            
            story.append(Spacer(1, 20))
            
            # Invoice details table
            invoice_details = [
                ['Invoice Date:', invoice_data.get('issue_date', 'N/A')],
                ['Due Date:', invoice_data.get('due_date', 'N/A')],
                ['Customer:', invoice_data.get('customer_name', 'N/A')],
                ['Status:', invoice_data.get('status', 'N/A')]
            ]
            
            details_table = Table(invoice_details, colWidths=[2*inch, 3*inch])
            details_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(details_table)
            story.append(Spacer(1, 30))
            
            # Invoice items
            if 'items' in invoice_data and invoice_data['items']:
                story.append(Paragraph("Invoice Items", self.styles['Heading3']))
                story.append(Spacer(1, 12))
                
                # Items table header
                items_data = [['Description', 'Quantity', 'Unit Price', 'Total']]
                
                # Add items
                for item in invoice_data['items']:
                    items_data.append([
                        item.get('description', ''),
                        str(item.get('quantity', 0)),
                        f"{item.get('unit_price', 0):.2f} MAD",
                        f"{item.get('total', 0):.2f} MAD"
                    ])
                
                items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
                items_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(items_table)
                story.append(Spacer(1, 20))
            
            # Totals
            totals_data = []
            
            if 'subtotal' in invoice_data:
                totals_data.append(['Subtotal:', f"{invoice_data['subtotal']:.2f} MAD"])
            
            if 'tax_amount' in invoice_data:
                tax_rate = invoice_data.get('tax_rate', 20)
                totals_data.append([f'Tax ({tax_rate}%):', f"{invoice_data['tax_amount']:.2f} MAD"])
            
            if 'discount_amount' in invoice_data and invoice_data['discount_amount'] > 0:
                totals_data.append(['Discount:', f"-{invoice_data['discount_amount']:.2f} MAD"])
            
            if 'total_amount' in invoice_data:
                totals_data.append(['Total:', f"{invoice_data['total_amount']:.2f} MAD"])
            
            if totals_data:
                totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
                totals_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
                ]))
                
                story.append(totals_table)
            
            # Footer
            story.append(Spacer(1, 50))
            story.append(Paragraph(
                "Thank you for your business!",
                self.styles['Normal']
            ))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF content
            pdf_content = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Generated PDF for invoice {invoice_data.get('invoice_number', 'N/A')}")
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error generating invoice PDF: {str(e)}")
            raise


# Convenience function for backward compatibility
def generate_invoice_pdf(invoice_data: Dict[str, Any]) -> bytes:
    """Generate invoice PDF - convenience function
    
    Args:
        invoice_data: Invoice data dictionary
        
    Returns:
        PDF content as bytes
    """
    generator = InvoicePDFGenerator()
    return generator.generate_invoice_pdf(invoice_data)


def generate_invoice_summary_report(invoices: List[Dict[str, Any]]) -> bytes:
    """Generate invoice summary report
    
    Args:
        invoices: List of invoice data
        
    Returns:
        PDF report as bytes
    """
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Report header
        story.append(Paragraph("Invoice Summary Report", styles['Title']))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary table
        if invoices:
            total_amount = sum(inv.get('total_amount', 0) for inv in invoices)
            paid_amount = sum(inv.get('total_amount', 0) for inv in invoices if inv.get('status') == 'paid')
            pending_amount = total_amount - paid_amount
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total Invoices', str(len(invoices))],
                ['Total Amount', f"{total_amount:.2f} MAD"],
                ['Paid Amount', f"{paid_amount:.2f} MAD"],
                ['Pending Amount', f"{pending_amount:.2f} MAD"]
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
        
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
        
    except Exception as e:
        logger.error(f"Error generating invoice summary report: {str(e)}")
        raise