# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    "name": "Payslip Whatsapp Integrations - Community Edition",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Accounting",
    "summary": "Payslip Whatsapp, Payroll Whatsapp, Payslip Whatsup, Payroll Whatsup, Manage Whatsap Payslip Odoo",
    "description": """Nowadays many communications take place on WhatsApp. Currently, in odoo, there is no feature where you can send employee payslip direct to WhatsApp. Here you can manage payroll in the WhatsApp. You can also change an employee contact number at that time when you send payslip by WhatsApp. You can send payroll information, report URL & signature to employee WhatsApp. """,
    "version": "14.0.2",
    "depends": ["sh_base_whatsapp_integration", "sh_hr_payroll", "mail"],
    "application": True,
    "data": [
        "data/payslip_email_data.xml",
        "security/whatsapp_security.xml",
        "views/res_config_settings.xml",
        "views/base_wp_message_view_inherit.xml",
        "views/payroll_inherit_view.xml",
    ],
    "images": [
        "static/description/background.png",
    ],
    "auto_install": False,
    "installable": True,
    "price": 20,
    "currency": "EUR",
}

