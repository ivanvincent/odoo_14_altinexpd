from odoo import models, fields, api

class SettingMachine(models.Model):
    _name = 'setting.machine'

    machine_id = fields.Many2one('mrp.machine', string='Machine')
    time_setting = fields.Float(string='Time Setting')
    employee_id = fields.Many2one('hr.employee', string='Setter')
    workorder_id = fields.Many2one('mrp.workorder', string='Workorder')