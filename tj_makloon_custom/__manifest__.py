# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Makloon Custom',
    'version': '1.0',
    'category': 'Makloon',
    'author'	: "Angkringan.com",
    'depends': ['sale','product','stock','purchase','mrp_textile','makloon_project','almega_stock'],
    'description': """
Features
==========================
* inventory -> stock barcode
* inventory -> print barcode
* purchase -> print hpp detail

""",
    'data': [

'data/ir_sequence_data.xml',
'report/report_purchase_order.xml',
'report/report_purchase_order2.xml',
'report/report_barcode.xml',
'report/report_makloon_barcode.xml',
'report/report_makloon_barcode_line.xml',
'report/report_makloon_purchase.xml',
'report/report_makloon_order.xml',
'report/report_makloon_planning.xml',
'report/report_makloon_planning2.xml',
'report/report_makloon_purchase_order.xml',
'report/report_makloon_hpp.xml',
'report/report_packing_list.xml',
'report/report_makloon_harga_outlet.xml',
'wizard/wizard_makloon_barcode.xml',
'wizard/wizard_makloon_purchase.xml',
'wizard/wizard_makloon_hpp.xml',
'wizard/wizard_makloon_harga_outlet.xml',
'wizard/wizard_stock_picking_list.xml',
'views/makloon_sequence.xml',
'views/makloon_resep_warna.xml',
'views/makloon_view.xml',
'views/makloon_order.xml',
'views/makloon_barcode.xml',
'views/makloon_operation.xml',
'views/makloon_planning.xml',
'views/makloon_harga_outlet.xml',
'views/purchase_order.xml',
'views/makloon_hpp.xml',
'views/product.xml',
'views/stockpicking.xml',
'views/makloon_picking_list.xml',
'views/purchase_order.xml',


'security/res_groups.xml',
'security/ir.model.access.csv'
    ],
    "installable": True,
    'application': False,
    'auto_install': False,
}