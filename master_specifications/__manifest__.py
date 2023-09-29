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
        'data/ir_sequence.xml',
        'views/master_jenis.xml',
        'views/master_require.xml',
        'views/specifications.xml',
        'views/quotation_request_form.xml',
        'report/print_qrf.xml',
        'report/specification_summary.xml',
        'report/specification.xml',
        'report/specification_detail.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
