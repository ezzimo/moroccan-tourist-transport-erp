"""
PDF generation utilities for booking vouchers
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import qrcode
from io import BytesIO
from datetime import datetime
from config import settings
from models import Booking
from typing import List, Optional
import uuid


def generate_qr_code(data: str) -> BytesIO:
    """Generate QR code for booking reference"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    return img_buffer


def generate_booking_voucher(
    booking: Booking, reservation_items: List = None
) -> BytesIO:
    """Generate PDF voucher for booking"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#2E86AB"),
    )

    header_style = ParagraphStyle(
        "CustomHeader",
        parent=styles["Heading2"],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor("#2E86AB"),
    )

    normal_style = styles["Normal"]

    # Company Header
    elements.append(Paragraph(settings.company_name, title_style))
    elements.append(Paragraph(f"{settings.company_address}", normal_style))
    elements.append(
        Paragraph(
            f"Phone: {settings.company_phone} | Email: {settings.company_email}",
            normal_style,
        )
    )
    elements.append(Spacer(1, 20))

    # Voucher Title
    elements.append(Paragraph("BOOKING VOUCHER", title_style))
    elements.append(Spacer(1, 20))

    # Booking Information Table
    booking_data = [
        ["Booking Reference:", str(booking.id)],
        ["Service Type:", booking.service_type.value],
        ["Status:", booking.status.value],
        ["Booking Date:", booking.created_at.strftime("%Y-%m-%d %H:%M")],
        ["Travel Date:", booking.start_date.strftime("%Y-%m-%d")],
    ]

    if booking.end_date:
        booking_data.append(["Return Date:", booking.end_date.strftime("%Y-%m-%d")])

    booking_table = Table(booking_data, colWidths=[2 * inch, 4 * inch])
    booking_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F8FF")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    elements.append(Paragraph("Booking Details", header_style))
    elements.append(booking_table)
    elements.append(Spacer(1, 20))

    # Customer Information
    customer_data = [
        ["Lead Passenger:", booking.lead_passenger_name],
        ["Email:", booking.lead_passenger_email],
        ["Phone:", booking.lead_passenger_phone],
        ["Passengers:", str(booking.pax_count)],
    ]

    customer_table = Table(customer_data, colWidths=[2 * inch, 4 * inch])
    customer_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F8FF")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    elements.append(Paragraph("Customer Information", header_style))
    elements.append(customer_table)
    elements.append(Spacer(1, 20))

    # Reservation Items (if provided)
    if reservation_items:
        elements.append(Paragraph("Services Included", header_style))

        items_data = [["Service", "Quantity", "Unit Price", "Total"]]
        for item in reservation_items:
            items_data.append(
                [
                    item.name,
                    str(item.quantity),
                    f"{item.unit_price} {booking.currency}",
                    f"{item.total_price} {booking.currency}",
                ]
            )

        items_table = Table(
            items_data, colWidths=[3 * inch, 1 * inch, 1 * inch, 1 * inch]
        )
        items_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86AB")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        elements.append(items_table)
        elements.append(Spacer(1, 20))

    # Pricing Information
    pricing_data = [
        ["Base Price:", f"{booking.base_price} {booking.currency}"],
        ["Discount:", f"-{booking.discount_amount} {booking.currency}"],
        ["Total Amount:", f"{booking.total_price} {booking.currency}"],
        ["Payment Status:", booking.payment_status.value],
    ]

    pricing_table = Table(pricing_data, colWidths=[2 * inch, 2 * inch])
    pricing_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F8FF")),
                ("BACKGROUND", (0, -2), (-1, -1), colors.HexColor("#E6F3FF")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTNAME", (0, -2), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    elements.append(Paragraph("Payment Information", header_style))
    elements.append(pricing_table)
    elements.append(Spacer(1, 20))

    # Special Requests
    if booking.special_requests:
        elements.append(Paragraph("Special Requests", header_style))
        elements.append(Paragraph(booking.special_requests, normal_style))
        elements.append(Spacer(1, 20))

    # QR Code
    qr_data = f"Booking: {booking.id}"
    qr_buffer = generate_qr_code(qr_data)

    # Add QR code image
    elements.append(Paragraph("Booking QR Code", header_style))
    qr_image = Image(qr_buffer, width=1.5 * inch, height=1.5 * inch)
    elements.append(qr_image)
    elements.append(Spacer(1, 20))

    # Footer
    footer_text = """
    <para align=center>
    <b>Important Notes:</b><br/>
    • Please present this voucher at the time of service<br/>
    • Contact us immediately for any changes or cancellations<br/>
    • Terms and conditions apply<br/><br/>
    Thank you for choosing {company_name}!
    </para>
    """.format(
        company_name=settings.company_name
    )

    elements.append(Paragraph(footer_text, normal_style))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    return buffer
