{
  'name': 'Manufacturing Request',
  'author': 'Emkka',
  'company': 'Wibicon',
  'version': '1.0',
  'depends': [
    'base','mrp','inherit_product','base_master','sale','wibicon_altinex_sale', 'product_defect','master_specifications'
  ],
  'data': [
    'data/ir_sequence.xml',
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
    'views/workorder_fat.xml',
    'views/mrp_workorder_line.xml',
    'views/mrp_workorder_line_operator.xml',
    'views/mrp_workorder_line_type.xml',
    'views/mrp_workorder_line_wc.xml',
    'views/mrp_workorder_line_tim.xml',
    'views/mrp_production_estimated.xml',
    'views/stock_picking.xml',
    'views/mrp_operation_template_line_parameter.xml',
    'views/mrp_workcenter.xml',
    'views/workorder_daily.xml',
    'views/res_users.xml',
    'views/sale_order.xml',
    
    # 'wizard/mrp_workoder_split_wizard.xml',
    'wizard/mrp_production_wizard.xml',
    'wizard/workorder_daily_wizard.xml',
    'wizard/progress_production_wizard.xml',
    'report/mrp_barcode.xml',
    'report/mrp_bom_structure.xml',
    # 'wizard/make_order_wizard.xml',
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