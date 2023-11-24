{
    'name': 'Master Specifications',
    'version': '0.1.3',
    'author': 'Yugi, Wibicon',
    'category': 'RND',
    'depends': [
        'base',
        # 'sale',
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
        'data/res_groups.xml',
        'views/master_jenis.xml',
        'views/master_require.xml',
        'views/specifications.xml',
        'views/quotation_request_form.xml',
        'views/master_qty.xml',
        'views/dqups_2.xml',
        'views/dqups_3.xml',
        'views/conclusion.xml',
        # 'report/specification.xml',
        'report/print_qrf.xml',
        'report/d_qups2_report.xml',
        'report/specification_summary.xml',
        'report/specification_detail.xml',
        'report/d_qups2_report_unpage.xml',
        'report/surat_penawaran.xml',
        'report/quotation.xml',
        'report/surat_penawaran_dqups2.xml',
        'report/quotation_dqups2.xml',
        'report/specification_summary_dqups2.xml',
        'report/print_qrf_unpage.xml',
        'wizard/print_qrf_wizard.xml',
        'wizard/print_qrf_dqups2.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
