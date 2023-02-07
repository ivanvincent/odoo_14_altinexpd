# Part of Softhealer Technologies.
{
    "name": "HR Payroll - Community Edition",
    "author": "Softhealer Technologies,Odoo SA",
    "license": "OPL-1",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Accounting",
    "summary": "Payroll System,Human Resource Payroll,HR Payroll,Employee Payroll Records,Salary Rules,Salary Structure,Print Payslip,Payslip Journal Entry,Payslip Journal Item,Payslip Accounting,Employee Salary Management Odoo",
    "description": """This module helps to manage the payroll of your organization. You can manage employee contracts with a salary structure. You can create an employee payslip and compute employee salary with salary structures & salary rules. You can generate all payslips using payslip batches.""",
    "version": "14.0.1",
    'depends': [
        'hr_contract',
        'hr_holidays',
    ],
    'data': [
        'security/hr_payroll_security.xml',
        'security/ir.model.access.csv',
        'wizard/hr_payroll_payslips_by_employees_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_employee_views.xml',
        'data/hr_payroll_sequence.xml',
        'views/hr_payroll_report.xml',
        'data/hr_payroll_data.xml',
        'wizard/hr_payroll_contribution_register_report_views.xml',
        'views/res_config_settings_views.xml',
        'views/report_contributionregister_templates.xml',
        'views/report_payslip_templates.xml',
        'views/report_payslipdetails_templates.xml',
        'wizard/hr_reporting_views.xml',
        
    ],
    'demo': ['data/hr_payroll_demo.xml'],
    "application": True,
    "auto_install": False,
    "installable": True,
    "images": ["static/description/background.png", ],
    "price": 20,
    "currency": "EUR"
}
