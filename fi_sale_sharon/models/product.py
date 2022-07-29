from odoo import api, fields, models

class ProductProduct(models.Model):
	_inherit = "product.product"
	
	customer_ids = fields.Many2many('res.partner', 'res_partner_product_product_rel',  'product_id', 'partner_id', string="Customer(s)")