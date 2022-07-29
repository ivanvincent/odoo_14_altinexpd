{
  'name': 'Pull MySql',
  'author': 'Wibicon',
  'version': '14',
  'depends': [
    'base','stock','warehouse_stock_restrictions','account'
  ],
  'data': [
    # 'data/ir_config_parameter.xml',
    # 'data/pulling_cron.xml',
    'security/security.xml',
    'security/ir.model.access.csv',
    # 'views/pull.xml',
    # 'views/om_temp_cron.xml',
    # 'views/stock_picking.xml',
    # 'views/sj_temp_cron.xml',
    'views/res_config_settings.xml',
    'views/invoice.xml',
    'wizard/pull_mysql_wizard.xml',
    # 'views/account_move.xml',
    # 'report/report_inv_kg.xml',
  ],
  'qweb': [
    # 'static/src/xml/nama_widget.xml',
  ],
  'sequence': 1,
  'auto_install': False,
  'installable': True,
  'application': False,
  'category': 'Tools',
  'summary': 'Tools Additional For My sql',
  'license': 'OPL-1',
  'website': 'https://www.wibicon.com/',
  'description': '-'
}