{
    'name': 'Stock Point Order',
    'author': 'Emkka',
    'company': 'Wibicon',
    'version': '1.0',
    'depends': [
        'base', 'account','stock', 'dh_res_partner','mail','inherit_fleet'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/stock_point_order.xml',
        'views/res_config_setting.xml',
        'views/res_partner_jalur.xml',
        'report/stock_point_order.xml',
    ],
    'qweb': [
        # 'static/src/xml/nama_widget.xml',
    ],
    'sequence': 1,
    'auto_install': False,
    'installable': True,
    'application': True,
    'category': 'Sale',
    'summary': 'Sale',
    'license': 'OPL-1',
    'website': 'https://www.wibicon.com/',
    'description': '-'
}
