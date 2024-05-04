from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import time,timedelta, datetime, time
import pandas as pd

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    time_waiting = fields.Datetime(string='Waiting Check In', compute='compute_time_waiting')
    time_waiting_co = fields.Datetime(string='Waiting Check Out', compute='compute_time_waiting')
    late_counter = fields.Float(string='Employee Late Counter', compute='compute_late_time', store=True)
    shift_3_counter = fields.Float(string='Shift 3 Counter', compute='compute_shift_3_counter', store=True)
    resource_calendar_ids = fields.Many2one('resource.calendar', string='Working Hours')
    should_hour_from = fields.Float(string='Hour From',  compute='compute_should_hour_from')
    should_hour_to = fields.Float(string='Hour To', compute='compute_should_hour_from')
    should_tolerance_in_hours = fields.Float(string='Tolerance in hours', compute='compute_should_hour_from')


    @api.depends('check_in', 'check_out')
    def compute_time_waiting(self):
        for rec in self:
            rec.time_waiting = rec.check_in + timedelta(minutes=30)
            if rec.check_out:
                rec.time_waiting_co = rec.check_out + timedelta(minutes=30)
            else:
                rec.time_waiting_co = False

    @api.depends('check_in')
    def compute_late_time(self):
        for rec in self:
            checkin = datetime.strptime(rec.check_in.strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S") + timedelta(hours=7)
            check_in_time = checkin.time()
            #check-in times that is considered as late
            s3_start_late_time = time(0,31,0)
            s3_end_late_time = time(5,0,0)
            cleaner_start_late_time = time(6,31,0)
            cleaner_end_late_time = time(7,0,0)
            s1a_start_late_time = time(8,31,0)
            s1a_end_late_time = time(12,0,0)
            s1b_start_late_time = time(13,31,0)
            s1b_end_late_time = time(15,0,0)
            s2_start_late_time = time(16,31,0)
            s2_end_late_time = time(21,30,0)

            if (check_in_time >= s3_start_late_time and check_in_time <= s3_end_late_time) or (check_in_time >= cleaner_start_late_time and check_in_time <= cleaner_end_late_time) or (check_in_time >= s1a_start_late_time and check_in_time <= s1a_end_late_time) or (check_in_time >= s1b_start_late_time and check_in_time <= s1b_end_late_time) or (check_in_time >= s2_start_late_time and check_in_time <= s2_end_late_time):
                rec.late_counter = 0.5
            else:
                rec.late_counter = 0
    

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
                tolerance_in_hours = rec.resource_calendar_ids.attendance_ids.filtered(lambda x: x.dayofweek == days_dict.get(day_checkin)).tolerance_in
                # tolerance_in_hours = rec.resource_calendar_ids.attendance_ids.filtered(lambda x: x.dayofweek == days_dict.get(day_checkin)).tolerance_in
                hour_from = rec.resource_calendar_ids.attendance_ids.filtered(lambda x: x.dayofweek == days_dict.get(day_checkin)).hour_from
                # if rec.resource_calendar_ids.id == 14 and rec.check_in < :
                if rec.resource_calendar_ids.id == 14:
                    if (int(rec.check_in.strftime("%H")) + 7) >= 21:
                        datetime_tolerance_in = datetime.strptime(rec.check_in.strftime('%Y-%m-%d'), "%Y-%m-%d") + timedelta(hours=tolerance_in_hours) + timedelta(days=1)
                    else:
                        datetime_tolerance_in = datetime.strptime(rec.check_in.strftime('%Y-%m-%d'), "%Y-%m-%d") + timedelta(hours=tolerance_in_hours)
                else:
                    datetime_tolerance_in = datetime.strptime(rec.check_in.strftime('%Y-%m-%d'), "%Y-%m-%d") + timedelta(hours=tolerance_in_hours)

                # hour_from_datetime = datetime.strptime(rec.check_in.strftime('%Y-%m-%d'), "%Y-%m-%d") + timedelta(hours=hour_from)
                hour_to = rec.resource_calendar_ids.attendance_ids.filtered(lambda x: x.dayofweek == days_dict.get(day_checkin)).hour_to
                half_day_calculation = (hour_from-hour_to)/2 + 2


                if rec.check_in > datetime_tolerance_in:
                    rec.late_counter = 0.5
                else:
                    rec.late_counter = 0
                # else:
                #     if (rec.check_in <= datetime_tolerance_in) and (rec.worked_hours >= half_day_calculation):
                #         rec.late_counter = 0
                #     else : 
                #         rec.late_counter = 0.5

            else:
                rec.late_counter = 0

    @api.depends('check_in','check_out','worked_hours')
    def compute_shift_3_counter(self):
        for rec in self:
            checkin = datetime.strptime(rec.check_in.strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S") + timedelta(hours=7)
            check_in_time = checkin.time()
            #time window for checking in
            curr_start_checkin_time = time(21,0,0)
            curr_end_checkin_time = time(23,59,59)
            next_start_checkin_time = time(0,0,0)
            next_end_checkin_time = time(2,0,0)
            #time window for half / full time limitation
            half_time_start = time(5,0,0)
            half_time_end = time(5,59,59)
            full_time_start = time(6,0,0)

            if (rec.check_out):
                checkout = datetime.strptime(rec.check_out.strftime( '%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S") + timedelta(hours=7)
                check_out_time = checkout.time()
                work_hours = rec.worked_hours
                if (check_in_time>=curr_start_checkin_time and check_in_time <= curr_end_checkin_time) or (check_in_time >= next_start_checkin_time and check_in_time <= next_end_checkin_time):
                    if check_out_time <= half_time_start:
                        rec.shift_3_counter = 0
                    elif check_out_time >= half_time_start and check_out_time <= half_time_end and work_hours > 5.0:
                        rec.shift_3_counter = 0.5
                    elif check_out_time >= full_time_start and work_hours < 6.0:
                        rec.shift_3_counter = 0.5
                    elif check_out_time >= full_time_start and work_hours > 6.0:
                        rec.shift_3_counter = 1    
                    else:
                        rec.shift_3_counter = 0
                else:
                    rec.shift_3_counter = 0
            
    @api.depends('resource_calendar_ids', 'check_in')
    def compute_should_hour_from(self):
        days_dict = {
            'Monday'    : '0',
            'Tuesday'   : '1',
            'Wednesday' : '2',
            'Thursday'  : '3',
            'Friday'    : '4',
            'Saturday'  : '5',
        }
        for rec in self:
            day_checkin = rec.check_in.today().strftime('%A')
            tolerance_in_hours = rec.employee_id.resource_calendar_ids.attendance_ids.filtered(lambda x: x.dayofweek == days_dict.get(day_checkin)).tolerance_in
            should_hour_to = rec.employee_id.resource_calendar_ids.attendance_ids.filtered(lambda x: x.dayofweek == days_dict.get(day_checkin)).hour_to

            rec.should_hour_from = rec.employee_id.resource_calendar_ids.attendance_ids.filtered(lambda x: x.dayofweek == days_dict.get(day_checkin)).hour_from
            rec.should_tolerance_in_hours = tolerance_in_hours
            rec.should_hour_to = should_hour_to

    def action_refresh_data(self):
        # compute late & shift 3
        self.compute_late_time()
        self.compute_shift_3_counter()    