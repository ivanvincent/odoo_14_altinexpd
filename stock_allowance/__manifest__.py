{
    'name': "Inherit Mrp",
    'version': '1.0',
    'depends': ['base', 'stock_no_negative'],
    'author': "Yugi, Wibicon",
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'views/product_template.xml',
        'views/purchase_order.xml',
    ],
}