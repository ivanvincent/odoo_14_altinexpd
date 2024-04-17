from odoo import api, fields, models, _
import time
from itertools import groupby
from datetime import datetime, timedelta

from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

import odoo.addons.decimal_precision as dp
import pandas as pd

MUTASI_STATES =[('draft','Draft'), ('confirm','Confirm'), ('done','Done'), ('cancel','Cancel'),]

class BlessingMutasiPartnerReportLine(models.Model):
    _name = 'blessing.mutasi.partner.report.line'
    _description = 'Blessing Mutasi Partner Report Line'
    # _order = 'id desc'

    urut           = fields.Integer(string="Urut")
    date           = fields.Date(string='Tanggal')
    name           = fields.Char(string="Keterangan")
    move_id   = fields.Many2one(
        comodel_name='account.move', 
        string='No Journal')
    partner_id     = fields.Many2one(
        comodel_name='res.partner', 
        string='Partner')
    account_id     = fields.Many2one(
        comodel_name='account.account', 
        string='Account')
    journal_id     = fields.Many2one(
        comodel_name='account.journal', 
        string='Journal')
    debet          = fields.Float(string="Debet", digits=dp.get_precision('Account'))
    credit         = fields.Float(string="Credit", digits=dp.get_precision('Account'))
    balance        = fields.Float(string="Jumlah", digits=dp.get_precision('Account'))
    state_line     = fields.Selection([('open', 'Draft'), ('confirm', 'Post')], string="Status Journal")

