from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError
from datetime import timedelta

class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    # Start Override From base odoo
    def _attendance_action_change(self):
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """
        self.ensure_one()
        action_date = fields.Datetime.now()
        attendance_checked_out = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '!=', False)], limit=1)
        # self.check_out_waiting_time(attendance_checked_out, action_date)
        if self.attendance_state != 'checked_in':
            if(attendance_checked_out):
                self.check_in_once_per_day(attendance_checked_out,action_date)
            else:
                vals = {
                    'employee_id': self.id,
                    'check_in': action_date,
                    'resource_calendar_ids': self.resource_calendar_ids.id
                }
                return self.env['hr.attendance'].create(vals)
        
        attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)
        # self.check_waiting_time(attendance, action_date)
        if attendance:
            attendance.check_out = action_date
        else:
            raise exceptions.UserError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.sudo().name, })
        return attendance
    # End Override From base odoo

    def check_waiting_time(self, attendance, date_now):
        if date_now <= attendance.time_waiting:
            raise exceptions.UserError(_('Thank you, you have already checked in before'))

    def check_out_waiting_time(self, attendance, date_now):
        if attendance.time_waiting_co:
            if date_now <= attendance.time_waiting_co:
                raise exceptions.UserError(_('Thank you, you have already checked out before'))
            
    def check_in_once_per_day(self,attendance,date_now):
        previousCheckInDate = attendance.check_in.date()
        todayCheckInDate = date_now.date()
        if previousCheckInDate == todayCheckInDate:
            raise UserError('Check In hanya bisa 1x')
                