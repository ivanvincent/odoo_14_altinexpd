from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class StockMoveLineBefore(models.Model):
    _inherit = 'stock.move.line.before'
    
    
    lot_greige_ids = fields.One2many('stock.production.lot.temp', 'move_before_id', string='Barcode Greige')
    
    def action_show_details(self):
        _logger.warning('='*40)
        _logger.warning('ACTION SHOW DETAILS')
        _logger.warning('='*40)
        # self.ensure_one()
        # action = super().action_show_details()
        # if self.raw_material_production_id:
        #     action['views'] = [(self.env.ref('mrp.view_stock_move_operations_raw').id, 'form')]
        #     action['context']['show_destination_location'] = False
        # elif self.production_id:
        #     action['views'] = [(self.env.ref('mrp.view_stock_move_operations_finished').id, 'form')]
        #     action['context']['show_source_location'] = False
        # return action
    

    

class StockProductLotTemp(models.Model):
    _name = 'stock.production.lot.temp'
    
    
    lot_greige_id  = fields.Many2one('stock.production.lot', string='Barcode Greige')
    move_before_id = fields.Many2one('stock.move.line.before', string='Stock Move Line Before')
    lot_id         = fields.Many2one('stock.production.lot', string='Barcode',related="move_before_id.lot_id")
    production_id  = fields.Many2one('mrp.production', string='Production',related="move_before_id.production_id")
    picking_id     = fields.Many2one('stock.picking', string='Stock Picking')
    quantity       = fields.Float(string='QUantity')
