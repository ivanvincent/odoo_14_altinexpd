{
  'name': 'Extension Vehicle',
  'author': 'emkka',
  'company':'Wibicon',
  'version': '1.0',
  'depends': [
    'fleet',
    'request_requisition'
  ],
  'data': [
    'security/ir.model.access.csv',
    'views/fleet_service.xml',
    'views/fleet_vehicle_category.xml',
  ],
  'qweb': [
    # 'static/src/xml/nama_widget.xml',
  ],
  'sequence': 1,
  'auto_install': False,
  'installable': True,
  'application': False,
  'category': 'fleet',
  'summary': 'history maintenance',
  'license': 'OPL-1',
  'website': 'https://www.wibicon.com/',
  'description': '-'
}