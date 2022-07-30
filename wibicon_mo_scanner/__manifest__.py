{
  'name': 'Wibicon Manufaturing Order Scanner',
  'company': 'Wibicon',
  'author': 'emkka',
  'version': '14.0',
  'depends': [
    'base','web'
  ],
  'data': [
    'views/mrp_assets_common.xml',
    'views/mrp_assets.xml',
  ],
  'qweb': [
    'static/src/xml/*.xml',
  ],
  'sequence': 1,
  'auto_install': False,
  'installable': True,
  'application': True,
  'category': 'utils',
  'summary': 'Scanner Of Manufacturing Order',
  'license': 'OPL-1',
  'website': 'https://www.wibicon.com/',
  'description': '-'
}