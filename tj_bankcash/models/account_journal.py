from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_kas_pembelian = fields.Boolean(string='Kas Pembelian ?')