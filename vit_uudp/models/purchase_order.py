from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    penyelesaian_id = fields.Many2one('uudp', string='Penyelesaian',domain=[('type','=','penyelesaian')])