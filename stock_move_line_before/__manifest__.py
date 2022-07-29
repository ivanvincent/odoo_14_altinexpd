{
  'name': 'Stock Move Line Before',
  'author': 'Wibicon',
  'version': '1.0',
  'depends': [
    'base','product','inherit_mrp','hr','product_defect','base_master'
  ],
  'data': [
    'security/stock_move_line_group.xml',
    'security/ir.model.access.csv',
    'views/stock_move_line_before.xml',
    'views/mrp.xml',
    'wizard/mrp_dopping_wizard.xml',
  ],
  'qweb': [
    # 'static/src/xml/nama_widget.xml',
  ],
  'sequence': 1,
  'auto_install': False,
  'installable': True,
  'application': False,
  'category': 'addtional',
  'summary': 'Before Produce',
  'license': 'OPL-1',
  'website': 'https://www.wibicon.com/',
  'description': '-'
}