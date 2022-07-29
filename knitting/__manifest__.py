{
    'name': "Knitting",
    'version': '1.0',
    'depends': ['base', 'mrp','stock','inherit_mrp','inherit_sale_order','stock_move_line_before'],
    'author': "Wibicon",
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'data/ir.sequence.xml',
        'security/ir.model.access.csv',
        'views/inspect.xml',
        'views/knitting.xml',
        'views/mrp_request.xml',
        'views/mrp_request_weaving.xml',
        'views/mrp_request_sizing.xml',
        'views/mrp_request_twisting.xml',
        'views/mrp_request_warping.xml',
        'views/product.xml',
        'views/mrp_production.xml',
        'views/sale_order.xml',
        'wizard/inspect_transfer.xml',
        'wizard/inspect_return_wizard.xml',
        'report/produksi_inspect_barcode.xml',
    ],
}