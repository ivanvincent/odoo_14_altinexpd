{
    'name': 'Base Master',
    'version': '0.1.3',
    'author': 'Wibicon',
    'category': 'RND',
    'depends': [
        'base',
        # 'hide_any_menu',
        # 'prt_report_attachment_preview',
        # 'wibicon_iot_box',
        ],
    'summary': 'Base Master',
    'description': """
Dev
""",
    'data': [
        'data/ir.sequence.xml',
        'security/ir.model.access.csv',
        'views/warna.xml',
        'views/master_flowprocess.xml',
        # 'views/master_wip.xml',
        # 'views/master_sisir.xml',
        # 'views/type_beam.xml',
        # 'views/master_rack.xml',
        'views/mrp_machine.xml',
        # 'views/brightness_color.xml',
        # 'views/material_chemical_type.xml',
        # 'views/master_opc.xml',
        # 'views/nama_dagang.xml',
        'views/makloon_design.xml',
        'views/treatment.xml',
        'report/mrp_machine.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
