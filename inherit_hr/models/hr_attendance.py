from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    time_waiting = fields.Datetime(string='Waiting Check In', compute='compute_time_waiting')

    @api.depends('check_in')
    def compute_time_waiting(self):
        for rec in self:
            rec.time_waiting = rec.check_in + timedelta(minutes=30)