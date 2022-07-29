from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountAccount(models.Model):
    _inherit = 'account.account'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Acc.')