from shutil import move
from xml import dom
from odoo import api, fields, models, _
import time
from itertools import groupby
from datetime import datetime, timedelta

from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

import odoo.addons.decimal_precision as dp
import pandas as pd


MUTASI_STATES = [('draft', 'Draft'), ('confirm', 'Confirm'),
                    ('done', 'Done'), ('cancel', 'Cancel'), ]


# class AccountMoveLine(models.Model):
#     _inherit = 'account.move.line'

#     state = fields.Selection([("draft","Unposted"),("posted","Posted")], string='State', related='move_id.state', store=True,)

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    kolom_ar = fields.Integer(string="Kolom Mutasi AR")
    kolom_ap = fields.Integer(string="Kolom Mutasi AP")
    reverse_ar = fields.Boolean(
        string="PDF Reverse AR",
        default=0)
    reverse_ap = fields.Boolean(
        string="PDF Reverse AP",
        default=0)
    # _sql_constraints = [
    #     ('nama_kolomar_uniq', 'unique(kolom_ar)', 'Kolom must be unique !'),
    #     ('nama_kolomap_uniq', 'unique(kolom_ap)', 'Kolom must be unique !'),
    # ]


class BlessingMutasiPartnerReportLine(models.Model):
    _name = 'blessing.mutasi.partner.report.line'
    _description = 'Blessing Mutasi Partner Report Line'
    _order = 'group_partner_id,partner_id asc'

    urut = fields.Integer(string="Urut")
    date = fields.Date(string='Tanggal')
    name = fields.Char(string="Keterangan")
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='No Journal')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner')
    group_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Group Partner')
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account')
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal')
    # init_ids   = fields.Float(string="Opening", digits=dp.get_precision('Account'))
    opening = fields.Float(string="Opening", digits=dp.get_precision('Account'))
    debet = fields.Float(string="Debet", digits=dp.get_precision('Account'))
    credit = fields.Float(string="Credit", digits=dp.get_precision('Account'))
    balance = fields.Float(string="Closing", digits=dp.get_precision('Account'))
    state_line = fields.Selection(
        [('draft', 'Draft'), ('posted', 'Post'), ('all', 'All')], string="Status Journal")


