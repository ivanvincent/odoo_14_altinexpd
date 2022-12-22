from odoo import models, fields, api

class StockMoveSat(models.Model):
    _name = 'stock.move.sat'

    defect_id = fields.Many2one('product.defect', string='Defect')
    quantity = fields.Float(string='Qty')
    stock_move_id = fields.Many2one('stock.move', 'Stock Move')