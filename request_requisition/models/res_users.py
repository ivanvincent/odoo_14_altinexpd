from odoo import models, fields, api, _
from odoo.exceptions import UserError

class NamaModel(models.Model):
    _inherit = 'res.users'

    approver_rr_id = fields.Many2one('res.users', string='Approver RR')
    