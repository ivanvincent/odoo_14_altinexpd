from odoo import api, models, fields, exceptions
import logging
_logger = logging.getLogger(__name__)


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
    # readonly=True, states={'draft': [('readonly', False)]}

    @api.model
    def create(self, vals):
        value = self.env['account.journal'].browse(vals['journal_id'])
        if not value.bk_seq_id or not value.bk_seq_out_id:
            raise exceptions.Warning('Bankcash sequence id belum di set!')
        else:
            if vals['operation_type'] == 'payment':
                seq = self.env['ir.sequence'].browse(int(value.bk_seq_out_id))
            else:
                seq = self.env['ir.sequence'].browse(int(value.bk_seq_id))
            kode = str(seq.code) or ''
            vals['name'] = self.env['ir.sequence'].next_by_code(kode)
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

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False,
                                  track_visibility='onchange', )
    an_giro = fields.Char(string="A.n Giro", required=False, track_visibility='onchange', )
    no_giro = fields.Char(string="No Giro", required=False, track_visibility='onchange', )
    tgl_jt = fields.Date(string="Tgl Jatuh Tempo", required=False, track_visibility='onchange', )
    no_po = fields.Char(string="No Po", required=False, track_visibility='onchange', )
    no_receive = fields.Char(string="No Receive", required=False, track_visibility='onchange', )
    number = fields.Char(string="Number", )
    journal_id_2 = fields.Many2one('account.journal', string='Journal 2', related="move_id.journal_id", )
    date_2 = fields.Date(string='Date 2', related="move_id.date", store=True,)
    ref_2 = fields.Char(string='Ref 2', related="move_id.ref", store=True,)
    narration_2 = fields.Text(string='Narration 2')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Qty')
    uom_id = fields.Many2one('uom.uom', string='Uom', related="product_id.uom_id")
    price = fields.Float(string='Price')
    # image_ids = fields.One2many('account.bank.statement.image', 'account_bank_statement_line_id', 'Line')
    order_id = fields.Many2one('store.order', 'Invoice')

    @api.onchange('price','quantity')
    def _onchange_quantity(self):
        if self.price or self.quantity:
            amount = self.price * self.quantity
            self.amount = -abs(amount) if self.statement_id.operation_type == 'payment' else abs(amount)

    # @api.model
    # def create(self, vals):

        # if vals.get('journal_id') == 6:
        #     seq_id = self.env.ref('tj_bankcash.seq_kas_line6')
        # elif vals.get('journal_id') == 21:
        #     seq_id = self.env.ref('tj_bankcash.seq_kas_line6')    
        # elif vals.get('journal_id') == 33:
        #     seq_id = self.env.ref('tj_bankcash.seq_kas_line33')
        # elif vals.get('journal_id') == 37:
        #     seq_id = self.env.ref('tj_bankcash.seq_kas_line37')
        # elif vals.get('journal_id') == 38:
        #     seq_id = self.env.ref('tj_bankcash.seq_kas_line38')
        # elif vals.get('journal_id') == 39:
        #     seq_id = self.env.ref('tj_bankcash.seq_kas_line39')
        # elif vals.get('journal_id') == 40:
        #     seq_id = self.env.ref('tj_bankcash.seq_kas_line40')
        # elif vals.get('journal_id') == 41:
        #     seq_id = self.env.ref('tj_bankcash.seq_kas_line41')
        # elif vals.get('journal_id') == 42:
        #     seq_id = self.env.ref('tj_bankcash.seq_kas_line42')
        # elif vals.get('journal_id') == 43:
        #     seq_id = self.env.ref('tj_bankcash.seq_kas_line43')
        # else:
        #     seq_id = self.env.ref('tj_bankcash.seq_bank_line7')

        # vals['number'] = seq_id.next_by_id()
        # return super(BankstatementLine, self).create(vals)

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.partner_id = self.employee_id.partner_id.id

    # @api.onchange('partner_id')
    # def onchange_employee_id(self):
    #     if self.partner_id:
    #         self.statement_id.partner_id = self.partner_id.id

    def action_show_image(self):
        action = self.env.ref('tj_bankcash.account_bank_statement_image_action').read()[0]
        action['res_id'] = self.id
        action['name'] = "Images of %s" % (self.payment_ref)
        return action

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False,
                                  track_visibility='onchange', )
    an_giro = fields.Char(string="A.n Giro", required=False, track_visibility='onchange', )
    no_giro = fields.Char(string="No Giro", required=False, track_visibility='onchange', )
    tgl_jt = fields.Date(string="Tgl Jatuh Tempo", required=False, track_visibility='onchange', )
