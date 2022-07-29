from odoo import fields, models, api, _
from odoo.exceptions import UserError

class DetailMoWizard(models.TransientModel):
    _name = 'detail.mo.wizard'

    mrp_production_ids = fields.Many2many(comodel_name='mrp.production', string='Mo Detail',)

    @api.model
    def default_get(self, fields):
        res = super(DetailMoWizard, self).default_get(fields)
        ctx = self._context
        sol_obj = self.env['sale.order.line'].browse(ctx.get('active_id'))
        res.update({'mrp_production_ids': [(6, 0, sol_obj.mrp_ids.ids)]})
        return res
