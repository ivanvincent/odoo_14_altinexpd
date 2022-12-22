from odoo import models, fields, api, _
from odoo.exceptions import UserError

class NamaModel(models.Model):
    _inherit = 'hr.employee'

    employee_team = fields.Selection([
        ('1', 'Tim 1'),
        ('2', 'Tim 2'),
        ('3', 'Tim 3')
    ], string='Employee Team')
    


    