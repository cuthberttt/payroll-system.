# Napol Inc. Payroll System XX

A simple, functional Payroll & Employee Information Management System for Napol Inc. (Ghana-based company). Built with Python Flask, SQLite, and Bootstrap.

## Features

✅ **Employee Management**
- Add, edit, view employees
- Track basic salary, department, job title, bank details
- Activate/deactivate employees

✅ **Payroll Calculation**
- GRA PAYE tax bands (Ghana-compliant)
- SSNIT contributions (Employee 5.5%, Employer 13%)
- Support for allowances and deductions
- Automatic gross, tax, and net pay calculation

✅ **Payslip Generation & Distribution**
- PDF payslip generation with professional formatting
- Deep blue and white branding (Napol Inc.)
- Email payslips to employees via SMTP
- Download payslips anytime

✅ **Role-Based Access**
- Admin: Full payroll and employee management
- Employee: View own profile and download payslips

✅ **Responsive Design**
- Mobile-friendly Bootstrap UI
- Clean, professional interface
- Ghana Cedis (GH₵) currency

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite (no migrations needed)
- **Frontend**: HTML5, CSS3, Jinja2, Bootstrap 5
- **PDF**: ReportLab
- **Email**: smtplib (SMTP)
- **Authentication**: Flask sessions + password hashing (Werkzeug)

## Project Structure

```
napol_payroll/
├── app.py                    # Main Flask app with all routes
├── models.py                 # SQLAlchemy models (User, Employee, Payslip)
├── payroll.py                # Payroll calculation logic (PAYE, SSNIT)
├── payslip_pdf.py            # PDF generation function
├── email_utils.py            # SMTP email utility
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore rules
├── templates/                # Jinja2 HTML templates
│   ├── base.html             # Base layout
│   ├── login.html            # Login page
│   ├── admin_dashboard.html  # Admin home
│   ├── employees_list.html   # Employee list & search
│   ├── add_employee.html     # Add employee form
│   ├── edit_employee.html    # Edit employee form
│   ├── run_payroll.html      # Payroll run form
│   ├── payroll_summary.html  # Payroll summary view
│   ├── view_payslip.html     # Payslip details
│   ├── employee_dashboard.html # Employee home
│   ├── employee_profile.html # Employee profile
│   ├── 404.html              # Not found page
│   └── 500.html              # Server error page
├── static/
│   └── style.css             # Custom CSS (deep blue theme)
├── payslips/                 # Generated PDF payslips (auto-created)
└── README.md                 # This file
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/cuthberttt/payroll-system.git
cd payroll-system
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your settings:

```bash
cp .env.example .env
```

Edit `.env`:

```env
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///napol_payroll.db

# Gmail SMTP (example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # Use Gmail App Password, not your regular password
MAIL_DEFAULT_SENDER=noreply@napolinc.com
```

**Note**: For Gmail, generate an [App Password](https://support.google.com/accounts/answer/185833) instead of using your regular password.

### 5. Run the Application

```bash
python app.py
```

The app will be available at: `http://localhost:5000`

## Demo Credentials

The system seeds demo data on first run:

**Admin Login:**
- Email: `admin@napolinc.com`
- Password: `admin123`

**Employee Logins:**
- Email: `ama.osei@napolinc.com` | Password: `employee123`
- Email: `kwaku.mensah@napolinc.com` | Password: `employee123`
- Email: `abena.owusu@napolinc.com` | Password: `employee123`

## Usage

### For Administrators

1. **Login** with admin credentials
2. **Manage Employees** → View, add, edit, deactivate employees
3. **Run Payroll** → Select month/year and generate payslips for all active employees
4. **Generate PDFs** → Convert payslips to professional PDFs
5. **Send Emails** → Email payslips directly to employees

### For Employees

1. **Login** with your email and password
2. **View Dashboard** → See all your payslips
3. **Download Payslips** → Get PDF copies of any payslip
4. **View Profile** → Check your personal and employment details

## Payroll Calculation Details

### GRA PAYE Tax Bands (Ghana 2024)

| Income Range | Tax Rate |
|--------------|----------|
| First GH₵110 | 0% |
| Next GH₵493 | 5% |
| Next GH₵823 | 10% |
| Above GH₵1,426 | 15% |

### SSNIT Contributions

- **Employee**: 5.5% of gross pay
- **Employer**: 13% of gross pay (tracked but not deducted from employee)

### Formula

```
Gross Pay = Basic Salary + Allowances
PAYE Tax = Calculated using tax bands
SSNIT (Employee) = Gross Pay × 5.5%
Total Deductions = PAYE Tax + SSNIT + Other Deductions
Net Pay = Gross Pay - Total Deductions
```

## Database Schema

### Users Table
```sql
id, email, password_hash, role (admin/employee), created_at
```

### Employees Table
```sql
id, user_id, name, email, department, job_title, date_hired, basic_salary, phone, bank_account, bank_name, is_active, created_at
```

### Payslips Table
```sql
id, employee_id, month, year, basic_salary, allowances, gross_pay, paye_tax, ssnit_employee, other_deductions, total_deductions, net_pay, pdf_path, date_generated, email_sent, email_sent_at
```

## Email Configuration

### Using Gmail

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Use the App Password in `.env`
4. Update `MAIL_USERNAME` with your Gmail address

### Using Other SMTP Providers

Simply update the SMTP settings in `.env`:

```env
MAIL_SERVER=your-smtp-server.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-username
MAIL_PASSWORD=your-password
```

## Troubleshooting

### Database Error on First Run

**Solution**: Delete `napol_payroll.db` and restart:
```bash
rm napol_payroll.db
python app.py
```

### Email Not Sending

- Check `.env` credentials
- Verify SMTP settings are correct
- For Gmail: Ensure App Password is used, not regular password
- Check firewall/network (port 587 must be open)

### Port 5000 Already in Use

```bash
python app.py --port 5001
```

## Future Enhancements

- [ ] Allowances/deductions management per employee
- [ ] Payroll history filtering and export (CSV)
- [ ] Tax exemptions and advanced deductions
- [ ] Attendance tracking integration
- [ ] Reports and analytics dashboard
- [ ] Multi-company support
- [ ] API for third-party integrations

## Security Notes

⚠️ **Production Checklist**:
- [ ] Change `SECRET_KEY` in `.env` to a strong random value
- [ ] Set `FLASK_ENV=production`
- [ ] Use HTTPS (deploy with gunicorn + nginx/Apache)
- [ ] Store `.env` securely (never commit)
- [ ] Use strong database backups
- [ ] Implement CSRF protection for forms
- [ ] Add rate limiting to login
- [ ] Use proper logging and error tracking

## License

MIT License - Feel free to use and modify for your needs.

## Support

For issues or questions, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for Napol Inc. - Ghana Payroll Excellence**
