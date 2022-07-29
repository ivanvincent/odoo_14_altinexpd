{
  'name': 'Manufacturing Request',
  'author': 'Emkka',
  'company': 'Wibicon',
  'version': '1.0',
  'depends': [
    'base','mrp','inherit_product','stock_point_order'
  ],
  'data': [
    'security/security.xml',
    'security/ir.model.access.csv',
    'views/mrp_request.xml',
    'views/res_config_setting.xml',
    'views/product.xml',
    'wizard/stock_point_order_line_wizard.xml',
  ],
  'qweb': [
    # 'static/src/xml/nama_widget.xml',
  ],
  'sequence': 1,
  'auto_install': False,
  'installable': True,
  'application': True,
  'category': 'Manufacture',
  'summary': 'Manufacturing Request',
  'license': 'OPL-1',
  'website': 'https://www.wibicon.com/',
  'description': '-'
}