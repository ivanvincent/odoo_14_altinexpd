{
    'name': 'Master Specifications',
    'version': '0.1.3',
    'author': 'Yugi, Wibicon',
    'category': 'RND',
    'depends': [
        'base',
        # 'hide_any_menu',
        # 'prt_report_attachment_preview',
        # 'wibicon_iot_box',
        ],
    'summary': 'Master Specifications',
    'description': """
Dev
""",
    'data': [
        'security/ir.model.access.csv',
        'views/master_jenis.xml',
        'views/master_require.xml',
        'views/specifications.xml',
        'views/quotation_request_form.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
