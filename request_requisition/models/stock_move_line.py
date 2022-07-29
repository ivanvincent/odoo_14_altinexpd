from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    variasi = fields.Char(string='Variasi', compute='_compute_variasi')

    def _compute_variasi(self):
        for a in self:
            for b in a.product_id:
                a.variasi = ', '.join(b.product_template_attribute_value_ids.filtered(lambda x: x.attribute_id.name == 'Variasi').mapped('name'))
                break