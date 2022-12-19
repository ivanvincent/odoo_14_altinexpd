from odoo import api, fields, models, _
import datetime

class Hr_employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    #additional field
    batch_recruitment  = fields.Integer(string="Batch Recruitment", readonly=True)



