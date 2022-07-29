from odoo import fields, models, api, _
from odoo.exceptions import UserError

class ReprocessWoWizard(models.TransientModel):
    _name = 'reprocess.wo.wizard'

    workorder_id = fields.Many2one('mrp.workorder', string='Workcenter')

    @api.onchange('workorder_id')
    def _onchange_workcenter_id(self):
        ctx = self.env.context
        res = {}
        mrp_obj = self.env['mrp.production'].browse(ctx.get('active_id'))
        res['domain'] = {'workorder_id': [('id', 'in', mrp_obj.workorder_ids.ids)]}
        return res
    
    def reprocess(self):
        ctx = self.env.context
        mrp_obj = self.env['mrp.production'].search([('id', '=', ctx.get('active_id'))], limit=1)
        self.env['mrp.workorder'].browse(self.workorder_id.id).with_context(reprocess=True).copy()