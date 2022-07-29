from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = 'stock.move'

    variasi = fields.Char(string='Variasi', compute='_compute_variasi')

    def _compute_variasi(self):
        for a in self:
            for b in a.product_id:
                a.warna = ', '.join(b.product_template_attribute_value_ids.filtered(lambda x: x.attribute_id.name == 'Variasi').mapped('name'))
                break