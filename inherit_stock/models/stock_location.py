from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockLocation(models.Model):
    _inherit = 'stock.location'
    
    
    
    location_code        = fields.Char(string='Code')
    pr_sequence_id       = fields.Many2one('ir.sequence', string='PR Sequence')
    rr_sequence_id       = fields.Many2one('ir.sequence', string='RR Sequence')
    siba_location        = fields.Boolean(string='SIBA Location ?',default=False)
    warehouse_id         = fields.Many2one('stock.warehouse', string='Warehouse',compute='_compute_warehouse',store=False)
    is_stock_point       = fields.Boolean(string='Stock Point ?')
    
    
    def _compute_warehouse(self):
        for location in self:
            if location.usage == 'internal':
                warehouse_id = self.get_warehouse()
                location.warehouse_id = warehouse_id.id if warehouse_id else False
                # location.is_stock_point = warehouse_id.is_stock_point if warehouse_id else False
            else:
                location.warehouse_id = False

    
    