from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Product(models.Model):
    _inherit = 'product.product'
    

    sale_history_ids = fields.One2many('sale.product.history', 'product_id', string='History of Sale Product')