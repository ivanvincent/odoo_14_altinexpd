from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    treatment_id    = fields.Many2one('treatment', string='Heat Treatment')
    shape           = fields.Selection([("caplet","Caplet"),("round","Round")], string='Shape')
    kd_bahan        = fields.Char('Kode Bahan')
    lapisan         = fields.Selection([("coating","Coating"),("plating","Plating")], string='Surface Finish')
    tax_id          = fields.Many2many(string='Tax')