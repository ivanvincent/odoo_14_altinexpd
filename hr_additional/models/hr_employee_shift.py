from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrEmployee(models.Model):
    _name = 'hr.employee.shift'

    name        = fields.Char(string='Shift')
    description = fields.Text(string='Description')
    