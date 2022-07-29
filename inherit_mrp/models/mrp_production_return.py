from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpProductionReturn(models.Model):
    _name = 'mrp.production.return'
    _description = 'Manufacture Returned'

    name               = fields.Char(string='Returned')
    production_id      = fields.Many2one('mrp.production', string='Production')
    production_type_id = fields.Many2one(related='production_id.type_id', string='Production Type')
    return_date        = fields.Date(string='Return Date', default=fields.Date.today())
    move_line_id       = fields.Many2one('stock.move.line', string='Stock Move Line')
    lot_id             = fields.Many2one(related='move_line_id.lot_id', string='Barcode')
    move_id            = fields.Many2one(related='move_line_id.move_id', string='Stock Move')
    description        = fields.Text(string='Description')
    
    