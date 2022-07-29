from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrEmployeeKelompok(models.Model):
    _name = 'hr.employee.kelompok'

    name        = fields.Char(string='Kelompok')
    description = fields.Text(string='Description')
    