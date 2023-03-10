from odoo.exceptions import UserError
from odoo import fields, api, models, _

KB_STATES =[
    ('draft','Draft'),
    ('confirm','Confirm'),
    ('approve_purchasing','Approve Purchasing'),
    ('approve','Approve'),
    ('done','Done'),
    ('cancel','Cancel'),
]
class AccountInvoice(models.Model):
    _inherit = "account.move"

    kontrabon_id = fields.Many2one('kontrabon.order', 'Kontrabon', copy=False, track_visibility='onchange',)
    no_surat_jalan = fields.Char(string='Surat Jalan', compute="_compute_no_surat_jalan")
    kontrabon_external = fields.Char(string='Kontrabon External', related='kontrabon_id.no_kb')
    pro_no_sj = fields.Char(string='No SJ',)
    amount_kb = fields.Float(string='Penyesuaian')

    faktur = fields.Char(string='No Faktur')
    invoice_supplier = fields.Char(string='Invoice Supplier')
    sj_supplier = fields.Char(string='Surat Jalan Supllier', 
    # related='picking_id.surat_jalan_supplier',
    readonly=False)
    move_id = fields.Many2one('account.move', string='Number', compute='_compute_move_id')
    state_kb = fields.Selection(string="State KB", selection=KB_STATES, readonly=True, default=KB_STATES[0][0], related='kontrabon_id.state', store=True,)
    norek_id = fields.Many2one('account.journal', string='Norek', domain=[('type', 'in', ['bank', 'cash'])])
    keterangan_transaksi = fields.Char(string='Ket Transaksi')
    account_id = fields.Many2one('account.account', string='COA', default=52)

    @api.onchange('amount_kb')
    def onchange_amount_kb(self):
        amount_kb = self.amount_kb
        five_percent = (self.amount_total * 0.05)
        if amount_kb:
            if amount_kb > five_percent:
                raise UserError(_("Mohon maaf amount tidak boleh melebihi %s (5 percent)") % (str(five_percent)))

    # date_invoice = fields.Date(string='Invoice Date',
    #     readonly=True, states={'draft': [('readonly', False)]}, index=True,
    #     help="Keep empty to use the current date", copy=False)
    # date_due = fields.Date(string='Due Date',
    #     readonly=True, states={'draft': [('readonly', False)]}, index=True, copy=False,
    #     help="If you use payment terms, the due date will be computed automatically at the generation "
    #          "of accounting entries. The payment term may compute several due dates, for example 50% "
    #          "now and 50% in one month, but if you want to force a due date, make sure that the payment "
    #          "term is not set on the invoice. If you keep the payment term and the due date empty, it "
    #          "means direct payment.")
    # origin = fields.Char(string='Source Document',
    #     help="Reference of the document that produced this invoice.",
    #     readonly=True, states={'draft': [('readonly', False)]})

    def _compute_no_surat_jalan(self):
        print('=============_compute_no_surat_jalan===========')
        for a in self:
            if a.journal_id.id == 8:
                pickingObj = self.env['stock.picking'].search([('name','=',a.ref.split('-')[0].replace(" ", ""))])
                a.no_surat_jalan = pickingObj.no_surat_jalan if pickingObj else False
            else:
                a.no_surat_jalan = a.picking_id.no_surat_jalan
    
    def _compute_move_id(self):
        for rec in self:
            rec.move_id = rec.id


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    kb_id = fields.Many2one('kontrabon.order', 'Kontrabon', related='move_id.kontrabon_id')
    kb_account_debit_id = fields.Many2one('account.account', 'Kontrabon Account Debit', related='move_id.kontrabon_id.account_debit_id')
    location_id = fields.Many2one('stock.location', string='Location')