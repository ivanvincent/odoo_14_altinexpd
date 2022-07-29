# -*- coding: utf-8 -*-
{
    'name': "Request Requisition",

    'summary': """Manage Request Requisition""",

    'description': """
        Request Requisition module
    """,

    'author': "Romadon",
    'website': "http://www.wibicon.com",
    'category': 'Request Requisition',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 
                'stock',
                'purchase_request',
                'fleet'
                ],

    # always loaded
    'data': [        
        "data/request_requisition_sequence.xml",
        "data/request_requisition_data.xml",
        "data/res_group.xml",
        'security/security.xml',
        # "data/ir_rule.xml",
        "reports/report_request_requisition.xml",
        'security/ir.model.access.csv',
        # 'security/ir_rule.xml',
        'views/request_requisition.xml',
        'views/request_requisition_report.xml',
        'views/warehouse.xml',
        'views/res_users.xml',
        'views/purchase_order_line.xml',
        'views/stock_picking.xml',
        'wizard/rr_purchase_request_wizard.xml',
        
        'views/purchase_request.xml'
    ],

    'qweb': ['static/src/xml/qty_at_date.xml'],
    'application'   : True,
}
