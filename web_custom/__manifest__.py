{
    'name': "Web Custom",
    'version': '1.0',
    'depends': ['base'],
    'author': "Yugi, Wibicon",
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',
        'views/website_templates.xml',
        'views/subscribe.xml',
        'views/monoblock.xml',
        'views/monoblock_quotation.xml',
        'views/error.xml',
        'views/multipart_quotation.xml',
        'views/die_quotation.xml',
        'views/die.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
        # 'demo/demo_data.xml',
    ],
}