# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Makloon Project',
    'version': '1.0',
    'category': 'Manufacturing',
    'sequence': 50,
    'summary': '3rd Party Textile Production',
    'depends': ['mrp_textile','inherit_purchase_order'],
    "author"	: "Jumeldi Panca Putra",
    'description': """
Makloon Project
==========================

Sometimes you need to produce your product via 3rd Party Vendor instead of you produce by your own machine
""",
    'data': [
        'security/makloon_group.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/makloon_sequence.xml',
        'views/makloon_operation_view.xml',
        'views/makloon_order_view.xml',
        'views/makloon_planning_view.xml',
        'views/purchase_view.xml',
        'views/stock_view.xml',
        'report/makloon_order_printout.xml'

    ],
    "installable": True,
    'application': False,
}
