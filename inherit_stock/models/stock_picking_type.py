from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    return_type              = fields.Selection([("return_in","Return In"),("return_out","Return Out")], string='Return Type')
    journal_mutation_id      = fields.Many2one('account.journal', string='Journal Mutation')
    is_stock_point           = fields.Boolean(related='warehouse_id.is_stock_point', string='Stock Point')
    is_multi_location        = fields.Boolean(related='warehouse_id.is_multi_location', string='Multi Location')
    default_location_siba_id = fields.Many2one('stock.location', string='Default Siba Location')
    is_multi_step            = fields.Boolean(string='Multi Step')
    is_transit_transfer      = fields.Boolean(string='Transit ?')
    
    
    
