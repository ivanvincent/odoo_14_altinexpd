from odoo import fields, models, api, _
from odoo.exceptions import UserError

class BankStatementWizard(models.TransientModel):

    _name = 'bank.statement.wizard'
    
    
    statement_id = fields.Many2one('account.bank.statement', string='Statement')
    credit_notes = fields.Text(string='Notes',help="Label pada line bank statement",required=True, )
    invoice_ids  = fields.Many2many(comodel_name='account.move', relation='bank_statement_invoice_rel',string='Invoice')

    

    def action_add_bank_cash(self):
        line_ids = []
            
        for invoice in self.invoice_ids:
            if invoice.id in [ inv.id for inv in self.statement_id.line_ids.mapped('invoice_id')]:
                raise UserError('Mohon maaf invoice %s sudah dimasukan'%(invoice.name))
            else:
                line_ids += [(0,0,{
                    "invoice_id":invoice.id,
                    "date":invoice.invoice_date,
                    "partner_id":invoice.partner_id.id,
                    "credit":invoice.amount_total if invoice.state == 'not_paid' else invoice.amount_residual,
                    "payment_ref":self.credit_notes,
                })]
            
            
        if self.statement_id and line_ids:
            self.statement_id.update({"line_ids": line_ids})
            for line in self.statement_id.line_ids:
                line.onchange_credit()