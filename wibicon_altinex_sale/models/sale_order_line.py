from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    treatment_id = fields.Many2one('treatment', string='Treatment')
    shape = fields.Selection([("caplet","Caplet"),("round","Round")], string='Shape')