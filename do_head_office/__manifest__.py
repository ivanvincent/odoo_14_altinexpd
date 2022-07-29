{
  'name': 'DO Head Office',
  'author': 'Emkka',
  'version': '1.0',
  'depends': [
    'base','stock','dh_res_partner','stock_point_order'
  ],
  'data': [
    'security/security.xml',
    'security/ir.model.access.csv',
    'data/ir_sequence.xml',
    'views/do_head_office.xml',
    'views/res_config_setting.xml',
    'report/do_all_product.xml',
    # 'views/stock_location_route.xml',
    # 'views/stock_location_route_template.xml',
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