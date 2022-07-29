from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductCategory(models.Model):
    _inherit = 'product.category'

    code = fields.Char(string='Code')