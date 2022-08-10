{
  'name': 'Manufacturing Request',
  'author': 'Emkka',
  'company': 'Wibicon',
  'version': '1.0',
  'depends': [
    'base','mrp','inherit_product','base_master'
  ],
  'data': [
    'security/security.xml',
    'security/ir.model.access.csv',
    'views/mrp_request.xml',
    'views/res_config_setting.xml',
    'views/product.xml',
    'views/mrp_request_line.xml',
    'views/mrp_production.xml',
    'views/mrp_workorder.xml',
    'views/mrp_operation_template.xml',
    'views/mrp_bom.xml',
    'views/mrp_parameter.xml',
    'views/mrp_production_type.xml',
    'views/mrp_afkir_category.xml',
    'views/mrp_waste_category.xml',
    'views/mrp_afkir.xml',
    'views/mrp_waste.xml',
    'views/mrp_workorder_line.xml',
    'views/mrp_production_estimated.xml',
    # 'wizard/mrp_workoder_split_wizard.xml',
    'wizard/mrp_production_wizard.xml',
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