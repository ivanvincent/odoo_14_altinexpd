from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    mrp_request_id = fields.Many2one('mrp.request', string='Mrp Request')
    production_id = fields.Many2one('mrp.production', string='Production')