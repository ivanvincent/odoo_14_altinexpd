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
        self.check_out_waiting_time(attendance_checked_out, action_date)
        if self.attendance_state != 'checked_in':
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
                'resource_calendar_ids': self.resource_calendar_ids.id
            }
            return self.env['hr.attendance'].create(vals)
        
        attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)
        if attendance: 
            self.missed_check_out_correction(attendance, action_date) # check-out, lalu otomatis check-in kembali, hanya terjadi jika masih check in setelah 15.5 jam
            self.check_waiting_time(attendance, action_date) # raise error jika check in berulang dalam kurun < 30 menit
            attendance.check_out = action_date # normal check-out
        else:
            raise exceptions.UserError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.sudo().name, })
        return attendance
    # End Override From base odoo

    def check_waiting_time(self, attendance, date_now):
        if date_now <= attendance.time_waiting:
            raise exceptions.UserError(_('You have checked-in during last 30 mins'))

    def check_out_waiting_time(self, attendance, date_now):
        if attendance.time_waiting_co:
            if date_now <= attendance.time_waiting_co:
                raise exceptions.UserError(_('You have checked-out during last 30 mins'))
            
    def missed_check_out_correction(self,attendance,date_now):
        previousCheckInDate = attendance.check_in
        if date_now >= previousCheckInDate + timedelta(hours=15.5):
            attendance.check_out = self.action_date - timedelta(hours=1)
            vals = {
                'employee_id': self.id,
                'check_in': self.action_date,
                'resource_calendar_ids': self.resource_calendar_ids.id
            }
            return self.env['hr.attendance'].create(vals)
            
                