class BlessingMutasiPartnerReport(models.Model):
    _name = 'blessing.mutasi.partner.report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id asc'

    mutasi_company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        string='Company',
        required=True,
        ondelete='cascade')
    name = fields.Char(
        string='Nomor Report',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New'))
    description = fields.Text(
        string='Keterangan',
        required=False,
        track_visibility='onchange')
    tanggal = fields.Date(
        string='Tanggal Report',
        required=False,
        default=lambda self: time.strftime('%Y-%m-%d'),
        track_visibility='onchange')
    start_date = fields.Date(
        string="Periode Awal",
        required=True)
    end_date = fields.Date(
        string="Periode Akhir",
        required=True)
    state_doc = fields.Selection(
        string='State',
        selection=MUTASI_STATES,
        required=True,
        readonly=True,
        default=MUTASI_STATES[0][0],
        track_visibility='onchange')
    mutasi_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=False)
    account_mutasi = fields.Selection(
        [('receivable', 'Receivable'), ('payable', 'Payable')],
        required=True)
    mutasi_ids = fields.Many2many(
        comodel_name='blessing.mutasi.partner.report.line',
        relation='blessing_mutasi_partner_report_line_rel',
        column1='mutasi_id',
        column2='mutasi_line_id',
        string='Mutasi Partner List')
    check_draft_mutasi_partner = fields.Boolean(
        string="Draft Journal",
        default=0)
    check_posted_mutasi_partner = fields.Boolean(
        string="Post Journal",
        default=1)
    check_detail_mutasi = fields.Selection(
        [('detail', 'Kartu AR/AP'), ('rekap', 'Mutasi AR/AP')],
        string="Type Mutasi",
        required=True)
    start_amount    = fields.Float(string="Saldo Awal", store="True", digits=dp.get_precision('Account'))
    db_amount       = fields.Float(string="Total Debet", compute="calc_amount", store="True", digits=dp.get_precision('Account'))
    cr_amount       = fields.Float(string="Total Credit", compute="calc_amount", store="True", digits=dp.get_precision('Account'))
    final_amount    = fields.Float(string="Saldo Akhir", store="True", digits=dp.get_precision('Account'))
    status_customer = fields.Selection([("piutang_lancar","Piutang Lancar"),("piutang_macet","Piutang Macet"),("piutang_grup_perusahaan","Piutang Grup Perusahaan"),("all", "ALL")], string='Status Kelompok pelanggan', default="piutang_lancar")

    @api.model
    def get_pph_and_retur(self, partner_id, id, type):
        print('get_pph_and_retur')
        """
            account_id 11991 = 113003-000-0-0 - Pajak Dibayar Dimuka - Pph 23
        """
        move_obj = self.env['account.move']
        account_obj = self.env['account.account']
        me_obj = self.browse(id)

        if type == 'retur':
            domain = [('partner_id', '=', partner_id),
                    ('move_type', '=', 'out_refund'),
                    ('date', '>=', self.start_date),
                    ('date', '<=', self.end_date),]
            if me_obj.check_draft_mutasi_partner and me_obj.check_posted_mutasi_partner:
                domain.append(('state', 'in', ['draft', 'posted']))
            elif me_obj.check_draft_mutasi_partner:
                domain.append(('state', '=', 'draft'))
            elif me_obj.check_posted_mutasi_partner:
                domain.append(('state', '=', 'posted'))
            amount = move_obj.search(domain).mapped('amount_total_signed')
            return sum(amount)
        elif type == 'pph23':
            account_pph = account_obj.search([('is_coa_pph', '=', True)])
            domain = [('partner_id', '=', partner_id),
                    ('move_type', 'in', ['out_invoice', 'entry']),
                    ('date', '>=', self.start_date),
                    ('date', '<=', self.end_date),]
            if me_obj.check_draft_mutasi_partner and me_obj.check_posted_mutasi_partner:
                domain.append(('state', 'in', ['draft', 'posted']))
            elif me_obj.check_draft_mutasi_partner:
                domain.append(('state', '=', 'draft'))
            elif me_obj.check_posted_mutasi_partner:
                domain.append(('state', '=', 'posted'))
            amount = move_obj.search(domain).line_ids.filtered(lambda x: x.account_id.id in account_pph.ids).mapped('balance')
            return sum(amount)
        elif type == 'penyesuaian':
            print('=========penyesuian========')
            account_penyesuaian = account_obj.search([('is_coa_penyesuaian', '=', True)])
            domain = [('partner_id', '=', partner_id),
                    ('move_type', 'in', ['out_invoice', 'entry']),
                    ('date', '>=', self.start_date),
                    ('date', '<=', self.end_date),
                    ]
            if me_obj.check_draft_mutasi_partner and me_obj.check_posted_mutasi_partner:
                domain.append(('state', 'in', ['draft', 'posted']))
            elif me_obj.check_draft_mutasi_partner:
                domain.append(('state', '=', 'draft'))
            elif me_obj.check_posted_mutasi_partner:
                domain.append(('state', '=', 'posted'))
            amount = move_obj.search(domain).line_ids.filtered(lambda x: x.account_id.id in account_penyesuaian.ids).mapped('balance')
            return sum(amount)


    def calc_amount(self):
        self.calc_start_amount()
        self.calc_end_amount()
        if self.mutasi_ids:
            self.db_amount      = sum(self.mutasi_ids.mapped('debet'))
            self.cr_amount      = sum(self.mutasi_ids.mapped('credit'))

    # @api.depends('start_date', 'account_mutasi')
    def calc_start_amount(self):
        saldo_awal = 0
        opening_ids = []
        filters = [
            ('date', '<', self.start_date),
            ('account_id.internal_type', '=', self.account_mutasi),
            # ('partner_id.status_customer', 'in', self.filter_status_customer()),
        ]

        # if self.check_draft_mutasi_partner  self.check_posted_mutasi_partner:
        if self.check_draft_mutasi_partner and self.check_posted_mutasi_partner:
            filters.append(tuple(('move_id.state', 'in', ('draft', 'posted'))))
        elif self.check_draft_mutasi_partner:
            filters.append(tuple(('move_id.state', '=', 'draft')))
        elif self.check_posted_mutasi_partner:
            filters.append(tuple(('move_id.state', '=', 'posted')))

        if self.check_detail_mutasi == 'detail':
            filters.append(
                tuple(('partner_id', '=', self.mutasi_partner_id.id)))

        opening_ids = self.env['account.move.line'].search(filters)

        for opening_id in opening_ids:
            saldo_awal += opening_id.balance

        if self.account_mutasi == 'payable':
            saldo_awal = -1 * saldo_awal

        if self.check_detail_mutasi == 'detail':
            self.start_amount = saldo_awal
        else:
            self.start_amount   = sum(self.mutasi_ids.mapped('opening'))

    # @api.depends('end_date', 'account_mutasi')
    def calc_end_amount(self):
        saldo_akhir = 0
        closing_ids = []
        filters = [
            ('date', '<=', self.end_date),
            ('account_id.internal_type', '=', self.account_mutasi),
            # ('partner_id.status_customer', 'in', self.filter_status_customer()),
        ]

        # if self.check_draft_mutasi_partner != self.check_posted_mutasi_partner:

        if self.check_draft_mutasi_partner and self.check_posted_mutasi_partner:
            filters.append(tuple(('move_id.state', 'in', ['draft', 'posted'])))
        elif self.check_draft_mutasi_partner:
            filters.append(tuple(('move_id.state', '=', 'draft')))
        elif self.check_posted_mutasi_partner:
            filters.append(tuple(('move_id.state', '=', 'posted')))

        if self.check_detail_mutasi == 'detail':
            filters.append(
                tuple(('partner_id', '=', self.mutasi_partner_id.id)))

        closing_ids = self.env['account.move.line'].search(filters)

        for closing_id in closing_ids:
            saldo_akhir += closing_id.balance

        if self.account_mutasi == 'payable':
            saldo_akhir = -1 * saldo_akhir
        
        if self.check_detail_mutasi == 'detail':
            self.final_amount = saldo_akhir
        else:
            self.final_amount = sum(self.mutasi_ids.mapped('balance'))


    def button_calculate(self):
        self.restart()
        self.calculate_mutasi_partner()
        self.calc_amount()
        return True

    def restart(self):
        self.mutasi_ids.unlink()
        return True

    # Mengambil dan Menghitung Saldo Mutasi Partner
    def calculate_mutasi_partner(self):
        # data['form'] = self.read(['start_date', 'end_date', ... ,dan seterusnya, ...])[0]
        new_mutasi_ids = []
        mutasi_lst = []
        mutasi_ids = None
        filters = []
        # if self.check_draft_mutasi_partner != self.check_posted_mutasi_partner:
        if self.check_draft_mutasi_partner:
            filters.append('draft')
        if self.check_posted_mutasi_partner:
            filters.append('posted')
        # print('this is.append(', filters))

        # if self.check_detail_mutasi == 'detail':
        #     mutasi_ids = self.env['account.move.line'].search([
        #         ('date', '>=', self.start_date),
        #         ('date', '<=', self.end_date),
        #         ('move_id.state', 'in', filters),
        #         ('partner_id', '=', self.mutasi_partner_id.id),
        #         # ('partner_id.status_customer', 'in', self.filter_status_customer()),
        #         ('account_id.internal_type', '=', self.account_mutasi)],
        #         order='date asc')
        #     init_ids = self.env['account.move.line'].search([
        #         ('date', '<=', self.end_date),
        #         ('move_id.state', 'in', filters),
        #         ('partner_id', '=', self.mutasi_partner_id.id),
        #         # ('partner_id.status_customer', 'in', self.filter_status_customer()),
        #         ('account_id.internal_type', '=', self.account_mutasi)],
        #         order='date asc')

        # if self.check_detail_mutasi == 'rekap':
        #     mutasi_ids = self.env['account.move.line'].search([
        #         ('date', '>=', self.start_date),
        #         ('date', '<=', self.end_date),
        #         ('move_id.state', 'in', filters),
        #         # ('partner_id.status_customer', 'in', self.filter_status_customer()),
        #         ('account_id.internal_type', '=', self.account_mutasi)],
        #         order='date asc')
        #     init_ids = self.env['account.move.line'].search([
        #         ('date', '<=', self.end_date),
        #         ('move_id.state', 'in', filters),
        #         # ('partner_id.status_customer', 'in', self.filter_status_customer()),
        #         ('account_id.internal_type', '=', self.account_mutasi)],
        #         order='date asc')
        # else:
        if self.check_detail_mutasi == 'detail':
            mutasi_ids = self.env['account.move.line'].search([
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
                ('partner_id', '=', self.mutasi_partner_id.id),
                # ('partner_id.status_customer', 'in', self.filter_status_customer()),
                ('move_id.state', 'in', filters),
                ('account_id.internal_type', '=', self.account_mutasi)],
                order='date asc')
            init_ids = self.env['account.move.line'].search([
                ('date', '<=', self.end_date),
                ('partner_id', '=', self.mutasi_partner_id.id),
                # ('partner_id.status_customer', 'in', self.filter_status_customer()),
                ('move_id.state', 'in', filters),
                ('account_id.internal_type', '=', self.account_mutasi)],
                order='date asc')
        if self.check_detail_mutasi == 'rekap':
            mutasi_ids = self.env['account.move.line'].search([
                ('date', '<=', self.start_date),
                # ('date', '<=', self.end_date),
                ('move_id.state', 'in', filters),
                ('account_id.internal_type', '=', self.account_mutasi)],
                order='date asc')
            init_ids = self.env['account.move.line'].search([
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
                ('move_id.state', 'in', filters),
                ('account_id.internal_type', '=', self.account_mutasi)],
                order='date asc')

