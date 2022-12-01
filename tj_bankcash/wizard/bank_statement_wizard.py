from odoo import fields, models, api, _
from odoo.exceptions import UserError
import json

class BankStatementWizard(models.TransientModel):

    _name = 'bank.statement.wizard'
    
    
    statement_id = fields.Many2one('account.bank.statement', string='Statement')
    move_type    = fields.Selection([("receipt","Receipt"),("payment","Payment")], string='Move Type')
    credit_notes = fields.Text(string='Notes',help="Label pada line bank statement",required=True, )
    invoice_ids  = fields.Many2many(comodel_name='account.move', relation='bank_statement_invoice_rel',string='Invoice')
    # [('payment_state', 'in', ('not_paid','partial')),('state', '=', 'posted'),('state_kb', '=', 'approve')]
    invoice_ids_domain = fields.Char(
    compute="compute_invoice_ids_domain",
    readonly=True,
    store=False,
)
    
    @api.depends('move_type')
    def compute_invoice_ids_domain(self):
        for line in self:
            if line.move_type == 'receipt':
                line.invoice_ids_domain  = json.dumps([('move_type','=','out_invoice'),('payment_state', 'in', ('not_paid','partial')),('state', '=', 'posted')])
            else:
                line.invoice_ids_domain  = json.dumps([('move_type','=','in_invoice'),('payment_state', 'in', ('not_paid','partial')),('state', '=', 'posted'),('state_kb', '=', 'approve')])

            
    
    
    
    # @api.model
    # def default_get(self,fields):
    #     res = super(BankStatementWizard,self).default_get(fields)
    #     context = self._context
    #     if context.get('default_operation_type') == 'receipt':
    #         res['move_type'] == 'receipt'
    #     elif context.get('default_operation_type') == 'payment':
    #         res['move_type'] == 'payment'
    #     return res

    
        # return res
    
    def _get_domain_invoice(self):
        domain = []
        context = self._context
        if context.get('default_operation_type') == 'receipt':
            domain = [('move_type','=','out_invoice'),('payment_state', 'in', ('not_paid','partial')),('state', '=', 'posted')]
        elif context.get('default_operation_type') == 'payment':
            domain = [('move_type','=','in_invoice'),('payment_state', 'in', ('not_paid','partial')),('state', '=', 'posted'),('state_kb', '=', 'approve')]
        return domain

    def action_add_bank_cash(self):
        line_ids = []
            
        for invoice in self.invoice_ids:
            if invoice.id in [ inv.id for inv in self.statement_id.line_ids.mapped('invoice_id')]:
                raise UserError('Mohon maaf invoice %s sudah dimasukan'%(invoice.name))
            else:
                if self.move_type == 'receipt':
                    line_ids += [(0,0,{
                        "invoice_id":invoice.id,
                        "date":self.statement_id.date,
                        "partner_id":invoice.partner_id.id,
                        "debit":invoice.amount_total if invoice.state == 'not_paid' else invoice.amount_residual,
                        "payment_ref":self.credit_notes,
                    })]
                else:
                    line_ids += [(0,0,{
                        "invoice_id":invoice.id,
                        "date":self.statement_id.date,
                        "partner_id":invoice.partner_id.id,
                        "credit":invoice.amount_total if invoice.state == 'not_paid' else invoice.amount_residual,
                        "payment_ref":self.credit_notes,
                    })]
            
            
        if self.statement_id and line_ids:
            self.statement_id.update({"line_ids": line_ids})
            for line in self.statement_id.line_ids:
                line.onchange_credit()