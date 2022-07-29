from itertools import product
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    
    # def action_open_inventory_lines(self):
    #     # super(SaleOrder, self).action_cancel()
    #     res = super(StockInventory, self).action_open_inventory_lines()
    #     res['context']['name_product_without_code'] = True
    #     # ctx['name_product_without_code'] = True
    #     import logging;
    #     _logger = logging.getLogger(__name__)
    #     _logger.warning('='*40)
    #     _logger.warning(res['context'])
    #     _logger.warning('='*40)
        
    #     return res
        




class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    
    product_code = fields.Char(related='product_id.default_code', string='Code')