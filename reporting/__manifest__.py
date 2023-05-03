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
        'views/reporting_stock_kg.xml',
        'views/custom_fonts.xml',
        'views/reporting_stock_request.xml',
        'views/reporting_purchase_order.xml',
        'report/reporting_stock.xml',
        'report/reporting_stock_lot.xml',
        'report/print_stock_opname.xml',
        'report/laporan_mutasi_barang.xml',
        'report/laporan_pengeluaran_kain.xml',
        'report/laporan_pengeluaran_kain.xml',
        'report/laporan_kain_lama.xml',
        'report/laporan_akurasi_data_stock_opname.xml',
        'report/laporan_group_by_palet.xml',
        'report/laporan_barcode_perpalet.xml',
    ],
    
    # 'demo': [
        # 'demo/demo.xml',
    # ],
}