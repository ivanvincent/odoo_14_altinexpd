from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import time,timedelta, datetime
import pandas as pd

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    time_waiting = fields.Datetime(string='Waiting Check In', compute='compute_time_waiting')
    time_waiting_co = fields.Datetime(string='Waiting Check Out', compute='compute_time_waiting')
    late_counter = fields.Float(string='Employee Late Counter', compute='compute_late')
    shift_3_counter = fields.Float(string='Shift 3 Counter', compute='compute_shift_3_counter')

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
            if rec.employee_id.resource_calendar_ids:
                day_checkin = rec.check_in.today().strftime('%A')
                tolerance_in_hours = rec.employee_id.resource_calendar_ids.attendance_ids.filtered(lambda x: x.dayofweek == days_dict.get(day_checkin)).tolerance_in
                datetime_tolerance_in = datetime.strptime(rec.check_in.strftime('%Y-%m-%d'), "%Y-%m-%d") + timedelta(hours=tolerance_in_hours)
                hour_from = rec.employee_id.resource_calendar_ids.attendance_ids.filtered(lambda x: x.dayofweek == days_dict.get(day_checkin)).hour_from
                hour_to = rec.employee_id.resource_calendar_ids.attendance_ids.filtered(lambda x: x.dayofweek == days_dict.get(day_checkin)).hour_to
                half_day_calculation = (hour_from-hour_to)/2 + 1

                if rec.check_in > datetime_tolerance_in:
                    rec.late_counter = 0.5
                else:
                    if (rec.check_in <= datetime_tolerance_in) and (rec.worked_hours >= half_day_calculation):
                        rec.late_counter = 0
                    else : 
                        rec.late_counter = 0.5

            else:
                rec.late_counter = 0

    @api.depends('check_in')
    def compute_shift_3_counter(self):
        for rec in self:
            checkin = datetime.strptime(rec.check_in.strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S") + timedelta(hours=7)
            datetime_start = datetime.strptime(rec.check_in.strftime('%Y-%m-%d 23:00:00'), "%Y-%m-%d %H:%M:%S")
            datetime_end = datetime_start + timedelta(hours=2) 
            # print("datetime_start", datetime_start)
            # print("datetime_end", datetime_end)
            print("==============================")

            print("id             ",rec.id)
            print("name:          ",rec.employee_id.name)
            print("check in       ",checkin) 
            print("datetime_start ", datetime_start)
            print("datetime_end   ", datetime_end)
            print(checkin >= datetime_start and checkin <= datetime_end)
            if checkin >= datetime_start and checkin <= datetime_end :
                rec.shift_3_counter = 1
            else:
                rec.shift_3_counter = 0
                # if rec.check_in >= datetime_start and rec.check_in <= datetime_end:11
                # else:
                # if checkin >= datetime_start:
                #     rec.shift_3_counter = 0