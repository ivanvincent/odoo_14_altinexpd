from odoo import api, models, fields, exceptions
import logging
_logger = logging.getLogger(__name__)
from . import terbilang as tmb
from odoo.exceptions import UserError


class TjAccountJournal(models.Model):
    _inherit = 'account.journal'

    bk_seq_id = fields.Many2one('ir.sequence', string='Seq Cashbank Receipt', required=False,)
    bk_seq_out_id = fields.Many2one('ir.sequence', string='Seq Cashbank Pyment', required=False,)
    bk_seq_line_id  = fields.Many2one('ir.sequence', string='Seq Cashbank Line Number', required=False,)

class Bankstatement(models.Model):
    _inherit = 'account.bank.statement'    


    # @api.multi
    @api.depends('line_ids.amount','balance_end','balance_end_real')
    def _compute_in_out(self):
        for me_id in self :
            me_id.total_in = sum([line.amount if line.amount > 0 else 0 for line in me_id.line_ids])
            me_id.total_out = sum([line.amount if line.amount <= 0 else 0 for line in me_id.line_ids])
            me_id.balance_end_real = me_id.balance_end

    total_in = fields.Monetary('Total In', compute='_compute_in_out', store=True)
    total_out = fields.Monetary('Total Out', compute='_compute_in_out', store=True)

    partner_id = fields.Many2one('res.partner', string="Vendor/Customer", )
    number = fields.Char(string="Source Document", )
    operation_type = fields.Selection([
        ('payment', 'Payment'),
        ('receipt', 'Receipt')],
        "Type",
        required=True, default="payment",)
    
    pengantar = fields.Char(string='Pengantar')
    penyerah = fields.Char(string='Penyerah')
    penerima = fields.Char(string='Penerima')
    terbilang           = fields.Text(string='Terbilang', compute='_compute_terbilang')

    
    def action_open_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pilih Invoice',
            'res_model': 'bank.statement.wizard',
            'view_mode': 'form',
            'context':{'default_statement_id':self.id},
            'target': 'new',
        }
    
    
    
    def _compute_terbilang(self):
        for rec in self:
            rec.terbilang = tmb.terbilang(float(rec.total_in if rec.total_in else abs(rec.total_out)),'IDR', 'id')

    @api.model
    def create(self, vals):
        value = self.env['account.journal'].browse(vals['journal_id'])
        if not value.bk_seq_id or not value.bk_seq_out_id:
            raise exceptions.Warning('Bankcash sequence id belum di set!')
        else:
            seq = self.env['ir.sequence'].browse(int(value.bk_seq_id))
            if self._context.get('default_operation_type') == 'payment' or vals.get('operation_type') == 'payment':
                seq = self.env['ir.sequence'].browse(int(value.bk_seq_out_id))
            vals['name'] = seq.next_by_id()
            res = super(Bankstatement, self).create(vals)
            return res
    


    @api.onchange('line_ids')
    def onchange_partner_id(self):
        if self.line_ids:
            self.partner_id = self.line_ids[0].partner_id.id

class BankstatementLine(models.Model):
    _inherit = 'account.bank.statement.line'    

    # CUSTOM CODE TO SORT BANK STATEMENT LINE BY NUMBER
    _order = 'id asc'

    employee_id     = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False,track_visibility='onchange', )
    an_giro         = fields.Char(string="A.n Giro", required=False, track_visibility='onchange', )
    no_giro         = fields.Char(string="No Giro", required=False, track_visibility='onchange', )
    tgl_jt          = fields.Date(string="Tgl Jatuh Tempo", required=False, track_visibility='onchange', )
    no_po           = fields.Char(string="No Po", required=False, track_visibility='onchange', )
    no_receive      = fields.Char(string="No Receive", required=False, track_visibility='onchange', )
    number          = fields.Char(string="Number", )
    journal_id_2    = fields.Many2one('account.journal', string='Journal 2', related="move_id.journal_id", )
    date_2          = fields.Date(string='Date 2', related="move_id.date", store=True,)
    ref_2           = fields.Char(string='Ref 2', related="move_id.ref", store=True,)
    narration_2     = fields.Text(string='Narration 2')
    kategori_id     = fields.Many2one('kategori.kas', string='Kategori')
    debit           = fields.Monetary('Debit')
    credit          = fields.Monetary('Credit')
    invoice_id      = fields.Many2one('account.move', string='Invoice')
    amount_total    = fields.Monetary(string='Inv Total',compute='_compute_outstanding')
    outstanding     = fields.Monetary(compute='_compute_outstanding', string='Outstanding', store=False)
    
    
    
    
    @api.model_create_multi
    def create(self, vals_list):
        res = super(BankstatementLine, self).create(vals_list)
        import logging;
        _logger = logging.getLogger(__name__)
        _logger.warning('='*40)
        _logger.warning('vals_list')
        _logger.warning(vals_list)
        _logger.warning('='*40)
        
        return res
        
    
    
    def _seek_for_lines(self):
        res = super(BankstatementLine, self)._seek_for_lines()
        liquidity_lines, suspense_lines, other_lines = res
        to_delete = [x.id for x in self.move_id.line_ids.filtered(lambda l:l.credit == 0.0 and l.debit == 0.0)]
        # for line in liquidity_lines.filtered(lambda l:l.id in to_delete):
        #     line.unlink()
        # liquidity_lines = liquidity_lines.filtered(lambda l:l.id  not in to_delete)
        # for line in suspense_lines.filtered(lambda l:l.id in to_delete):
        #     line.unlink()
        # for line in other_lines.filtered(lambda l:l.id in to_delete):
        #     line.unlink()
        # import logging;
        # _logger = logging.getLogger(__name__)
        # _logger.warning('='*40)
        # _logger.warning('on _seek_for_lines')
        # # _logger.warning()
    
        # _logger.warning('liquidity_lines')
        # # _logger.warning([(line.account_id.name,line.credit,line.debit) for line in liquidity_lines])
        # _logger.warning(len(liquidity_lines))
        # _logger.warning('suspense_lines')
        # _logger.warning(suspense_lines)
        # _logger.warning('other_lines')
        # _logger.warning([x.account_id.name for x in other_lines])
        # # raise UserError('Mohon maaf tidak bisa ..')
        # _logger.warning('='*40)
        return res
        
    
    @api.depends('partner_id','credit','debit')
    def _compute_outstanding(self):
        for line in self:
            if line.partner_id and line.invoice_id and line.invoice_id.payment_state == 'not_paid':
                line.amount_total = line.invoice_id.amount_total
                line.outstanding = line.amount_total - line.credit if line.credit else 0
            elif line.partner_id and line.invoice_id and line.invoice_id.payment_state == 'partial':
                line.amount_total = line.invoice_id.amount_residual
                line.outstanding = line.invoice_id.amount_residual - line.credit
            else :
                line.outstanding = 0
                line.amount_total  = 0
    

    @api.onchange('credit','debit')
    def onchange_credit(self):
        for line in self:
            line.amount = line.debit - line.credit


    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.partner_id = self.employee_id.partner_id.id


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False,
                                  track_visibility='onchange', )
    an_giro = fields.Char(string="A.n Giro", required=False, track_visibility='onchange', )
    no_giro = fields.Char(string="No Giro", required=False, track_visibility='onchange', )
    tgl_jt = fields.Date(string="Tgl Jatuh Tempo", required=False, track_visibility='onchange', )
