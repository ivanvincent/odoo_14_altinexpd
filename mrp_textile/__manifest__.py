# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Textile Manufacturing',
    'version': '1.0',
    'category': 'Manufacturing',
    'sequence': 50,
    'summary': 'Manufacture Process for Textile Industry',
    'depends': ['mrp', 'purchase','stock_account'],
    "author"	: "Jumeldi Panca Putra",
    'description': """
Makloon Project
==========================

Manufacture Process for Textile Industry
""",
    'data': [
        'security/ir.model.access.csv',
        'views/product_view.xml',
    ],
    "installable": True,
    'application': False,
}
