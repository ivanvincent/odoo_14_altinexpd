{
    'name': "Inherit Inventory",
    'version': '1.0',
    'depends': ['stock', 'product_defect'],
    'author': "Yugi, Wibicon",
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',
        'data/ir.config_parameter.xml',
        # 'data/ir.rule.xml',
        # 'data/ir.sequence.xml',
        'views/stock_picking.xml',
        'views/stock_move.xml',
        # 'views/stock_inventory.xml',
        'views/account_move.xml',
        'views/stock_move_line.xml',
        'views/stock_warehouse.xml',
        'views/stock_move_sat.xml',
        # 'views/product_category.xml',
        # 'report/report_product_persupplier.xml',
        # 'wizard/product_persupplier_wizard.xml',
    ],
}