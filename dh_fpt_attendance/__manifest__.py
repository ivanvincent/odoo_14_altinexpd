{
    'name': 'Wibicon Device FingerPrint Bridging',
    'version': '14.0.1.0.0',
    'summary': """Integrating Device FingerPrint Bridging (Model series ZK / Solution Tested Machine(X100C,X103C,X302,X304)) With HR Attendance""",
    'description': """This module integrates Odoo with the Device FingerPrint Bridging (Model series ZK / Solution Tested Machine(X100C,X103C,X302,X304)),odoo,hr,attendance""",
    'category': 'Generic Modules/Human Resources',
    'author': 'Wibicon, Deni Hidayat',
    'company': 'Wibicon',
    'website': "https://www.wibicon.com",
    'depends': ['base_setup', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/dh_fpt_machine_view.xml',
        'views/dh_fpt_machine_log_view.xml',
        'views/dh_fpt_machine_finger_view.xml',
        'data/download_data.xml'

    ],
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}