from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_foh = fields.Boolean(sting='Is Foh ?')
    is_stock = fields.Boolean(string='Stock Finish Good?')