from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'
    
    product_category_ids = fields.Many2many(
        comodel_name='product.category',    
        relation='warehouse_product_category_rel',
        column1='product_categ_id',
        column2='warehouse_id',
        string='Product Category'
        )
    
    is_stock_point      = fields.Boolean(string='Stock Point ?',default=False)
    is_multi_location   = fields.Boolean(string='Multi Location ?',default=False)
    lead_days           = fields.Integer(string='Lead')
    
    