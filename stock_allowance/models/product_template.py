from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allowance           = fields.Float(string='Allowance')
    price_allowance     = fields.Float(string='Price Allowance')
    