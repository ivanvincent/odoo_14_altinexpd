
import time
import logging


from collections import namedtuple
import json
import time

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
# from odoo.addons.procurement.models import procurement
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_is_zero, float_round



_logger = logging.getLogger(__name__)
STATES = [('draft', 'Draft'), ('open', 'Open'), ('close', 'Close'),
         ('reject', 'Reject'), ('posted', 'Out Standing')]


class VitGiro(models.Model):
    _name = 'vit.giro'
    _rec_name = 'name'
    _description = 'Giro'

    @api.depends('giro_invoice_ids')
    def _get_invoices(self):
        for giro in self:
            giro.invoice_names = ' '.join(invoice.name for invoice in giro.giro_invoice_ids.mapped('invoice_id') if invoice)

    name             = fields.Char('Number', help='Nomor Giro', readonly=True, states={'draft': [('readonly', False)]})
    due_date         = fields.Date('Jatuh Tempo', help='', )
    receive_date     = fields.Datetime('Receive Date', help='', readonly=True, default=time.strftime("%Y-%m-%d %H:%M:%S"), states={'draft': [('readonly', False)]})
    clearing_date    = fields.Datetime('Clearing Date', help='', readonly=True, states={'posted': [('readonly', False)]})
    amount           = fields.Float('Amount', help='', readonly=True, states={'draft': [('readonly', False)]})
    partner_id       = fields.Many2one('res.partner', 'Partner', help='', readonly=True,states={'draft': [('readonly', False)]})
    journal_id       = fields.Many2one('account.journal', 'Journal Giro', domain=[('type', '=', 'bank'), ('giro', '=', True)], help='',readonly=True, states={'draft': [('readonly', False)]})
    giro_invoice_ids = fields.One2many('vit.giro.invoice', 'giro_id', readonly=True,states={'draft': [('readonly', False)]})
    invoice_names    = fields.Char(compute='_get_invoices',  string="Allocated Invoices")
    bank_id          = fields.Many2one(comodel_name="res.bank", string="Nama Bank",required=False, store=True, track_visibility='onchange')
    type             = fields.Selection([('payment', 'Payment'),('receipt', 'Receipt')],"Type",required=True, default="receipt", readonly=True, states={'draft': [('readonly', False)]})
    invoice_type     = fields.Char('Invoice Type', readonly=True, default="in_invoice", states={'draft': [('readonly', False)]})
    state            = fields.Selection(string="State", selection=STATES,default=STATES[0][0], required=True, readonly=True)
    account_id       = fields.Many2one('account.account', string="Account Clearing", domain=[('user_type_id.name', '=', 'Bank and Cash')])
    bank_journal_id  = fields.Many2one('account.journal', 'Bank Journal for Clearing', domain=[('type', '=', 'bank'), ('giro', '=', False)])
    statement_ids    = fields.Many2many(comodel_name='account.bank.statement', relation='abs_giro_rel',string='Statement')
    cleared          = fields.Boolean(string='Cleared ?')
    statement_count  = fields.Integer(string='Statement Count',compute="_get_statements")
    payment_ids = fields.Many2many(
        comodel_name='account.payment', 
        relation='account_giro_payment_rel',
        compute='_get_payments',
        string='Payments'
        )
    
    
    
    _sql_constraints = [('name_uniq', 'unique(name)',
                         _('Nomor Giro tidak boleh sama'))]

    def _get_payments(self):
        for giro in self:
            giro.payment_ids = [(4,line.payment_id.id) for line in giro.giro_invoice_ids]
    
    
    def _get_statements(self):
        for giro in self:
            giro.statement_count = len(giro.statement_ids)
    
    def action_view_statement(self):
        action = self.env.ref('tj_bankcash.action_bank_statement_in').read()[0]
        if self.type == 'payment':
            action = self.env.ref('tj_bankcash.action_bank_statement_out').read()[0]
        action['domain'] = [('id','in',self.statement_ids.ids)]
        action['context'] = {}
        return action
    
    def action_open_giro_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pilih Invoice',
            'res_model': 'giro.inv.wizard',
            'view_mode': 'form',
            'context': {'default_partner_id': self.partner_id.id, 'default_giro_id': self.id},
            'target': 'new',
        }


    def validate_payment(self):
        payment_obj = self.env["account.payment"]
        for giro in self:
            for inv in giro.invoice_ids:
                if inv.amount_total != 0:
                    if giro.type == 'payment':
                        payment_method = self.env['account.payment.method'].search(
                            [('payment_type', '=', 'outbound')])
                        partner_type = 'supplier'
                        payment_type = 'outbound'
                    elif giro.type == 'receipt':
                        payment_method = self.env['account.payment.method'].search(
                            [('payment_type', '=', 'inbound')])
                        partner_type = 'customer'
                        payment_type = 'inbound'
                    if len(payment_method) > 1:
                        payment_method = payment_method[0]
                    vals = {
                        'journal_id': giro.journal_id.id,
                        'partner_id': giro.partner_id.id,
                        'payment_method_id': payment_method.id,
                        'partner_type': partner_type,
                        'amount': giro.amount,
                        'communication': inv.number,
                        'payment_type': payment_type,
                        'invoice_ids': [(4, inv.id, None)],
                    }

                    acc_payment_id = payment_obj.create(vals)
                    acc_payment_id.post()

   

    def _cek_total(self):
        inv_total = 0.0
        for giro in self:
            for gi in giro.giro_invoice_ids:
                inv_total += gi.amount

            if giro.amount == inv_total:
                return True

        return False

    _constraints = [(_cek_total, _('Total amount allocated for the invoices must be the same as total Giro amount'),
                     ['amount', 'giro_invoice_ids'])]

    
    
    
    
    def action_cancel(self):
        data = {'state': STATES[0][0]}
        if self.statement_ids:
            for statement in self.statement_ids:
                statement.button_reopen()
                statement.unlink()
        
        if self.payment_ids:
            for payment in self.payment_ids:
                payment.action_draft()
                payment.unlink()
              
        self.write(data)

   
    def action_confirm(self):
        data = {'state': STATES[1][0]}
        if any(invoice.amount < 1 for invoice in self.giro_invoice_ids):
            raise UserError('Mohon maaf jumlah alokasi tidak boleh 0')
        elif self.amount < 1:
            raise UserError('Mohon maaf jumlah Giro tidak boleh 0')
        elif self.amount < sum(self.giro_invoice_ids.mapped('amount')):
            raise UserError('Mohon maaf jumlah alokasi melibihi jumlah giro')
            
        self.write(data)

    # posting langsung kurangi piutang here
   
    def action_post(self):
        # return self.create_abs()
        for line in self.giro_invoice_ids:
            line.validate_payment()
        self.write({'state': 'posted'})
    
    
    def create_abs(self):
        statement_id = self.env['account.bank.statement']
        # operation_type = 
        line_ids = []
        if not self.statement_ids:
            for line in self.giro_invoice_ids:
                line_ids +=  [(0,0,{
                        "date"       :fields.Date.today(),
                        "partner_id" :line.invoice_id.partner_id.id,
                        "payment_ref":line._get_label_payment(line.invoice_id),
                        "invoice_id" :line.invoice_id.id,
                        "credit"     :line.amount
                        
                    })]
                
            values = {
                "journal_id": self.journal_id.id,
                "operation_type":'payment',
                "date":fields.Date.today(),
                "line_ids": line_ids
                
            }
            
            statement_id = statement_id.create(values)
            if statement_id:
                self.statement_ids = [(4,statement_id.id)]
                for line in statement_id.line_ids:
                    line.onchange_credit()
                statement_id.button_post()
                self.write({'state':'posted'})

                return {
                    "type": "ir.actions.client",
                    "tag": "bank_statement_reconciliation_view",
                    "context": {
                        "is_giro": True,
                        "statement_line_ids": statement_id.line_ids.ids,
                        "company_ids": statement_id.mapped("company_id").ids,
                    },
                }
        else:
            
            if self.statement_ids[0].state == 'new':
                self.statement_ids[0].button_post()
            
            return {
                "type": "ir.actions.client",
                "tag": "bank_statement_reconciliation_view",
                "context": {
                    "is_giro": True,
                    "statement_line_ids": self.statement_ids[0].line_ids.ids,
                    "company_ids": self.statement_ids[0].mapped("company_id").ids,
                },
            }
            
            
            

   
    def action_clearing(self):
        self.ensure_one()

        if self.due_date >= fields.Date.today():
            raise UserError(_('Belum Masuk Tanggal Jatuh Tempo'))


        move_obj = self.env['account.move']
        if not self.clearing_date and self.type == 'receipt' and not self.cleared:
            line = []
            val_credit = {
                'date_maturity': False,
                'name': self.name,
                'debit': 0,
                'credit': self.amount,
                'account_id': self.journal_id.default_credit_account_id.id,
                'quantity': 1,
                'analytic_account_id': False,
                'partner_id': self.partner_id.id
            }
            line.append((0, 0, val_credit))

            val_debt = {
                'date_maturity': False,
                'name': self.name,
                'debit': self.amount,
                'credit': 0,
                'account_id': self.bank_journal_id.default_debit_account_id.id,
                'quantity': 1,
                'analytic_account_id': False,
                'partner_id': self.partner_id.id
            }
            line.append((0, 0, val_debt))
            move_vals = {

                'name': self.name,
                'ref': self.name,
                'line_ids': line,
                'journal_id': self.bank_journal_id.id,
                'date': fields.Date.context_today(self) or self.date,  # REVISI
                'narration': ' ',
                'company_id': self.bank_journal_id.company_id.id
            }

            move = move_obj.create(move_vals)
            move.post()
            self.clearing_date = fields.Datetime.now()
            
        elif not self.clearing_date and self.type == 'payment' and not self.cleared:
            statement_id = self.env['account.bank.statement']
            move_line = []
            vals_debit = {
                'date_maturity': False,
                'name': self.name,
                'debit': self.amount,
                'credit': 0,
                'account_id': self.journal_id.payment_credit_account_id.id,
                # 'account_id': self.journal_id.default_account_id.id,
                "reconcile_model_id":2,
                
                'quantity': 1,
                'analytic_account_id': False,
                'partner_id': self.partner_id.id
            }
            move_line.append((0, 0, vals_debit))

            vals_credit = {
                'date_maturity': False,
                'name': self.name,
                'debit': 0,
                'credit': self.amount,
                # 'account_id': self.bank_journal_id.suspense_account_id.id,
                'account_id': self.bank_journal_id.default_account_id.id,
                'quantity': 1,
                "reconcile_model_id":2,
                'analytic_account_id': False,
                'partner_id': self.partner_id.id
            }
            move_line.append((0, 0, vals_credit))
            
            move_vals = {
                'ref': self.name,
                'move_type':'entry',
                'line_ids': move_line,
                'journal_id': self.bank_journal_id.id,
                'date': fields.Date.context_today(self) or self.date,
                'narration': ' ',
                'company_id': self.bank_journal_id.company_id.id
            }
            
            # move_id = move_obj.create(move_vals)
           
            # move_id.post()
            line_ids = []
            # for line in self.giro_invoice_ids:
            #     line_ids += [(0,0,{
            #         "date"       :fields.Date.today(),
            #         "partner_id" :line.invoice_id.partner_id.id,
            #         # "account_id" :self.journal_id.payment_credit_account_id.id,
            #         "account_id" :line.giro_id.journal_id.default_account_id.id,
            #         # "account_id" :self.bank_journal_id.default_account_id.id,
            #         "move_id"    :move_id.id,
            #         "invoice_id":line.invoice_id.id,
            #         "payment_ref": line.giro_id.name,
            #         "credit"     :line.amount
                    
            #     })]
                
            st_values = {
                "journal_id": self.bank_journal_id.id,
                "operation_type":'payment',
                "date":fields.Date.today(),
                # "line_ids":line_ids
                # "move_line_ids":move_line,
                "line_ids": [(0,0,{
                    "date"       :fields.Date.today(),
                    "partner_id" :self.partner_id.id,
                    "payment_ids": [(6,0,self.payment_ids.ids)],
                    # "account_id" :self.journal_id.payment_credit_account_id.id,
                    "account_id" :self.journal_id.default_account_id.id,
                    # "account_id" :self.bank_journal_id.default_account_id.id,
                    # "move_id"    :move_id.id,
                    # "move_line_ids":move_line,
                    "payment_ref": self.name,
                    "credit"     :self.amount
                    
                })]
                
            }
            
            statement_id = statement_id.with_context(is_giro=True).create(st_values)
            import logging;
            _logger = logging.getLogger(__name__)
            # statement_id = statement_id.with_context(skip_account_move_synchronization=True).create(st_values)
            if statement_id:
                self.statement_ids = [(4,statement_id.id)]
                # for ml in move_id.line_ids.filtered(lambda l: l.credit == 0.0 and l.debit == 0.0):
                #     ml.with_context(force_delete=True).unlink()
                    
                for line in statement_id.line_ids:
                    # line.move_id.unlink()
                    _logger.warning('='*40)
                    _logger.warning(line.move_id.account_id.name)
                    _logger.warning('='*40)
                    # line.write({"move_id":move_id.id})
                    _logger.warning('='*40)
                    _logger.warning(line.move_id.account_id.name)
                    _logger.warning('='*40)
                
                    line.onchange_credit()
                    # _logger.warning([x.unlink() for x in line.move_id.line_ids.filtered(lambda l: l.credit == 0.0 and l.debit == 0.0)])
                
                      
            
                _logger.warning('='*40)
                _logger.warning(statement_id.move_line_count)
                _logger.warning('='*40)
                
                # raise UserError('Mohon maaf tidak bisa ..')
                
                statement_id.button_post()
                
                
                
                # self.cleared = True
                
                return {
                    "type": "ir.actions.client",
                    "tag": "bank_statement_reconciliation_view",
                    "context": {
                        "is_giro": True,
                        "statement_line_ids": statement_id.line_ids.ids,
                        "company_ids": statement_id.mapped("company_id").ids,
                    },
                }

        # return self.write({'state': 'close'})


   

    def action_reject(self):
        data = {'state': STATES[3][0]}
        self.write(data)

    @api.onchange('type')
    def on_change_type(self):
        inv_type = 'in_invoice'
        if self.type == 'payment':
            inv_type = 'in_invoice'
        elif self.type == 'receipt':
            inv_type = 'out_invoice'
        self.invoice_type = inv_type
        
    @api.onchange('partner_id')
    def on_change_partner(self):
        if self.state == 'draft':
            self.giro_invoice_ids = False


