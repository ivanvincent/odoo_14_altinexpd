{
    'name': 'Master Specifications',
    'version': '0.1.3',
    'author': 'Yugi, Wibicon',
    'category': 'RND',
    'depends': [
        'base', 'mail'
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
<<<<<<< HEAD
        'views/dqups_2.xml',
=======
        'views/dqucps_2.xml',
>>>>>>> 42cdb9030f851b5fe403eed06a6fc058da9468d8
        # 'views/dqups_3.xml',
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
        'report/print_qrf_dqups3.xml',
        'report/inform_consent.xml',
        'wizard/print_qrf_wizard.xml',
        'wizard/print_qrf_dqups2.xml',
        'wizard/print_qrf_dqups3.xml',
        'wizard/inform_consent_wizard.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
