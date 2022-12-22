from odoo import api, fields, models, exceptions, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

class Hr_applicant(models.Model):
    _name = 'hr.applicant'
    _inherit = 'hr.applicant'

    batch_recruitment  = fields.Integer(string="Batch Recruitment", readonly=True)

    @api.model
    def create(self, vals):
        job_id = vals.get('job_id')
        batch = self.env['hr.job'].search([('id','=',job_id)]).batch_recruitment
        vals['batch_recruitment'] = batch
        return super(Hr_applicant, self).create(vals)

    