# jika pilihan mutasi rekap AR/AP
        if self.check_detail_mutasi == 'rekap':
            temp_mutasi_ids = []
# membuat kolom penjualan
            for debet_id in mutasi_ids:
                debet_values = {
                    'date': debet_id.date,
                    'name': debet_id.name,
                    'move_id': debet_id.move_id.id,
                    'partner_id': debet_id.partner_id.id,
                    'group_partner_id':debet_id.partner_id.group_partner_id.id,
                    'journal_id': debet_id.journal_id.id,
                    'account_id': debet_id.account_id.id,
                    'debet': debet_id.debit,
                    'credit_bank': 0,
                    'credit_kas': 0,
                    'balance': 0,
                    'state_line': debet_id.move_id.state,
                }
                temp_mutasi_ids.append(debet_values)
#  membuat kolom pembayaran bank
            for bank_id in mutasi_ids:
                bank_values = {
                    'date': bank_id.date,
                    'name': bank_id.name,
                    'move_id': bank_id.move_id.id,
                    'partner_id': bank_id.partner_id.id,
                    'group_partner_id':bank_id.partner_id.group_partner_id.id,
                    'journal_id': bank_id.journal_id.id,
                    'account_id': bank_id.account_id.id,
                    'debet': 0,
                    'credit_bank': 0,
                    'credit_kas': 0,
                    'balance': bank_id.balance,
                    'state_line': bank_id.move_id.state,
                }
                temp_mutasi_ids.append(bank_values)
