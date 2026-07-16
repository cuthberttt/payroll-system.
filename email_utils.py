"""Email utility module for sending payslips."""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
from dotenv import load_dotenv

load_dotenv()

class PayslipEmailer:
    
    def __init__(self):
        self.smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('MAIL_PORT', 587))
        self.username = os.getenv('MAIL_USERNAME')
        self.password = os.getenv('MAIL_PASSWORD')
        self.sender = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@napolinc.com')
    
    def send_payslip(self, recipient_email, employee_name, payslip_path, month, year):
        """
        Send payslip via email.
        
        Args:
            recipient_email (str): Employee's email
            employee_name (str): Employee's name
            payslip_path (str): Path to PDF file
            month (int): Month (1-12)
            year (int): Year
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not self.username or not self.password:
                return False, "Email credentials not configured. Check .env file."
            
            if not os.path.exists(payslip_path):
                return False, f"Payslip file not found: {payslip_path}"
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = recipient_email
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = f'Your Payslip - {month:02d}/{year}'
            
            # Email body
            month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            
            body = f"""
Dear {employee_name},

Please find attached your payslip for {month_names[month]} {year}.

If you have any questions regarding your payslip, please contact the HR department.

Best regards,
Napol Inc. HR Department
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach PDF
            with open(payslip_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(payslip_path)}')
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True, f"Payslip sent successfully to {recipient_email}"
        
        except Exception as e:
            return False, f"Failed to send payslip: {str(e)}"
