from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    account_budget_id = fields.Many2one('account.budget.post', 'Budget', related="order_id.account_budget_id")
