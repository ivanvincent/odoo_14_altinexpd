from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockLocation(models.Model):
    _inherit = 'stock.location'
    
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')

    