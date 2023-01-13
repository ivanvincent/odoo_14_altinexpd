from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    
    mrp_ids  = fields.One2many('mrp.production', 'sale_line_id', string='Manufacture')