class VitGiroInvoice(models.Model):
    _name = 'vit.giro.invoice'
    _description = 'Giro vs Invoice'

    giro_id    = fields.Many2one('vit.giro', 'Giro', help='')
    move_id    = fields.Many2one('account.move', string='Journal Entry',)
    payment_id = fields.Many2one('account.payment', string='Payment')
    invoice_id = fields.Many2one('account.move', 'Invoice',help='Invoice to be paid',domain=[('state', '=', 'posted'),('payment_state', 'in', ('not_paid','partial'))])
    # 'amount_invoice': fields.related("invoice_id", "residual",
    #             relation="account.invoice",
    #             type="float", string="Invoice Amount", store=True),
    amount_invoice = fields.Float('Invoice Amount')
    amount         = fields.Float('Amount Allocated')

    @api.onchange('invoice_id')
    def on_change_invoice_id(self):
        self.amount_invoice = self.invoice_id.amount_total

    def _get_label_payment(self,invoice):
        return ' '.join(label for label in invoice.line_ids.filtered(lambda l: not l.product_id and l.exclude_from_invoice_tab and l.credit > 0).mapped('name') if label)
        
        

    def validate_payment(self):
        for line in self:
            payment_obj = self.env["account.payment"]
            if line.amount != 0:
                if line.giro_id.type == 'payment':
                    payment_method = self.env['account.payment.method'].search(
                        [('payment_type', '=', 'outbound')])
                    partner_type = 'supplier'
                    payment_type = 'outbound'
                    # partner_type = 'customer'
                    # payment_type = 'inbound'
                elif line.giro_id.type == 'receipt':
                    payment_method = self.env['account.payment.method'].search(
                        [('payment_type', '=', 'inbound')])
                    # partner_type = 'supplier'
                    # payment_type = 'outbound'
                    partner_type = 'customer'
                    payment_type = 'inbound'
                if len(payment_method) > 1:
                    payment_method = payment_method[0]
                    
                
                move = self.env['account.move'].create({
                    "ref":self._get_label_payment(line.invoice_id),
                    'move_type':'entry',
                    'journal_id':line.giro_id.journal_id.id,
                    'partner_id':line.giro_id.partner_id.id,
                    
                    
                })
                if move:
                    line.move_id = move.id
                vals = {
                    'journal_id': line.giro_id.journal_id.id,
                    'partner_id': line.giro_id.partner_id.id,
                    'payment_method_id': payment_method.id,
                    'partner_type': partner_type,
                    'amount': line.amount,
                    'move_id':move.id,
                    'payment_type': payment_type,
                }
                if not line.payment_id:
                    acc_payment_id = payment_obj.create(vals)
                    line.payment_id = acc_payment_id.id
                    acc_payment_id.action_post()


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    giro_invoice_ids = fields.One2many(
        'vit.giro.invoice', 'invoice_id', string="Giro")


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    giro = fields.Boolean(string="Journal Giro")
