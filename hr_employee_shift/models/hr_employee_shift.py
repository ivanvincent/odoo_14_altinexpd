# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _

class HrEmployeeModifiedShift (models.Model):
    _inherit = "resource.calendar.attendance"

    tolerance_in = fields.Float('Tolerance In')
    shift3_flag = fields.Boolean('Shift3 Flag')
    day_period = fields.Selection([('morning', 'Morning'), ('afternoon', 'Afternoon'),('evening', 'Evening'),], required=True, default='morning')

class HrEmployeeInherited(models.Model):
    _inherit = 'hr.employee'

    resource_calendar_ids = fields.Many2one('resource.calendar', 'Working Hours',)


class HrEmployeeShift(models.Model):
    _inherit = 'resource.calendar'

    def _get_default_attendance_ids(self):
        return [
            (0, 0, {'name': _('Monday Morning'), 'dayofweek': '0', 'hour_from': 8, 'tolerance_in':8.50, 'hour_to': 12, 'shift3_flag': 0}),
            (0, 0, {'name': _('Monday Afternoon'), 'dayofweek': '0','day_period': 'afternoon', 'hour_from': 13, 'tolerance_in':13.25, 'hour_to': 16,'shift3_flag': 0}),
            (0, 0, {'name': _('Tuesday Morning'), 'dayofweek': '1', 'hour_from': 8, 'tolerance_in':8.50, 'hour_to': 12,'shift3_flag': 0}),
            (0, 0, {'name': _('Tuesday Afternoon'), 'dayofweek': '1', 'day_period': 'afternoon', 'hour_from': 13, 'tolerance_in':13.25,'hour_to': 16,'shift3_flag': 0}),
            (0, 0, {'name': _('Wednesday Morning'), 'dayofweek': '2', 'hour_from': 8, 'tolerance_in':8.50, 'hour_to': 12,'shift3_flag': 0}),
            (0, 0, {'name': _('Wednesday Afternoon'), 'dayofweek': '2', 'day_period': 'afternoon', 'hour_from': 13, 'tolerance_in':13.25,'hour_to': 16,'shift3_flag': 0}),
            (0, 0, {'name': _('Thursday Morning'), 'dayofweek': '3', 'hour_from': 8, 'tolerance_in':8.50, 'hour_to': 12,'shift3_flag': 0}),
            (0, 0, {'name': _('Thursday Afternoon'), 'dayofweek': '3', 'day_period': 'afternoon', 'hour_from': 13, 'tolerance_in':13.25,'hour_to': 16,'shift3_flag': 0}),
            (0, 0, {'name': _('Friday Morning'), 'dayofweek': '4', 'hour_from': 8, 'tolerance_in':8.50, 'hour_to': 12,'shift3_flag': 0}),
            (0, 0, {'name': _('Friday Afternoon'), 'dayofweek': '4', 'day_period': 'afternoon', 'hour_from': 13, 'tolerance_in':13.25, 'hour_to': 16,'shift3_flag': 0}),
            (0, 0, {'name': _('Saturday Morning'), 'dayofweek': '5', 'hour_from': 8, 'tolerance_in':8.50, 'hour_to': 13,'shift3_flag': 0}),
        ]

    color = fields.Integer(string='Color Index', help="Color")
    hr_department = fields.Many2one('hr.department', string="Department", required=True, help="Department")
    sequence = fields.Integer(string="Sequence", required=True, default=1, help="Sequence")
    # harus ditambahkan employee team di modul employee
    group_employee = fields.Selection([
        ('1', 'Tim 1'),
        ('2', 'Tim 2'),
        ('3', 'Tim 3')
    ], string='Tim')
    attendance_ids = fields.One2many(
        'resource.calendar.attendance', 'calendar_id', 'Workingssss Time',
        copy=True, default=_get_default_attendance_ids)

    @api.constrains('sequence')
    def validate_seq(self):
        if self.hr_department.id:
            record = self.env['resource.calendar'].search([('hr_department', '=', self.hr_department.id),
                                                           ('sequence', '=', self.sequence),
                                                           ('company_id', '=', self.company_id.id)
                                                           ])
            if len(record) > 1:
                raise ValidationError("One record with same sequence is already active."
                                      "You can't activate more than one record  at a time")


