from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_team = fields.Selection([
        ('1', 'Tim 1'),
        ('2', 'Tim 2'),
        ('3', 'Tim Netral'),
        ('4', 'Staff Non-Produksi'),
        ('5', 'Staff Produksi Tidak Langsung'),
        ('6', 'Tim Netral Non-Shift'),
    ], string='Employee Team')
    
    
    

    