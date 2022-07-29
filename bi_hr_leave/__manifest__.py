# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Leave Report Print',
    'version': '14.0.0.0',
    'category': 'Human Resource',
    'summary': 'HR Leave Reports Odoo Apps helps Human resource officer and manager to print HR leave report in PDF and excel format. User can print single leave report from form view and multiple leave report from tree view.',
    'description' :"""
         
        HR Leave Reports in odoo,
        Print Leave Report in odoo,
        Print Single Leave Report in odoo,
        Print Multiple Leave Report in odoo,
        HR Leave Report in PDF Format in odoo,
        HR Leave Report in Excel Format in odoo,

    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'depends': ['base','hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'report/leave_report_template.xml',
        'report/leave_report_view.xml',
        'wizard/excel_report.xml',
        'wizard/hr_leave_excel_report.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/s-7gaM6oqhM',
    "images":['static/description/Banner.png'],
}