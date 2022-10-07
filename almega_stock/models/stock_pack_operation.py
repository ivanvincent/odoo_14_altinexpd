from odoo import fields, api, models, _

class StockPackOperationLot(models.Model):
    _inherit = 'stock.production.lot'

    no_urut = fields.Char(string='No Urut')
    no_lot = fields.Char(string='No Lot')
    