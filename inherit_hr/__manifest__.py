{
  'name': 'Hr Custom',
  'author': 'Yugi',
  'company':'Wibicon',
  'version': '14.0',
  'depends': [
    'base',
    'hr_attendance'
  ],
  'data': [
    'security/ir.model.access.csv',
    'views/hr_attendance.xml',
    'wizard/laporan_shift_3.xml',
  ],    
  'qweb': [
    'static/src/xml/attendance.xml',
  ],
  'sequence': 1,
  'auto_install': False,
  'installable': True,
  'application': True,
  'category': 'Tools',
  'license': 'OPL-1',
  'website': 'https://www.wibicon.com/',
  'description': '-'
}