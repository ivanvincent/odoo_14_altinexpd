from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RuteSaleExpense(models.Model):
    _name = 'rute.sale.expense'

    name        = fields.Char(string='Expense')
    code        = fields.Char(string='Code')
    account_id  = fields.Many2one('account.account', string='Account',)
    is_active   = fields.Boolean(string='Active ?',default=True)
    description = fields.Text(string='Description')