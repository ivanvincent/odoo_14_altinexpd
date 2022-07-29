from odoo import api, fields, models, _
import time
from itertools import groupby
from datetime import datetime, timedelta
from . import terbilang

from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

import odoo.addons.decimal_precision as dp

KB_STATES =[
    ('draft','Draft'),
    ('confirm','Confirm'),
    ('approve_purchasing','Approve Purchasing'),
    ('approve','Approve'),
    ('done','Done'),
    ('cancel','Cancel'),
]

class KontrabonOrder(models.Model):
    _name = 'kontrabon.order'
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'name desc'

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         seq = self.env['ir.sequence'].next_by_code('kontrabon.order') or _('New')
    #         vals['name'] = seq
    #         result = super(KontrabonOrder, self).create(vals)
    #         return result



    @api.model
    def create(self, vals):
        if vals['type_kontra'] == 'in_invoice':
            seq_id = self.env.ref('tj_kontrabon.seq_kontrabon_new')
        else:
            seq_id = self.env.ref('tj_kontrabon.seq_kontrabon_piutang_new')
        vals['name'] = seq_id.next_by_id()
        return super(KontrabonOrder, self).create(vals)


    @api.depends('amount','inv_ids.amount_total')
    def _cek_total_amount(self):
        inv_total = 0.0 
        total_dpp = 0
        for giro in self:
            for gi in giro.inv_ids:
                inv_total += gi.amount_total
                if giro.set_makloon:
                    total_dpp += gi.amount_untaxed
            giro.amount = inv_total - round(total_dpp*2/100) if giro.set_makloon else inv_total


    # @api.model
    # def create(self, vals):
    #     if type_kontra == 'in_invoice':
    #         if vals.get('name', _('New')) == _('New'):
    #             seq = self.env['ir.sequence'].next_by_code('kontrabon.order') or _('New')
    #             vals['name'] = seq
    #             result = super(KontrabonOrder, self).create(vals)
    #             return result
    #     elif
    #         if vals.get('name', _('New')) == _('New'):
    #             seq = self.env['ir.sequence'].next_by_code('kontrabon.order') or _('New')
    #             vals['name'] = seq
    #             result = super(KontrabonOrder, self).create(vals)
    #             return result

        # seq_id = self.env.ref('sale_quotation_number_10.seq_sale_rajut')


    # @api.model
    # def _get_default_name(self):
    #     return self.env['ir.sequence'].next_by_code('delivery.order')

    # name = fields.Char("Name",)
    # name = fields.Char('DO Reference', size=32,
    #                    # required=True,
    #                    # default=_get_default_name,
    #                    track_visibility='onchange')
    name = fields.Char(string='No Kontrabon', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    description = fields.Text(string="Description", required=False, track_visibility='onchange',)
    tanggal = fields.Date(string="Tanggal", required=False, default=lambda self: time.strftime("%Y-%m-%d"),
                          track_visibility='onchange',)
    state = fields.Selection(string="State", selection=KB_STATES, required=True, readonly=True, default=KB_STATES[0][0], track_visibility='onchange',)
    no_kb = fields.Char(string='No KB Manual')
    amount = fields.Float(compute='_cek_total_amount',string='Amount', store=False)

    type_kontra = fields.Selection(string="Type Kontra", selection=[
    ('out_invoice','Piutang'),
    ('in_invoice','Hutang'),
    ], required=True,)

    inv_ids = fields.Many2many('account.move', 'kontrabon_order_line', 'kb_id', 'inv_id', "Invoice List")
    inv_line_ids = fields.One2many(
        comodel_name='account.move.line', 
        inverse_name="kb_id",
        string="Invoice Line List",
        required=False,)

    partner_id = fields.Many2one('res.partner', string='Partner', change_default=True, index=True , required=True , ondelete='restrict')

    # saleorder_ids = fields.One2many(comodel_name="delivery.order.line", inverse_name="delivery_order_id",
    #                                  string="Saleorder", required=False, track_visibility='onchange',)

    # so_ids = fields.Many2many('sale.order', 'delivery.order.line', 'delivery_order_id.id', 'soline.id', '"SO List")
    # saleorder_ids = fields.One2many(comodel_name="delivery.order.line", inverse_name="so_id",
    #                                  string="Saleorder", required=False, track_visibility='onchange',)

    collector_id = fields.Many2one(comodel_name="hr.employee", string="Collector", required=False, store=True,
                               domain=[('job_id.name', 'in', ('COLLECTOR','Collector','collector','SALES','Sales','sales'))], track_visibility='onchange',)

    date_invoice = fields.Date(string='Invoice Date',
    readonly=True, states={'draft': [('readonly', False)]}, index=True,
    help="Keep empty to use the current date", copy=False)
    
    date_due = fields.Date(string='Due Date',
        readonly=True, states={'draft': [('readonly', False)]}, index=True, copy=False,
        help="If you use payment terms, the due date will be computed automatically at the generation "
             "of accounting entries. The payment term may compute several due dates, for example 50% "
             "now and 50% in one month, but if you want to force a due date, make sure that the payment "
             "term is not set on the invoice. If you keep the payment term and the due date empty, it "
             "means direct payment.")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    label = fields.Char(string="Label")
    amount_admin_cost = fields.Float(
        string='Amount',
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
    )
    account_credit_id = fields.Many2one(
        'account.account',
        string='Account Credit',
    )
    account_debit_id = fields.Many2one(
        'account.account',
        string='Account Debit',
    )
    set_makloon = fields.Boolean(string='Set Penjualan ?')
    amount_to_text = fields.Char(string='Terbilang', compute="_compute_terbilang")
    total_journal = fields.Integer(string='Total Journal', compute="_compute_total_journal")
    is_ada_biaya = fields.Boolean(string='Ada Biaya ?', compute="compute_ada_biaya")
    state_2 = fields.Char(string='State 2')
    faktur = fields.Char(string='No Faktur')
    invoice_supplier = fields.Char(string='Invoice Supplier')
    sj_supplier = fields.Char(string='Surat Jalan Supllier')
    tgl_jth_tempo = fields.Date(string='Tanggal Jatuh Tempo')
    tgl_cair = fields.Date(string='Tanggal Cair di Bank')
    bank_id = fields.Many2one('res.bank', string='Bank')
    no_bbk = fields.Char(string='No. BBK')
    no_faktur_pajak = fields.Char(string='No. Faktur Pajak')
    
    # company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id.id, required=True)

    # @api.multi
    def action_draft(self):
        self.state = KB_STATES[0][0]

    # @api.multi
    def action_confirm(self):
        ########################################################################
        ### 
        ### comment dulu
        ### 
        ########################################################################
        # for inv in self.inv_ids:
        #     if self.type_kontra == 'in_invoice':
        #         if not inv.faktur or not inv.invoice_supplier or not inv.sj_supplier:
        #             raise ValidationError("Pastikan seri faktur, Invoice Supplier, Surat Jalan Supllier sudah terisi pada invoice")
                
        self.state = KB_STATES[1][0]
        self.inv_ids.write({'kontrabon_id':self.id})
        if self.is_ada_biaya:
            self.state_2 = 'show_button_approve_purchasing'
        else:
            self.state_2 = 'show_button_approve_2'

    # @api.multi
    def action_cancel(self):
        self.state = KB_STATES[5][0]
        self.inv_ids.write({'kontrabon_id': False})

    def action_done(self):
        # five_percent = (self.amount * 0.05)
        # if self.amount_admin_cost > five_percent:
        #     raise UserError("Mohon maaf amount tidak boleh melebihi 5%")

        self.state = KB_STATES[4][0]
        if self.is_ada_biaya:
            line = []
            for inv in self.inv_ids.filtered(lambda x: x.amount_kb > 0):
                # Credit
                line.append((0, 0, {
                    'partner_id': self.partner_id.id,
                    'account_id': self.account_credit_id.id,
                    'name': self.label,
                    'credit': inv.amount_kb,
                }))

                # Debit
                line.append((0, 0, {
                    'partner_id': self.partner_id.id,
                    'account_id': self.account_debit_id.id,
                    'name': self.label,
                    'debit': inv.amount_kb,
                }))

            move_obj = self.env['account.move'].create({
                'ref': self.name,
                'date': fields.Date.today(),
                'line_ids': line,
                'journal_id': self.journal_id.id,
                'kontrabon_id': self.id,
            })

    # @api.multi
    # def _cek_total(self):
    #     inv_total = 0.0
    #     for giro in self:
    #         for gi in giro.inv_ids:
    #             inv_total += gi.amount_residual_signed
            
    #         if giro.amount == inv_total:
    #             return True
        
    #     return False
    
    def _compute_terbilang(self):
        for rec in self:
            rec.amount_to_text = terbilang.terbilang(float(abs(rec.amount)),'IDR', 'id').replace("Sen", "")
        
    def _compute_total_journal(self):
        move_obj = self.env['account.move'].search([('kontrabon_id', '=', self.id)])
        self.total_journal = len(move_obj)
    
    def action_view_journal_entries(self):
        move_obj = self.env['account.move'].search([('ref', '=', self.name)], limit=1)
        action = {
            'name': 'Journal Entries',
            'view_mode': "form",
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': move_obj.id,
        }
        return action

    @api.depends('inv_ids.amount_kb')
    def compute_ada_biaya(self):
        if sum(self.inv_ids.mapped('amount_kb')) > 0:
            self.is_ada_biaya = True
        else:
            self.is_ada_biaya = False
    
    def action_approve_purchasing(self):
        self.state = 'approve_purchasing'
        if self.is_ada_biaya:
            self.state_2 = False

    def action_approve(self):
        self.state = 'approve'
        if self.state_2 == 'show_button_approve_2':
            self.state_2 = False