from odoo import api, fields, models, _

class Hr_job(models.Model):
    _name = 'hr.job'
    _inherit = 'hr.job'

    #additional field
    active             = fields.Boolean(string="Is Active")
