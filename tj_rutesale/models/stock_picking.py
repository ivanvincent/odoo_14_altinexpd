from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    
    rute_id = fields.Many2one('rute.sale', string='Rute Sale')

    