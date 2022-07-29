{
    'name': "Inherit Sale Order",
    'version': '1.0',
    'depends': ['base', 'sale', 'base_master', 'stock_summary_rak_variasi','inherit_product','test_development'],
    'author': "Wibicon",
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',
        'wizard/detail_mo_wizard.xml',
        'data/res_groups.xml',
        'views/sale_order_line.xml',
        'views/sale_order.xml',
        'views/product.xml',
        'wizard/create_wizard_kp.xml',
    ],
}