from odoo import api, fields, models, _

class Hr_job_level(models.Model):
    _name = 'hr.job.level'

    name    		 = fields.Char("Name", required=True)