# -*- coding: utf-8 -*-
{
    'name': "Close Stock Period",

    'summary': """
        Can not validate stock when period was closed
    """,

    'description': """
        
    """,

    'author': "Wibicon",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock',
    ],

    # always loaded
    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'views/close_stock_period_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}