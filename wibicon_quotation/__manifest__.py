{
    'name': "Quotation",
    'version': '1.0',
    'depends': ['base', 'stock', 'sale'],
    'author': "Wibicon, Yugi",
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'data/ir_sequence.xml',
        'views/quotation.xml',
        'security/ir.model.access.csv',
        'views/sales_contract.xml',
        'views/request_engineering.xml',
        'views/stock_picking.xml',
        'views/sale_order.xml',
    ],
    # data files containing optionally loaded demonstration data
}