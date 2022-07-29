from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPointOrderConfig(models.Model):
    _name = 'stock.point.order.config'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    
    
    filter_product       = fields.Boolean(string='Filter Product',default=False)
    approval             = fields.Boolean(string='Approval',default=False)
    product_category_ids = fields.Many2many(comodel_name='product.category', string='Product Category')
    
