from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import time,timedelta
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
        for rec in self:
            # get tolerance_in from shift module
            employee_id = self.employee_id.id
            employee = self.env['hr.employee'].search([('id','=',employee_id)])
            employee_shift = self.env['resource.calendar'].search([('id','=',employee.resource_calendar_ids.id)])
            
            for attendance in employee_shift.attendance_ids:
                dayOfWeek = attendance.dayofweek
                tol_in = attendance.tolerance_in
                print(dayOfWeek)
                print(tol_in)

            rec.late_counter = 1