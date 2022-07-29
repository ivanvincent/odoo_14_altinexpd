from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning
from datetime import datetime, timedelta

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder):
        res = super(StockMove, self)._action_done(cancel_backorder)
        for move in self :
            trx_date = move.picking_id.date or move.date
            datetime_move = trx_date + timedelta(hours=7)
            datetime_move_string = datetime_move.strftime('%Y-%m-%d')
            import logging;
            _logger = logging.getLogger(__name__)
            _logger.warning('='*40)
            _logger.warning('date move')
            _logger.warning(datetime_move_string)
            _logger.warning(move.picking_id.date)
            _logger.warning('='*40)
            warehouse_ids = move.location_id.get_warehouse().ids + move.location_dest_id.get_warehouse().ids
            warehouse_names = ', '.join([warehouse.name for warehouse in self.env['stock.warehouse'].browse(warehouse_ids)])
            if self.env['close.stock.period'].is_closed(datetime_move_string, warehouse_ids):
            # if self.env['close.stock.period'].is_closed(datetime_move_string, warehouse_ids) and not move.purchase_line_id:
                raise Warning(_("Can not transfer stock. This period was closed.\n\nDate: %s\nWarehouse: %s"%(datetime_move_string, warehouse_names)))
        return res
    