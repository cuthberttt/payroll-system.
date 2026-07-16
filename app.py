"""Napol Inc. Payroll & Employee Information Management System"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from functools import wraps
from datetime import datetime, date
from dotenv import load_dotenv
import os
from io import BytesIO
import zipfile

from models import db, User, Employee, Payslip
from payroll import PayrollCalculator
from payslip_pdf import generate_payslip_pdf
from email_utils import PayslipEmailer

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///napol_payroll.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ============================================================================
# DECORATORS
# ============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Administrator access required.', 'danger')
            return redirect(url_for('employee_dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# AUTHENTICATION
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash(f'Welcome, {email}!', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('employee_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ============================================================================
# ADMIN ROUTES
# ============================================================================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_employees = Employee.query.count()
    active_employees = Employee.query.filter_by(is_active=True).count()
    
    # Get last payroll run
    last_payslip = Payslip.query.order_by(Payslip.date_generated.desc()).first()
    last_payroll_date = last_payslip.date_generated if last_payslip else None
    
    return render_template('admin_dashboard.html',
                         total_employees=total_employees,
                         active_employees=active_employees,
                         last_payroll_date=last_payroll_date)

@app.route('/admin/employees')
@admin_required
def employees_list():
    search = request.args.get('search', '')
    
    if search:
        employees = Employee.query.filter(
            (Employee.name.ilike(f'%{search}%')) |
            (Employee.email.ilike(f'%{search}%')) |
            (Employee.department.ilike(f'%{search}%'))
        ).all()
    else:
        employees = Employee.query.all()
    
    return render_template('employees_list.html', employees=employees, search=search)

@app.route('/admin/employees/add', methods=['GET', 'POST'])
@admin_required
def add_employee():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        department = request.form.get('department')
        job_title = request.form.get('job_title')
        date_hired = datetime.strptime(request.form.get('date_hired'), '%Y-%m-%d').date()
        basic_salary = float(request.form.get('basic_salary'))
        phone = request.form.get('phone')
        bank_name = request.form.get('bank_name')
        bank_account = request.form.get('bank_account')
        password = request.form.get('password')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return render_template('add_employee.html')
        
        # Create user
        user = User(email=email, role='employee')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        # Create employee
        employee = Employee(
            user_id=user.id,
            name=name,
            email=email,
            department=department,
            job_title=job_title,
            date_hired=date_hired,
            basic_salary=basic_salary,
            phone=phone,
            bank_name=bank_name,
            bank_account=bank_account
        )
        db.session.add(employee)
        db.session.commit()
        
        flash(f'Employee {name} added successfully!', 'success')
        return redirect(url_for('employees_list'))
    
    return render_template('add_employee.html')

@app.route('/admin/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    
    if request.method == 'POST':
        employee.name = request.form.get('name')
        employee.department = request.form.get('department')
        employee.job_title = request.form.get('job_title')
        employee.date_hired = datetime.strptime(request.form.get('date_hired'), '%Y-%m-%d').date()
        employee.basic_salary = float(request.form.get('basic_salary'))
        employee.phone = request.form.get('phone')
        employee.bank_name = request.form.get('bank_name')
        employee.bank_account = request.form.get('bank_account')
        
        db.session.commit()
        flash('Employee updated successfully!', 'success')
        return redirect(url_for('employees_list'))
    
    return render_template('edit_employee.html', employee=employee)

@app.route('/admin/employees/<int:employee_id>/toggle', methods=['POST'])
@admin_required
def toggle_employee_status(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    employee.is_active = not employee.is_active
    db.session.commit()
    
    status = 'activated' if employee.is_active else 'deactivated'
    flash(f'Employee {status}.', 'success')
    return redirect(url_for('employees_list'))

@app.route('/admin/payroll/run', methods=['GET', 'POST'])
@admin_required
def run_payroll():
    if request.method == 'POST':
        month = int(request.form.get('month'))
        year = int(request.form.get('year'))
        
        # Get active employees
        employees = Employee.query.filter_by(is_active=True).all()
        
        count = 0
        for employee in employees:
            # Check if payslip already exists
            existing = Payslip.query.filter_by(
                employee_id=employee.id,
                month=month,
                year=year
            ).first()
            
            if existing:
                continue
            
            # Calculate payroll
            allowances = 0  # Can be extended later
            deductions = 0  # Can be extended later
            
            payroll_data = PayrollCalculator.calculate_net_pay(
                employee.basic_salary,
                allowances,
                deductions
            )
            
            # Create payslip
            payslip = Payslip(
                employee_id=employee.id,
                month=month,
                year=year,
                basic_salary=payroll_data['basic_salary'],
                allowances=payroll_data['allowances'],
                gross_pay=payroll_data['gross_pay'],
                paye_tax=payroll_data['paye_tax'],
                ssnit_employee=payroll_data['ssnit_employee'],
                other_deductions=payroll_data['other_deductions'],
                total_deductions=payroll_data['total_deductions'],
                net_pay=payroll_data['net_pay']
            )
            db.session.add(payslip)
            count += 1
        
        db.session.commit()
        flash(f'Payroll run complete! {count} payslips generated.', 'success')
        return redirect(url_for('payroll_summary', month=month, year=year))
    
    # Get current month and year
    today = date.today()
    
    return render_template('run_payroll.html', current_month=today.month, current_year=today.year)

@app.route('/admin/payroll/summary')
@admin_required
def payroll_summary():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    payslips = Payslip.query.filter_by(month=month, year=year).all()
    
    if not payslips:
        flash('No payslips found for this period.', 'warning')
        return redirect(url_for('admin_dashboard'))
    
    total_gross = sum(p.gross_pay for p in payslips)
    total_tax = sum(p.paye_tax for p in payslips)
    total_ssnit = sum(p.ssnit_employee for p in payslips)
    total_net = sum(p.net_pay for p in payslips)
    
    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    return render_template('payroll_summary.html',
                         payslips=payslips,
                         month=month,
                         year=year,
                         month_name=month_names[month],
                         total_gross=total_gross,
                         total_tax=total_tax,
                         total_ssnit=total_ssnit,
                         total_net=total_net)

@app.route('/admin/payslip/<int:payslip_id>/generate-pdf')
@admin_required
def generate_payslip_pdf_route(payslip_id):
    payslip = Payslip.query.get_or_404(payslip_id)
    employee = payslip.employee
    
    # Create payslips directory if it doesn't exist
    os.makedirs('payslips', exist_ok=True)
    
    # Generate PDF filename
    filename = f"payslip_{employee.id}_{payslip.month}_{payslip.year}.pdf"
    filepath = os.path.join('payslips', filename)
    
    # Generate PDF
    generate_payslip_pdf(employee, payslip, filepath)
    payslip.pdf_path = filepath
    db.session.commit()
    
    flash('Payslip PDF generated.', 'success')
    return redirect(url_for('view_payslip', payslip_id=payslip_id))

@app.route('/admin/payslip/<int:payslip_id>/send-email')
@admin_required
def send_payslip_email(payslip_id):
    payslip = Payslip.query.get_or_404(payslip_id)
    employee = payslip.employee
    
    # Ensure PDF exists
    if not payslip.pdf_path or not os.path.exists(payslip.pdf_path):
        flash('Please generate PDF first.', 'warning')
        return redirect(url_for('view_payslip', payslip_id=payslip_id))
    
    # Send email
    emailer = PayslipEmailer()
    success, message = emailer.send_payslip(
        employee.email,
        employee.name,
        payslip.pdf_path,
        payslip.month,
        payslip.year
    )
    
    if success:
        payslip.email_sent = True
        payslip.email_sent_at = datetime.utcnow()
        db.session.commit()
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('view_payslip', payslip_id=payslip_id))

@app.route('/payslip/<int:payslip_id>')
@login_required
def view_payslip(payslip_id):
    payslip = Payslip.query.get_or_404(payslip_id)
    employee = payslip.employee
    user = User.query.get(session.get('user_id'))
    
    # Check authorization: admin or the employee themselves
    if user.role != 'admin' and user.id != employee.user_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    
    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    return render_template('view_payslip.html',
                         payslip=payslip,
                         employee=employee,
                         month_name=month_names[payslip.month])

@app.route('/payslip/<int:payslip_id>/download')
@login_required
def download_payslip(payslip_id):
    payslip = Payslip.query.get_or_404(payslip_id)
    employee = payslip.employee
    user = User.query.get(session.get('user_id'))
    
    # Check authorization
    if user.role != 'admin' and user.id != employee.user_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    
    # Generate PDF if not exists
    if not payslip.pdf_path or not os.path.exists(payslip.pdf_path):
        os.makedirs('payslips', exist_ok=True)
        filename = f"payslip_{employee.id}_{payslip.month}_{payslip.year}.pdf"
        filepath = os.path.join('payslips', filename)
        generate_payslip_pdf(employee, payslip, filepath)
        payslip.pdf_path = filepath
        db.session.commit()
    
    return send_file(payslip.pdf_path, as_attachment=True,
                    download_name=f"payslip_{employee.name}_{payslip.month}_{payslip.year}.pdf")

# ============================================================================
# EMPLOYEE ROUTES
# ============================================================================

@app.route('/employee/dashboard')
@login_required
def employee_dashboard():
    user = User.query.get(session.get('user_id'))
    employee = user.employee
    
    if not employee:
        flash('Employee record not found.', 'danger')
        return redirect(url_for('logout'))
    
    payslips = Payslip.query.filter_by(employee_id=employee.id).order_by(Payslip.date_generated.desc()).all()
    
    return render_template('employee_dashboard.html', employee=employee, payslips=payslips)

@app.route('/employee/profile')
@login_required
def employee_profile():
    user = User.query.get(session.get('user_id'))
    employee = user.employee
    
    if not employee:
        flash('Employee record not found.', 'danger')
        return redirect(url_for('logout'))
    
    return render_template('employee_profile.html', employee=employee)

# ============================================================================
# UTILITY ROUTES
# ============================================================================

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('employee_dashboard'))
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

# ============================================================================
# INITIALIZATION
# ============================================================================

def create_tables():
    """Create database tables and seed demo data."""
    with app.app_context():
        db.create_all()
        
        # Check if demo data already exists
        if User.query.count() > 0:
            return
        
        # Create admin user
        admin = User(email='admin@napolinc.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.flush()
        
        # Create demo employees
        demo_employees_data = [
            {
                'name': 'Ama Osei',
                'email': 'ama.osei@napolinc.com',
                'department': 'Finance',
                'job_title': 'Finance Manager',
                'date_hired': date(2022, 1, 15),
                'basic_salary': 5500.00,
                'phone': '+233 24 123 4567',
                'bank_name': 'GCB Bank',
                'bank_account': '1234567890'
            },
            {
                'name': 'Kwaku Mensah',
                'email': 'kwaku.mensah@napolinc.com',
                'department': 'Operations',
                'job_title': 'Operations Officer',
                'date_hired': date(2021, 6, 10),
                'basic_salary': 3200.00,
                'phone': '+233 55 987 6543',
                'bank_name': 'First National Bank',
                'bank_account': '0987654321'
            },
            {
                'name': 'Abena Owusu',
                'email': 'abena.owusu@napolinc.com',
                'department': 'HR',
                'job_title': 'HR Specialist',
                'date_hired': date(2023, 3, 1),
                'basic_salary': 4000.00,
                'phone': '+233 50 555 1111',
                'bank_name': 'Zenith Bank',
                'bank_account': '1111111111'
            },
        ]
        
        for emp_data in demo_employees_data:
            user = User(email=emp_data['email'], role='employee')
            user.set_password('employee123')
            db.session.add(user)
            db.session.flush()
            
            employee = Employee(
                user_id=user.id,
                **emp_data
            )
            db.session.add(employee)
        
        db.session.commit()
        print('Database initialized with demo data.')

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