#  membuat kolom pembayaran kas
            for kas_id in mutasi_ids:
                kas_values = {
                    'date': kas_id.date,
                    'name': kas_id.name,
                    'move_id': kas_id.move_id.id,
                    'partner_id': kas_id.partner_id.id,
                    'group_partner_id':kas_id.partner_id.group_partner_id.id,
                    'journal_id': kas_id.journal_id.id,
                    'account_id': kas_id.account_id.id,
                    'debet': 0,
                    'credit_bank': 0,
                    'credit_kas': kas_id.credit,
                    'balance': 0,
                    'state_line': kas_id.move_id.state,
                }
                temp_mutasi_ids.append(kas_values)
# membuat kolom saldo akhir
            for init_id in init_ids:
                print('====init_id===', init_id.credit)
                init_values = {
                    'date': init_id.date,
                    'name': init_id.name,
                    'move_id': init_id.move_id.id,
                    'partner_id': init_id.partner_id.id,
                    'group_partner_id':init_id.partner_id.group_partner_id.id,
                    'journal_id': init_id.journal_id.id,
                    'account_id': init_id.account_id.id,
                    'debet': 0,
                    'credit_bank': init_id.credit,
                    'credit_kas': 0,
                    'balance': init_id.balance,
                    'state_line': init_id.move_id.state,
                }
                temp_mutasi_ids.append(init_values)
