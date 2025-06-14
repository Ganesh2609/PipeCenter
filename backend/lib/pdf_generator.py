import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from .models import Quotation

# Company information
COMPANY_INFO = {
    'name': 'Pipe Center',
    'address': '51, MARIYAPPA STREET, KATTOOR,\nCOIMBATORE, PIN - 641 009',
    'contact': '+91 9894858006 / +91 9894154439'
}

class QuotationPDFGenerator:
    """
    Professional PDF generator for quotations using ReportLab
    """
    
    @staticmethod
    def generate(quotation: Quotation) -> bytes:
        """Generate PDF for quotation and return as bytes"""
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
            elements = []
            styles = getSampleStyleSheet()
            
            # Company header
            elements.extend(QuotationPDFGenerator._create_company_header(styles))
            
            # Quotation details
            elements.extend(QuotationPDFGenerator._create_quotation_details(quotation, styles))
            
            # Customer details
            elements.extend(QuotationPDFGenerator._create_customer_details(quotation, styles))
            
            # Items table
            elements.extend(QuotationPDFGenerator._create_items_table(quotation, styles))
            
            # Summary table
            elements.extend(QuotationPDFGenerator._create_summary_table(quotation, styles))
            
            # Footer
            elements.extend(QuotationPDFGenerator._create_footer(styles))
            
            # Build PDF
            doc.build(elements)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise Exception(f"Failed to generate PDF: {str(e)}")
    
    @staticmethod
    def _create_company_header(styles):
        """Create company header section"""
        elements = []
        
        # Company name style
        company_style = ParagraphStyle(
            'CompanyHeader',
            parent=styles['Heading1'],
            fontSize=24,
            alignment=1,  # Center
            spaceAfter=6,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        # Address style
        address_style = ParagraphStyle(
            'AddressStyle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=1,  # Center
            spaceAfter=4,
            textColor=colors.black
        )
        
        # Contact style
        contact_style = ParagraphStyle(
            'ContactStyle',
            parent=styles['Normal'],
            fontSize=11,
            alignment=1,  # Center
            spaceAfter=20,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph(COMPANY_INFO['name'].upper(), company_style))
        elements.append(Paragraph(COMPANY_INFO['address'], address_style))
        elements.append(Paragraph(f"Contact: {COMPANY_INFO['contact']}", contact_style))
        elements.append(Spacer(1, 12))
        
        return elements
    
    @staticmethod
    def _create_quotation_details(quotation, styles):
        """Create quotation details section"""
        elements = []
        
        # Quotation header
        quote_header_style = ParagraphStyle(
            'QuoteHeader',
            parent=styles['Heading2'],
            fontSize=18,
            alignment=1,  # Center
            spaceAfter=12,
            textColor=colors.darkred,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("QUOTATION", quote_header_style))
        
        # Quotation details table
        quote_data = [
            ['Quotation ID:', quotation.id],
            ['Date:', quotation.date],
            ['Items:', str(len(quotation.items))]
        ]
        
        quote_table = Table(quote_data, colWidths=[2*inch, 3*inch])
        quote_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(quote_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    @staticmethod
    def _create_customer_details(quotation, styles):
        """Create customer details section"""
        elements = []
        
        # Bill to header
        billto_style = ParagraphStyle(
            'BillToHeader',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("BILL TO:", billto_style))
        
        # Customer details
        customer_style = ParagraphStyle(
            'CustomerStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=4,
            leftIndent=20
        )
        
        elements.append(Paragraph(f"<b>{quotation.buyerName}</b>", customer_style))
        elements.append(Paragraph(quotation.buyerAddress, customer_style))
        elements.append(Spacer(1, 20))
        
        return elements
    
    @staticmethod
    def _create_items_table(quotation, styles):
        """Create items table"""
        elements = []
        
        # Items header
        items_header_style = ParagraphStyle(
            'ItemsHeader',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("ITEMS:", items_header_style))
        
        # Table header
        table_data = [['S.No', 'Item Name', 'Rate (₹)', 'Quantity', 'Unit', 'Amount (₹)']]
        
        # Add items
        for item in quotation.items:
            table_data.append([
                str(item.sno),
                item.itemName,
                f"₹{item.rate:.2f}",
                f"{item.quantity:g}",  # Remove trailing zeros
                item.unit,
                f"₹{item.amount:.2f}"
            ])
        
        # Create table
        items_table = Table(table_data, colWidths=[0.8*inch, 2.5*inch, 1.2*inch, 1*inch, 1*inch, 1.5*inch])
        
        # Table styling
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            
            # Alternate row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    @staticmethod
    def _create_summary_table(quotation, styles):
        """Create summary/totals table"""
        elements = []
        
        # Summary header
        summary_header_style = ParagraphStyle(
            'SummaryHeader',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("SUMMARY:", summary_header_style))
        
        # Summary data
        summary_data = [
            ['Subtotal:', f"₹{quotation.subtotal:.2f}"],
            ['Transport Charges:', f"₹{quotation.transportCharges:.2f}"],
            ['GST (18%):', f"₹{quotation.gst:.2f}"],
            ['', ''],  # Empty row for spacing
            ['TOTAL:', f"₹{quotation.total:.2f}"]
        ]
        
        # Create summary table
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        
        # Summary table styling
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 3), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 3), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 3), 6),
            
            # Total row styling
            ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 4), (-1, 4), 14),
            ('TEXTCOLOR', (0, 4), (-1, 4), colors.darkred),
            ('LINEABOVE', (0, 4), (-1, 4), 2, colors.darkblue),
            ('BOTTOMPADDING', (0, 4), (-1, 4), 8),
            ('TOPPADDING', (0, 4), (-1, 4), 8),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 30))
        
        return elements
    
    @staticmethod
    def _create_footer(styles):
        """Create footer section"""
        elements = []
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=1,  # Center
            textColor=colors.darkblue,
            fontName='Helvetica-Bold-Oblique'
        )
        
        elements.append(Paragraph("Thank you for your business!", footer_style))
        
        return elements