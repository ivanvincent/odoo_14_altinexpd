# -*- coding: utf-8 -*-
{
    'name': "Reporting",

    'summary': """
        Report Report""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'stock',
        'base',
        'mail',
        'base_master',
        'request_requisition',
        ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/group.xml',
        'security/ir_rule.xml',
        'wizard/reporting_stock_wizard.xml',
        'wizard/reporting_stock_lot_wizard.xml',
        'views/reporting_stock_lot.xml',
        'views/reporting_stock.xml',
        'views/custom_fonts.xml',
        'views/reporting_stock_request.xml',
        'views/reporting_purchase_order.xml',
        'report/reporting_stock.xml',
        'report/reporting_stock_lot.xml',
        'report/print_stock_opname.xml',
    ],
    
    # 'demo': [
        # 'demo/demo.xml',
    # ],
}