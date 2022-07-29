{
  'name': 'Product Additional',
  'author': 'Wibicon',
  'version': '14.0',
  'depends': [
    'base','product','stock',
  ],
  'data': [
    'security/security.xml',
    'data/ir_sequence.xml',
    # 'security/ir.model.access.csv',
    'views/product.xml',
    # 'views/master_design.xml',
    # 'views/yarn_product.xml',
    # 'views/greige_product.xml',
    # 'views/finish_goods_product.xml',
  ],
  'qweb': [
    # 'static/src/xml/nama_widget.xml',
  ],
  'sequence': 1,
  'auto_install': False,
  'installable': True,
  'application': False,
  'category': 'additional',
  'summary': 'Product Addtional',
  'license': 'OPL-1',
  'website': 'https://www.wibicon.com',
  'description': '-'
}