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
        'data/ir_sequence_data.xml',
        'views/website_templates.xml',
        'views/subscribe.xml',
        'views/monoblock.xml',
        'views/monoblock_quotation.xml',
        'views/error.xml',
        'views/multipart_quotation.xml',
        'views/die_quotation.xml',
        'views/die.xml',
        'views/multipart.xml',
        'views/res_users.xml',                        
        'report/monoblock_report.xml',
        'report/multipart_report.xml',
        'report/die_report.xml',          
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
        # 'demo/demo_data.xml',
    ],
}