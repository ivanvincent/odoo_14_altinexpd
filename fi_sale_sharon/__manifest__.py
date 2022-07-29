# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2011 Smartmode LTD (<http://www.smartmode.co.uk>).

{
    'name': 'Sharon - Sale',
    'version': '1.0',
    'category': 'Sale',
    'description': """
    MSRA sale customization
    """,
    'author': 'PT.Sumihai Teknologi Indonesia',
    'website': 'http://www.sumihai.co.id',
    'depends': [
        'base',
        'sale',
        'product',
        'base_import',
    ],
    'data': [
        'datas/sequence.xml',
        'datas/decimal_accuracy.xml',
        'security/ir.model.access.csv',

        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/product_view.xml',

        #'views/custom_partner_cabang.xml',
        'views/custom_partner_divisi.xml',
        #'views/custom_partner_jalur.xml',
        'views/custom_partner_group.xml',
        # 'views/custom_partner_location_type.xml',
        # 'views/custom_partner_type.xml',
        #'views/custom_partner_wilayah.xml',
    ],
    'demo' : [],
}
