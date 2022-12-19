from odoo import api, fields, models, _

class Hr_job(models.Model):
    _name = 'hr.job'
    _inherit = 'hr.job'

    #additional field
    batch_recruitment  = fields.Integer(string="Batch Recruitment", readonly=True, default=1)

    
    def set_recruit(self):
        for record in self:
            no_of_recruitment = 1 if record.no_of_recruitment == 0 else record.no_of_recruitment
            batch = 0
            batch = record.batch_recruitment + 1
            record.write({'state': 'recruit', 'no_of_recruitment': no_of_recruitment, 'batch_recruitment': batch,})
        return True
