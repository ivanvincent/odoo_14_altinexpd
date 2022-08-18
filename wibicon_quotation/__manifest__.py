{
    'name': "Quotation",
    'version': '1.0',
    'depends': ['base'],
    'author': "Wibicon, Yugi",
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'data/ir_sequence.xml',
        'views/quotation.xml',
        'security/ir.model.access.csv'
    ],
    # data files containing optionally loaded demonstration data
}