from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    account_budget_id = fields.Many2one('account.budget.post', 'Budget')