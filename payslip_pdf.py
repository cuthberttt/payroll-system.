"""PDF generation module for payslips."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import os

def generate_payslip_pdf(employee, payslip, output_path):
    """
    Generate a PDF payslip for an employee.
    
    Args:
        employee: Employee object
        payslip: Payslip object
        output_path: Path where PDF will be saved
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           topMargin=0.5*inch,
                           bottomMargin=0.5*inch,
                           leftMargin=0.75*inch,
                           rightMargin=0.75*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#003366'),  # Deep blue
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#003366'),
        fontName='Helvetica-Bold'
    )
    
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=9
    )
    
    # Header - Company name
    elements.append(Paragraph('NAPOL INC.', title_style))
    elements.append(Paragraph('Payslip', header_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Employee and payslip info
    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    period = f"{month_names[payslip.month]} {payslip.year}"
    
    info_data = [
        ['Employee Name:', employee.name, 'Period:', period],
        ['Employee ID:', str(employee.id), 'Date Generated:', datetime.now().strftime('%d/%m/%Y')],
        ['Department:', employee.department, 'Job Title:', employee.job_title],
        ['Date Hired:', employee.date_hired.strftime('%d/%m/%Y'), 'Bank:', employee.bank_name or 'N/A'],
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
        ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#003366')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#003366')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#003366')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Earnings and Deductions
    payroll_data = [
        ['EARNINGS', '', 'DEDUCTIONS', ''],
        ['Basic Salary', f"GH₵ {payslip.basic_salary:,.2f}", 'PAYE Tax', f"GH₵ {payslip.paye_tax:,.2f}"],
        ['Allowances', f"GH₵ {payslip.allowances:,.2f}", 'SSNIT (Employee)', f"GH₵ {payslip.ssnit_employee:,.2f}"],
        ['', '', 'Other Deductions', f"GH₵ {payslip.other_deductions:,.2f}"],
    ]
    
    payroll_table = Table(payroll_data, colWidths=[1.75*inch, 1.75*inch, 1.75*inch, 1.75*inch])
    payroll_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (2, 0), (3, 0), colors.HexColor('#003366')),
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#E8F0F7')),
        ('BACKGROUND', (2, 0), (3, 0), colors.HexColor('#E8F0F7')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (1, -1), 0.5, colors.grey),
        ('LINEBELOW', (2, 0), (3, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#003366')),
    ]))
    elements.append(payroll_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Summary
    summary_data = [
        ['Gross Pay', f"GH₵ {payslip.gross_pay:,.2f}"],
        ['Total Deductions', f"GH₵ {payslip.total_deductions:,.2f}"],
        ['NET PAY', f"GH₵ {payslip.net_pay:,.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, 1), 'Helvetica', 9),
        ('FONT', (0, 2), (0, 2), 'Helvetica-Bold', 11),
        ('FONT', (1, 0), (1, 1), 'Helvetica', 9),
        ('FONT', (1, 2), (1, 2), 'Helvetica-Bold', 11),
        ('TEXTCOLOR', (0, 2), (1, 2), colors.HexColor('#003366')),
        ('BACKGROUND', (0, 2), (1, 2), colors.HexColor('#E8F0F7')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, 2), (1, 2), 1.5, colors.HexColor('#003366')),
        ('LINEBELOW', (0, 2), (1, 2), 1.5, colors.HexColor('#003366')),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        'This is a confidential document. For queries, contact HR.',
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
