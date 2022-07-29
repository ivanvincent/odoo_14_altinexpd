from odoo import api, fields, models


class DhFptMachineLog(models.Model):
    _name = 'dh.fpt.machine.log'

    name = fields.Char(string='Name', required=True)
    address_id = fields.Many2one('res.partner', string='Working Address', index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True)
    fpt_machine_id = fields.Many2one('dh.fpt.machine', string='Machine IP', index=True)
    fpt_uid = fields.Char(string='UID', index=True)
    fpt_user_id = fields.Char(string='User ID', index=True)
    fpt_punch = fields.Char(string='Punch', index=True)
    fpt_status = fields.Char(string='Status')
    fpt_timestamp = fields.Datetime(string='Timestamp')
    fpt_status_sync = fields.Selection([('draft', 'Draft'),
                                        ('done', 'Done')],
                                       string='Sync',
                                       default='draft')

    def send_log_attendance(self):
        attendance = self.env['hr.attendance']
        for info in self:
            if info.employee_id:
                if info.fpt_machine_id.device_checkin == int(info.fpt_punch):
                    check_attendance = attendance.search([('employee_id', '=', info.employee_id.id),
                                                          ('check_in', '>=',
                                                           info.fpt_timestamp.strftime('%Y-%m-%d 00:00:00')),
                                                          ('check_in', '<=',
                                                           info.fpt_timestamp.strftime('%Y-%m-%d 23:59:59'))])
                    if check_attendance:
                        continue
                    else:
                        attendance.create({'employee_id': info.employee_id.id,
                                           'check_in': info.fpt_timestamp.strftime('%Y-%m-%d %H:%M:%S')})
                        info.fpt_status_sync = 'done'
                elif info.fpt_machine_id.device_checkout == int(info.fpt_punch):
                    check_attendance = attendance.search([('employee_id', '=', info.employee_id.id),
                                                          ('check_in', '>=',
                                                           info.fpt_timestamp.strftime('%Y-%m-%d 00:00:00')),
                                                          ('check_in', '<=',
                                                           info.fpt_timestamp.strftime('%Y-%m-%d 23:59:59'))])
                    if check_attendance:
                        check_attendance.write({'employee_id': info.employee_id.id,
                                                'check_out': info.fpt_timestamp.strftime('%Y-%m-%d %H:%M:%S')})
                        info.fpt_status_sync = 'done'

        view = self.env.ref('dh_popup_message.dh_popup_message_wizard')
        context = dict(self._context or {})
        context['message'] = "Berhasil kirim log ke hr attendance"
        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'dh.popup.message.wizard',
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }
