from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_coa_pph = fields.Boolean(string='Coa PPH ?')
    is_coa_penyesuaian = fields.Boolean(string='Coa Penyesuaian ?')