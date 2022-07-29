from odoo import models, fields, api

class HrEmployeeGrop(models.Model):
    _name = 'hr.employee.grop'

    name = fields.Char(string='Grop')
    description = fields.Text(string='Description')
    