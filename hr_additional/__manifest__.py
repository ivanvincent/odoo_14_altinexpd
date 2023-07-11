{
  'name': 'Hr Additional',
  'author': 'Wibicon',
  'version': '14.0',
  'depends': [
    'base','hr','hr_contract_types'
  ],
  'data': [
    # 'security/ir.model.access.csv',
    # 'views/hr_employee.xml',
    # 'views/hr_employee_kelompok.xml',
    # 'views/hr_employee_shift.xml',
    # 'views/hr_employee_grop.xml',
    # 'views/hr_golongan.xml',
    # 'views/hr_department.xml',
    'views/res_users.xml',
    'security/security.xml',
  ],
  'qweb': [],
  'sequence': 1,
  'auto_install': False,
  'installable': True,
  'application': True,
  'category': 'additional',
  'summary': 'Additional for hr',
  'license': 'OPL-1',
  'website': 'https://www.wibicon.com/',
  'description': '-'
}