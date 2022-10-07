from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    product_id = fields.Many2one('product.product', string='Product', related='order_line.product_id')
    quantity = fields.Float(string='Quantity', related='order_line.product_qty')