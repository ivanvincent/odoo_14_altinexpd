from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import time,timedelta, datetime
import pandas as pd

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    time_waiting = fields.Datetime(string='Waiting Check In', compute='compute_time_waiting')
    time_waiting_co = fields.Datetime(string='Waiting Check Out', compute='compute_time_waiting')
    late_counter = fields.Float(string='Employee Late Counter', compute='compute_late')

    @api.depends('check_in', 'check_out')
    def compute_time_waiting(self):
        for rec in self:
            rec.time_waiting = rec.check_in + timedelta(minutes=30)
            if rec.check_out:
                rec.time_waiting_co = rec.check_out + timedelta(minutes=30)
            else:
                rec.time_waiting_co = False

    @api.depends('check_in')
    def compute_late(self):
        days_dict = {
            'Monday'    : '0',
            'Tuesday'   : '1',
            'Wednesday' : '2',
            'Thursday'  : '3',
            'Friday'    : '4',
            'Saturday'  : '5',
        }
        for rec in self:
            # get tolerance_in from shift module
            # employee_id = rec.employee_id.id
            # employee = self.env['hr.employee'].search([('id','=',employee_id)])
            # employee_shift = self.env['resource.calendar'].search([('id','=',employee.resource_calendar_ids.id)])
            if rec.employee_id.resource_calendar_ids:
                day_checkin = rec.check_in.today().strftime('%A')
                tolerance_in_hours = rec.employee_id.resource_calendar_ids.attendance_ids.filtered(lambda x: x.dayofweek == days_dict.get(day_checkin)).tolerance_in
                datetime_tolerance_in = datetime.strptime(rec.check_in.strftime('%Y-%m-%d'), "%Y-%m-%d") + timedelta(hours=tolerance_in_hours)
                if rec.check_in > datetime_tolerance_in:
                    rec.late_counter = 1
                else:
                    rec.late_counter = 0
            else:
                rec.late_counter = 0