class BlessingMutasiPartnerReport(models.Model):
    _name = 'blessing.mutasi.partner.report'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
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
        default=1)
    check_posted_mutasi_partner = fields.Boolean(
        string="Post Journal", 
        default=1)
    check_detail_mutasi = fields.Selection(
        [('detail', 'Kartu AR/AP'), ('rekap', 'Mutasi AR/AP')], 
        required=True)
    start_amount = fields.Float(string="Saldo Awal",
                                compute="calc_start_amount",
                                store="True",
                                digits=dp.get_precision('Account'))
    final_amount = fields.Float(string="Saldo Akhir",
                                compute="calc_end_amount",
                                store="True",
                                digits=dp.get_precision('Account'))

    @api.depends('start_date','account_mutasi','mutasi_partner_id')
    def calc_start_amount(self):
        saldo_awal = 0
        opening_ids = []
        if self.check_detail_mutasi == 'detail':
            opening_ids = self.env['account.move.line'].search([
                ('date','<',self.start_date), 
                ('partner_id','=',self.mutasi_partner_id.id), 
                ('account_id.internal_type','=',self.account_mutasi)])
        if self.check_detail_mutasi == 'rekap':
            opening_ids = self.env['account.move.line'].search([
                ('date','<',self.start_date), 
                ('account_id.internal_type','=',self.account_mutasi)])
        
        for opening_id in opening_ids:
            saldo_awal += opening_id.balance
        self.start_amount = saldo_awal

    @api.depends('end_date','account_mutasi','mutasi_partner_id')
    def calc_end_amount(self):
        saldo_akhir = 0
        closing_ids = []
        if self.check_detail_mutasi == 'detail':
            closing_ids = self.env['account.move.line'].search([
                ('date','<=',self.end_date), 
                ('partner_id.id','=',self.mutasi_partner_id.id), 
                ('account_id.internal_type','=',self.account_mutasi)])
        if self.check_detail_mutasi == 'rekap':
            closing_ids = self.env['account.move.line'].search([
                ('date','<=',self.end_date), 
                ('account_id.internal_type','=',self.account_mutasi)])
        for closing_id in closing_ids:
            saldo_akhir += closing_id.balance
        self.final_amount = saldo_akhir

    @api.multi
    def button_calculate(self):
        self.restart()
        self.calculate_mutasi_partner()
        return True

    @api.one
    def restart(self):
        self.mutasi_ids.unlink()
        return True

    # Mengambil dan Menghitung Saldo Mutasi Partner
    @api.one
    def calculate_mutasi_partner(self):
        # data['form'] = self.read(['start_date', 'end_date', ... ,dan seterusnya, ...])[0]
        new_mutasi_ids = []
        mutasi_lst = []
        mutasi_ids = None
        filters = ''
        if self.check_draft_mutasi_partner != self.check_posted_mutasi_partner:
            if self.check_draft_mutasi_partner:
                filters = '= draft'
            if self.check_posted_mutasi_partner:
                filters = '= posted'

            if self.check_detail_mutasi == 'detail':
                mutasi_ids = self.env['account.move.line'].search([
                    ('date','>=',self.start_date), 
                    ('date','<=',self.end_date), 
                    ('move_id.state', filters), 
                    ('partner_id.id','=',self.mutasi_partner_id.id), 
                    ('account_id.internal_type','=',self.account_mutasi)],
                    order='date asc')
            if self.check_detail_mutasi == 'rekap':
                mutasi_ids = self.env['account.move.line'].search([
                    ('date','>=',self.start_date), 
                    ('date','<=',self.end_date), 
                    ('move_id.state', filters), 
                    ('account_id.internal_type','=',self.account_mutasi)],
                    order='date asc')
                # new_mutasi_ids=pd.DataFrame(mutasi_ids).groupby('partner_id')['balance'].sum().to_frame().reset_index()
        else:
            if self.check_detail_mutasi == 'detail':
                mutasi_ids = self.env['account.move.line'].search([
                    ('date','>=',self.start_date), 
                    ('date','<=',self.end_date), 
                    ('partner_id.id','=',self.mutasi_partner_id.id), 
                    ('account_id.internal_type','=',self.account_mutasi)],
                    order='date asc')
            if self.check_detail_mutasi == 'rekap':
                mutasi_ids = self.env['account.move.line'].search([
                    ('date','>=',self.start_date), 
                    ('date','<=',self.end_date), 
                    ('account_id.internal_type','=',self.account_mutasi)],
                    order='date asc')
                # new_mutasi_ids=pd.DataFrame(mutasi_ids).groupby('partner_id')['balance'].sum().to_frame().reset_index()
        
        if self.check_detail_mutasi == 'rekap':
            temp_mutasi_ids = []
            for mutasi in mutasi_ids:
                values = {
                    'date'          : mutasi.date,
                    'name'          : mutasi.name,
                    'move_id'       : mutasi.move_id.id,
                    'partner_id'    : mutasi.partner_id.id,
                    'journal_id'    : mutasi.journal_id.id,
                    'account_id'    : mutasi.account_id.id,
                    'balance'       : mutasi.balance,
                    'state_line'    : mutasi.move_id.state,
                }
                temp_mutasi_ids.append(values)
            # raise Exception(temp_mutasi_ids)
            mutasi_ids = pd.DataFrame(temp_mutasi_ids).groupby(['partner_id','journal_id'])['balance'].sum().to_frame().reset_index().to_dict('records')

        i=0
        kum_balance=0
        for mutasi_o in mutasi_ids:
            # raise Exception(mutasi_o)
            i=i+1
            if self.check_detail_mutasi == 'rekap':
                kum_balance = kum_balance + mutasi_o['balance']
                values = {
                        'urut'          : i,
                        'partner_id'    : mutasi_o['partner_id'],
                        'journal_id'    : mutasi_o['journal_id'],
                        'debet'         : mutasi_o['balance'] if mutasi_o['balance']>0 else 0,
                        'credit'        : mutasi_o['balance'] if mutasi_o['balance']<0 else 0,
                        'balance'       : kum_balance + self.start_amount,
                    }
            else:
                kum_balance = kum_balance + mutasi_o.balance
                values = {
                        'urut'          : i,
                        'date'          : mutasi_o.date,
                        'name'          : mutasi_o.name,
                        'move_id'       : mutasi_o.move_id.id,
                        'partner_id'    : mutasi_o.partner_id.id,
                        'journal_id'    : mutasi_o.journal_id.id,
                        'account_id'    : mutasi_o.account_id.id,
                        'debet'         : mutasi_o.balance if mutasi_o.balance>0 else 0,
                        'credit'        : mutasi_o.balance if mutasi_o.balance<0 else 0,
                        'balance'       : kum_balance + self.start_amount,
                        'state_line'    : 'confirm' if mutasi_o.move_id.state else 'open',
                    }

            new_id = self.env['blessing.mutasi.partner.report.line'].create(values)
            new_mutasi_ids.append(new_id)
            mutasi_lst.append(new_id.id)
        self.write({'mutasi_ids': [(6, 0, mutasi_lst)]})
        return new_mutasi_ids

    @api.one
    @api.constrains('end_date', 'start_date')
    def check_date(self):
        if self.start_date > self.end_date:
            raise exceptions.Warning(
                _('Error!:: Tanggal Akhir lebih kecil dari Tanggal Awal.'))

    @api.one
    @api.constrains('check_draft_mutasi_partner','check_posted_mutasi_partner')
    def check_filter(self):
        if not self.check_draft_mutasi_partner and not self.check_posted_mutasi_partner:
            raise exceptions.Warning(
                _('Error!:: Harap di Cheklist Filter Data.'))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('blessing.mutasi.partner.report') or _('New')
            vals['name'] = seq
            result = super(BlessingMutasiPartnerReport, self).create(vals)
            return result

    @api.multi
    def action_draft(self):
        self.state_doc = MUTASI_STATES[0][0]

    @api.multi
    def action_confirm(self):
        self.state_doc = MUTASI_STATES[1][0]

    @api.multi
    def action_cancel(self):
        self.state_doc = MUTASI_STATES[3][0]

    @api.multi
    def action_done(self):
        self.state_doc = MUTASI_STATES[2][0]

    # @api.onchange('')
    # def _sql_init_balance(self):
    # def _sql_lines(self):