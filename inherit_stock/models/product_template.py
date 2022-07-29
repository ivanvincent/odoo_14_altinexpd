from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    jumlah_cones = fields.Float(string='Jumlah Cones')
    berat_per_cones = fields.Float(string='Berat Per Cones')
    berat_box = fields.Float(string='Berat Box', compute="_compute_berat_box")

    @api.depends('jumlah_cones', 'berat_per_cones')
    def _compute_berat_box(self):
        for rec in self:
            rec.berat_box = rec.jumlah_cones * rec.berat_per_cones