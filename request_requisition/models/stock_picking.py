from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    request_requisition_id = fields.Many2one('request.requisition', string='Request Requisition Id')