{
    'name': "Inherit Stock",
    'version': '1.0',
    'depends': ['base', 'stock','hr','base_master','warehouse_stock_restrictions'],
    'author': "Wibicon",
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir.sequence.xml',
        # 'views/product_attribute_value.xml',
        'views/stock_picking.xml',
        # 'views/stock_production_lot.xml',
        'views/stock_warehouse.xml',
        'views/stock_location.xml',
        # 'views/mrp_production.xml',
        # 'views/product_template.xml',
        'views/stock_picking_type.xml',
        # 'views/mrp_raw_revision.xml',
        # 'views/stock_production_lot_yarn.xml',
        # 'views/stock_production_lot_greige.xml',
        # 'views/stock_production_lot_fg.xml',
        'report/sppm.xml',
        'report/report_sppm.xml'
        'wizard/laporan_penerimaan_wizard.xml',
        'wizard/laporan_pemakaian_wizard.xml',
        'wizard/split_barcode_wizard.xml',
        # 'wizard/mrp_raw_revision_wizard.xml',
        'wizard/laporan_permintaan_barang.xml',
        # 'wizard/laporan_lpsm_benang.xml',
        # 'wizard/stock_picking_return.xml',
        'data/res_groups.xml',
    ],
}