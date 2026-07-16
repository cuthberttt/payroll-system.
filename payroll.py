"""Payroll calculation module for Napol Inc."""

class PayrollCalculator:
    """
    Handles payroll calculations for Ghana-based employees.
    - GRA PAYE tax bands
    - SSNIT contributions
    - Allowances and deductions
    """
    
    # GRA PAYE Tax Bands (2024 rates, in GH₵)
    # These are cumulative tax bands
    PAYE_BANDS = [
        (110.0, 0),           # First 110 GH₵ @ 0%
        (493.0, 0.05),        # Next 493 GH₵ @ 5%
        (823.0, 0.10),        # Next 823 GH₵ @ 10%
        (float('inf'), 0.15), # Above 1426 GH₵ @ 15%
    ]
    
    # SSNIT Contribution Rates
    SSNIT_EMPLOYEE_RATE = 0.055      # 5.5%
    SSNIT_EMPLOYER_RATE = 0.13       # 13%
    
    @staticmethod
    def calculate_paye_tax(gross_pay):
        """
        Calculate PAYE tax based on GRA bands.
        
        Args:
            gross_pay (float): Gross salary in GH₵
            
        Returns:
            float: PAYE tax amount
        """
        if gross_pay <= 0:
            return 0
        
        tax = 0
        cumulative = 0
        
        for band_limit, rate in PayrollCalculator.PAYE_BANDS:
            band_start = cumulative
            band_end = min(band_limit, gross_pay)
            
            if band_end > band_start:
                taxable_in_band = band_end - band_start
                tax += taxable_in_band * rate
                cumulative = band_end
            
            if gross_pay <= band_end:
                break
        
        return round(tax, 2)
    
    @staticmethod
    def calculate_ssnit(gross_pay, employee=True):
        """
        Calculate SSNIT contribution.
        
        Args:
            gross_pay (float): Gross salary in GH₵
            employee (bool): If True, calculate employee rate; if False, employer rate
            
        Returns:
            float: SSNIT contribution amount
        """
        rate = PayrollCalculator.SSNIT_EMPLOYEE_RATE if employee else PayrollCalculator.SSNIT_EMPLOYER_RATE
        return round(gross_pay * rate, 2)
    
    @staticmethod
    def calculate_net_pay(basic_salary, allowances=0, deductions=0):
        """
        Calculate complete payroll for an employee.
        
        Args:
            basic_salary (float): Basic salary in GH₵
            allowances (float): Additional allowances in GH₵
            deductions (float): Other deductions in GH₵
            
        Returns:
            dict: Detailed payroll breakdown
        """
        gross_pay = basic_salary + allowances
        paye_tax = PayrollCalculator.calculate_paye_tax(gross_pay)
        ssnit_employee = PayrollCalculator.calculate_ssnit(gross_pay, employee=True)
        
        total_deductions = paye_tax + ssnit_employee + deductions
        net_pay = gross_pay - total_deductions
        
        return {
            'basic_salary': round(basic_salary, 2),
            'allowances': round(allowances, 2),
            'gross_pay': round(gross_pay, 2),
            'paye_tax': paye_tax,
            'ssnit_employee': ssnit_employee,
            'other_deductions': round(deductions, 2),
            'total_deductions': round(total_deductions, 2),
            'net_pay': round(net_pay, 2),
        }
