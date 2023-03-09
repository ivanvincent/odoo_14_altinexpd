from odoo import models, fields, api, _
from odoo.exceptions import UserError



class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'
    
    # pencairan_id = fields.Many2one(related="line_ids.pencairan_id", string='Pencairan')

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'
    
    pencairan_id = fields.Many2one('uudp.pencairan', string='Pencairan')

    