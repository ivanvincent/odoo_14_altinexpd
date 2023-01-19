from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrLeaveAllovation(models.Model):
    _inherit = 'hr.leave.allocation'

    contract_id = fields.Many2one('hr.contract', string='Contract Id')