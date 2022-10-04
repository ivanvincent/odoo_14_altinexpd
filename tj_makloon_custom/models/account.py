from odoo import fields, api, models

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    no_sj = fields.Char(string='No SJ')
    