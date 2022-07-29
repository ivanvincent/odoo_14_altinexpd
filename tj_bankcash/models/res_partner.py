from email.policy import default
from odoo import models, fields, api, exceptions, _

class ResPartnerTjKasBank(models.Model):
    _inherit = 'res.partner'

    expenses = fields.Boolean(string='Is a Expenses',)
    property_account_expenses_id = fields.Many2one("account.account", "Account Expenses")
    is_created_bills = fields.Boolean(string='Created Bills ?', default=False)
    # contact_sales_id = fields.Many2one('vit.contact', string='Contact')

class VitContact(models.Model):
    _name = 'vit.contact'

    name = fields.Char(string='Sales Name')