# ada error kalau data kosong di partner_id. belum di perbaiki
            kumulatif = {
                'debet': sum,
                'credit_bank': sum,
                'credit_kas': sum,
                'balance': sum
            }

            if len(mutasi_ids) > 0:
                # mutasi_ids = pd.DataFrame(temp_mutasi_ids).groupby(['partner_id']).agg(kumulatif).reset_index().to_dict('records')
                mutasi_ids = pd.DataFrame(temp_mutasi_ids).groupby(['partner_id','group_partner_id']).agg(kumulatif).reset_index().to_dict('records')
                # print(temp_mutasi_ids)

        i = 0
        kum_balance = 0
        for mutasi_o in mutasi_ids:
            print(mutasi_o)
            i = i+1
            if self.check_detail_mutasi == 'rekap':
                opening = mutasi_o['balance'] + mutasi_o['credit_bank'] - mutasi_o['debet']
                # opening = mutasi_o['credit_bank']
                values = {
                    'urut': i,
                    'partner_id': mutasi_o['partner_id'],
                    'group_partner_id':mutasi_o['group_partner_id'],
                    'opening': opening ,
                    'debet': mutasi_o['debet'],
                    'credit': mutasi_o['credit_bank'],
                    'balance': mutasi_o['balance'],
                }
            else:
                kum_balance = kum_balance + mutasi_o.balance
                opening = kum_balance + mutasi_o.credit - mutasi_o.debit
                values = {
                    'urut': i,
                    'date': mutasi_o.date,
                    'name': mutasi_o.name,
                    'move_id': mutasi_o.move_id.id,
                    'partner_id': mutasi_o.partner_id.id,
                    'group_partner_id':mutasi_o.partner_id.group_partner_id.id,
                    'journal_id': mutasi_o.journal_id.id,
                    'account_id': mutasi_o.account_id.id,
                    'opening': opening,
                    'debet': mutasi_o.debit,
                    'credit': mutasi_o.credit,
                    # 'balance': kum_balance if self.account_mutasi == 'receivable' else -1 * (kum_balance),
                    'balance': kum_balance + self.start_amount if self.account_mutasi == 'receivable' else -1 * (kum_balance - self.start_amount),
                    # 'balance': mutasi_o.balance,
                    'state_line': mutasi_o.move_id.state,
                }

            new_id = self.env['blessing.mutasi.partner.report.line'].create(values)
            new_mutasi_ids.append(new_id)
            mutasi_lst.append(new_id.id)
        self.write({'mutasi_ids': [(6, 0, mutasi_lst)]})
        return new_mutasi_ids

    def get_thead_global(self):
        data_global = []
        if(self.account_mutasi == 'receivable'):
            data_global = self.env['account.journal'].search([
                ('kolom_ar', '!=', 0)
            ], order='kolom_ar asc')
        else:
            data_global = self.env['account.journal'].search([
                ('kolom_ap', '!=', 0)
            ], order='kolom_ap asc')
        return data_global

    def get_thead(self):
        data = []
        if(self.account_mutasi == 'receivable'):
            data = self.env['account.journal'].search([
                ('kolom_ar', '!=', 0)
            ], order='kolom_ar asc')
        else:
            data = self.env['account.journal'].search([
                ('kolom_ap', '!=', 0)
            ], order='kolom_ap asc')
        return data

    def get_by_global(self):
        data_global = []
        filters = []
        # if self.check_draft_mutasi_partner != self.check_posted_mutasi_partner:
        if self.check_draft_mutasi_partner:
            filters.append('draft')
        if self.check_posted_mutasi_partner:
            filters.append('posted')

            data_global = self.env['account.move.line'].search([
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
                ('move_id.state', 'in', filters),
                ('account_id.internal_type', '=', self.account_mutasi),
                ('move_id.move_type', '!=', 'out_refund'),
                # ('partner_id.status_customer', 'in', self.filter_status_customer()),
            ])
        else:
            data_global = self.env['account.move.line'].search([
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
                ('account_id.internal_type', '=', self.account_mutasi),
                ('move_id.move_type', '!=', 'out_refund'),
                # ('partner_id.status_customer', 'in', self.filter_status_customer()),
            ])

        thead_global = self.get_thead_global()
        value_global = dict()
        for row in data_global:
            for journal in thead_global:
                if(str(journal.code) == str(row.journal_id.code)):
                    if(str(journal.code) in value_global):
                        value_global[str(journal.code)] += row.balance
                        # value_global[str(journal.code)] += abs(row.balance) ===> asalnya
                    else:
                        value_global.update({str(journal.code): row.balance})
                        # {str(journal.code): abs(row.balance)}) ===> asalnya
        return value_global

    def get_by_partner(self, partner_id):
        account_pph = self.env['account.account'].search([('is_coa_pph', '=', True)])
        data = []
        data_2 = []
        filters = []
        # if self.check_draft_mutasi_partner != self.check_posted_mutasi_partner:
        if self.check_draft_mutasi_partner:
            filters.append('draft')
        if self.check_posted_mutasi_partner:
            filters.append('posted')
            data = self.env['account.move.line'].search([
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
                ('move_id.state', 'in', filters),
                ('partner_id', '=', partner_id),
                # ('partner_id.status_customer', 'in', self.filter_status_customer()),
                ('account_id.internal_type', '=', self.account_mutasi),
                ('move_id.move_type', '!=', 'out_refund'),
            ])
        else:
            data = self.env['account.move.line'].search([
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
                ('partner_id', '=', partner_id),
                # ('partner_id.status_customer', 'in', self.filter_status_customer()),
                ('account_id.internal_type', '=', self.account_mutasi), 
                ('move_id.move_type', '!=', 'out_refund'),
            ])

        data_2 = self.env['account.move.line'].search([
                ('account_id', 'in', account_pph.ids),
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
                ('move_id.state', 'in', filters),
                ('partner_id', '=', partner_id),
                ('account_id.internal_type', '=', self.account_mutasi), 
                # ('partner_id.status_customer', 'in', self.filter_status_customer()),
            ])

        thead = self.get_thead()
        value = dict()
        for row in data:
            for journal in thead:
                if(str(journal.code) == str(row.journal_id.code)):
                    if(str(journal.code) in value):
                        value[str(journal.code)] += row.balance
                    else:
                        value.update({str(journal.code): row.balance})

        for row in data_2:
            for journal in thead:
                if(str(journal.code) == str(row.journal_id.code)):
                    if(str(journal.code) in value):
                        value[str(journal.code)] += row.balance
                    else:
                        value.update({str(journal.code): row.balance})
        print('============value============', value)
        return value

    # def get_opening_partner(self, partner_id,):
    #     data = []
    #     saldo = 0
    #     if self.check_draft_mutasi_partner != self.check_posted_mutasi_partner:
    #         if self.check_draft_mutasi_partner:
    #             filters = 'draft'
    #         if self.check_posted_mutasi_partner:
    #             filters = 'posted'

    #         data = self.env['account.move.line'].search([
    #             ('date', '<', self.start_date),
    #             ('move_id.state', '=', filters),
    #             ('partner_id', '=', partner_id),
    #             ('partner_id.status_customer', 'in', self.filter_status_customer()),
    #             ('account_id.internal_type', '=', self.account_mutasi)
    #         ])
    #     else:
    #         data = self.env['account.move.line'].search([
    #             ('date', '<', self.start_date),
    #             ('partner_id', '=', partner_id),
    #             ('partner_id.status_customer', 'in', self.filter_status_customer()),
    #             ('account_id.internal_type', '=', self.account_mutasi)
    #         ])

    #     for row in data:
    #         saldo += row.balance

    #     return saldo

    def filter_status_customer(self):
        if self.status_customer == 'all':
            return ['piutang_lancar', 'piutang_macet', 'piutang_grup_perusahaan']
        else:
            return [self.status_customer]

    @api.constrains('end_date', 'start_date')
    def check_date(self):
        if self.start_date > self.end_date:
            raise UserError( _('Error!:: Tanggal Akhir lebih kecil dari Tanggal Awal.'))
            # raise exceptions.Warning(
            #     _('Error!:: Tanggal Akhir lebih kecil dari Tanggal Awal.'))

    @api.constrains('check_draft_mutasi_partner', 'check_posted_mutasi_partner')
    def check_filter(self):
        if not self.check_draft_mutasi_partner and not self.check_posted_mutasi_partner:
            raise UserError(_('Error!:: Harap di Cheklist Filter Data.'))
            
            # raise exceptions.Warning(
            #     _('Error!:: Harap di Cheklist Filter Data.'))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code(
                'blessing.mutasi.partner.report') or _('New')
            vals['name'] = seq
            result = super(BlessingMutasiPartnerReport, self).create(vals)
            return result

    def action_draft(self):
        self.state_doc = MUTASI_STATES[0][0]

    def action_confirm(self):
        self.state_doc = MUTASI_STATES[1][0]

    def action_cancel(self):
        self.state_doc = MUTASI_STATES[3][0]

    def action_done(self):
        self.state_doc = MUTASI_STATES[2][0]
