from odoo import models, fields, api

class ProductOrder(models.Model):
    _name = 'product.order'

    name = fields.Char(string='Name')