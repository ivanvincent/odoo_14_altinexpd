from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProgressProductionWizard(models.TransientModel):
    _name = 'progress.production.wizard'

    date_start = fields.Date(string='Date Start',default=fields.Date.today(), required=True, )
    date_end   = fields.Date(string='Date End',default=fields.Date.today(), required=True, )

    def action_generate(self):
        action = self.env.ref('mrp_request.open_kanban_production_action').read()[0]
        action['domain'] = [('date_planned_start', '>=', self.date_start), ('date_planned_start', '<=', self.date_end)]
        return action