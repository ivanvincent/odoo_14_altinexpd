from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrEmployeeGolongan(models.Model):
    _name = 'hr.employee.golongan'

    name        = fields.Char(string='Golongan')
    description = fields.Text(string='Description')