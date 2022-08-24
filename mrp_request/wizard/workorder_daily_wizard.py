from odoo import fields, models, api, _
from odoo.exceptions import UserError

class WorkorderDailyWizard(models.TransientModel):
    _name = 'workorder.daily.wizard'

    employee_id = fields.Many2one('hr.employee', string='Operator')
    date        = fields.Date(string='Date')
    workcenter_id = fields.Many2one('mrp.workcenter', string='Workcenter')

    def action_confirm(self):
        print('action_confirm')
