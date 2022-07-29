{
    'name': "tj summary rak variasi",
    'version': '10.0.2.0.0',
    'summary': """Create & Process Update""",
    'description': """This module allows to create and process update order.""",
    'author': "Angkringan",
    'company': "WIBICON",
    'website': "http://www.wibicon.com",
    'category': 'Inventory',
    'depends': [
                # 'tj_makloon_custom',
                'stock',
                'base',
                'mail',
                'base_master'
                ],
    'data': [
                'security/ir.model.access.csv',
                'security/group.xml',
                # 'views/menu.xml',
                # 'views/tj_summary_rak_variasi.xml',
                # 'views/tj_summary_rak_variasi_line_view.xml',
                # 'views/history_tree.xml',
                # 'report/stock_summary.xml',
                # 'report/stock_summary_xlsx_template.xml',
                # 'views/follow_up_forcast.xml',
                # 'wizard/follow_up_forcast_wizard_view.xml'
            ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}