from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    inspect_id   = fields.Many2one('produksi.inspect', string='Inspect')

    

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    inspect_date = fields.Date(string='Inspect Date')
    inspect_id   = fields.Many2one('produksi.inspect', string='Inspect')

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    group_category_id = fields.Many2one('group.category', string='Group Category')