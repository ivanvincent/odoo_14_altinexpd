from odoo import api, fields, models, _
import time
from itertools import groupby
from datetime import datetime, timedelta


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

class RvPayroll(models.Model):
    _name = 'rv.payroll'
    
    
    name = fields.Char(string='No Voucher', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    description = fields.Text(string="Description", required=False, track_visibility='onchange',)
    tanggal = fields.Date(string="Tanggal", required=False, default=lambda self: time.strftime("%Y-%m-%d"),
                          track_visibility='onchange',)
    state = fields.Selection(string="State", selection=KB_STATES, required=True, readonly=True, default=KB_STATES[0][0], track_visibility='onchange',)
    amount = fields.Float(string='Amount', store=False)
    # amount = fields.Float(compute='_cek_total_amount',string='Amount', store=False)

    # inv_ids = fields.Many2many('account.move', 'kontrabon_order_line', 'kb_id', 'inv_id', "Invoice List")
    rvp_line_ids = fields.One2many(
        comodel_name='rv.payroll.line', 
        inverse_name="rv_id",
        string="Rvp Line",
        required=False,)
    rvp_account_ids = fields.One2many(
        comodel_name='rv.payroll.line.account', 
        inverse_name="rv_id",
        string="Account Line",
        required=False,)
    
class RvPayrollLine(models.Model):
    _name = 'rv.payroll.line'
    
    name = fields.Char(string='No Voucher', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    description = fields.Text(string="Description", required=False, track_visibility='onchange',)
    rv_id = fields.Many2one('rv.payroll')
    state = fields.Selection(string="State", selection=KB_STATES, required=True, readonly=True, default=KB_STATES[0][0], track_visibility='onchange',)
    amount = fields.Float(string='Amount')
    
    nik_id = fields.Char(string="NIK")
    karyawan = fields.Char(string="Name")
    total_gapok = fields.Float(string='Gaji pokok')
    bpjs_kesehatan = fields.Float(string='Gaji Pokok BPJS Kes')
    bpjs_tk = fields.Float(string='Gaji Pokok BPJS TK')
    total_ahli = fields.Float(string='Tunjangan Keahlian')
    total_shift3 = fields.Float(string='Tunjangan Shift 3')
    total_faskes = fields.Float(string='Tunjangan Kes Non BPJS')
    total_lembur = fields.Float(string='Bonus Proyek')
    total_bonus = fields.Float(string='Bonus Bulanan')
    total_tunjangan = fields.Float(string='Total Tjg selain Tjg PPh')
    total_tpph = fields.Float(string='Tunjangan PPh 21')
    total_kes = fields.Float(string='BPJS Kes (Perusahaan)')
    total_jkk = fields.Float(string='BPJS JKK (Perusahaan)')
    total_jkm = fields.Float(string='BPJS JKM (Perusahaan)')
    total_bota = fields.Float(string='Bonus Tahunan')
    total_thr = fields.Float(string='THR')
    total_ktt = fields.Float(string='Total Komponen Tidak Tetap')
    total_bruto = fields.Float(string='Penghasilan Bruto')
    total_jht2 = fields.Float(string='BPJS JHT (Karyawan)')
    total_jp2 = fields.Float(string='BPJS JP (Karyawan)')
    total_jabat = fields.Float(string='Biaya Jabatan')
    total_potong = fields.Float(string='Potongan Resmi lainnya')
    total_net = fields.Float(string='Penghasilan Netto')
    total_net_annual = fields.Float(string='Penghasilan Netto disetahunkan')
    total_ptkp = fields.Float(string='PTKP')
    total_pkp_1 = fields.Float(string='PKP')
    pkp_pembulatan = fields.Float(string='PKP Pembulatan')
    total_pph21_1 = fields.Float(string='PPh 21 Terutang')
    total_pph21_2 = fields.Float(string='PPh 21 Dicicil')
    total_thp = fields.Float(string=' ')
    total_jp = fields.Float(string='BPJS JP (Perusahaan)')
    jht = fields.Float(string='BPJS JHT (Perusahaan)')
    total_bpjs_perusahaan = fields.Float(string='Total BPJS bayar Perusahaan')
    kes2 = fields.Float(string='BPJS Kes (Karyawan)')
    total_pkp_2 = fields.Float(string='Total BPJS bayar Karyawan')
    total_thp = fields.Float(string='THP')
    tot_pph21_perusahaan = fields.Float(string='Total BPJS untuk PPh21')
    tot_pph21_karyawan = fields.Float(string='Total pot BPJS u/ PPh21')
    
    # inv_ids = fields.Many2many('account.move', 'kontrabon_order_line', 'kb_id', 'inv_id', "Invoice List")
    # rvp_line_ids = fields.One2many(
    #     comodel_name='rv.payroll.line', 
    #     inverse_name="rv_id",
    #     string="Rvp Line",
    #     required=False,)   


class RvPayrollAccount(models.Model):
    _name = 'rv.payroll.account'
    
    
    name = fields.Char(string='No Voucher', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    description = fields.Text(string="Description", required=False, track_visibility='onchange',)
    
    journal_id = fields.Many2one('account.journal', 'Journal')
    total_gapok_account_id = fields.Many2one('account.account', 'Gaji pokok')
    bpjs_kesehatan_account_id = fields.Many2one('account.account',string='Gaji Pokok BPJS Kes')
    bpjs_tk_account_id = fields.Many2one('account.account',string='Gaji Pokok BPJS TK')
    total_ahli_account_id = fields.Many2one('account.account',string='Tunjangan Keahlian')
    total_shift3_account_id = fields.Many2one('account.account',string='Tunjangan Shift 3')
    total_faskes_account_id = fields.Many2one('account.account',string='Tunjangan Kes Non BPJS')
    total_lembur_account_id = fields.Many2one('account.account',string='Bonus Proyek')
    total_bonus_account_id = fields.Many2one('account.account',string='Bonus Bulanan')
    total_tunjangan_account_id = fields.Many2one('account.account',string='Total Tjg selain Tjg PPh')
    total_tpph_account_id = fields.Many2one('account.account',string='Tunjangan PPh 21')
    total_kes_account_id = fields.Many2one('account.account',string='BPJS Kes (Perusahaan)')
    total_jkk_account_id = fields.Many2one('account.account',string='BPJS JKK (Perusahaan)')
    total_jkm_account_id = fields.Many2one('account.account',string='BPJS JKM (Perusahaan)')
    total_bota_account_id = fields.Many2one('account.account',string='Bonus Tahunan')
    total_thr_account_id = fields.Many2one('account.account',string='THR')
    total_ktt_account_id = fields.Many2one('account.account',string='Total Komponen Tidak Tetap')
    total_bruto_account_id = fields.Many2one('account.account',string='Penghasilan Bruto')
    total_jht2_account_id = fields.Many2one('account.account',string='BPJS JHT (Karyawan)')
    total_jp2_account_id = fields.Many2one('account.account',string='BPJS JP (Karyawan)')
    total_jabat_account_id = fields.Many2one('account.account',string='Biaya Jabatan')
    total_potong_account_id = fields.Many2one('account.account',string='Potongan Resmi lainnya')
    total_net_account_id = fields.Many2one('account.account',string='Penghasilan Netto')
    total_net_annual_account_id = fields.Many2one('account.account',string='Penghasilan Netto disetahunkan')
    total_ptkp_account_id = fields.Many2one('account.account',string='PTKP')
    total_pkp_1_account_id = fields.Many2one('account.account',string='PKP')
    pkp_pembulatan_account_id = fields.Many2one('account.account',string='PKP Pembulatan')
    total_pph21_1_account_id = fields.Many2one('account.account',string='PPh 21 Terutang')
    total_pph21_2_account_id = fields.Many2one('account.account',string='PPh 21 Dicicil')
    total_thp_account_id = fields.Many2one('account.account',string=' ')
    total_jp_account_id = fields.Many2one('account.account',string='BPJS JP (Perusahaan)')
    jht_account_id = fields.Many2one('account.account',string='BPJS JHT (Perusahaan)')
    total_bpjs_perusahaan_account_id = fields.Many2one('account.account',string='Total BPJS bayar Perusahaan')
    kes2_account_id = fields.Many2one('account.account',string='BPJS Kes (Karyawan)')
    total_pkp_2_account_id = fields.Many2one('account.account',string='Total BPJS bayar Karyawan')
    total_thp_account_id = fields.Many2one('account.account',string='THP')
    tot_pph21_perusahaan_account_id = fields.Many2one('account.account',string='Total BPJS untuk PPh21')
    tot_pph21_karyawan_account_id = fields.Many2one('account.account',string='Total pot BPJS u/ PPh21')
    
    
class RvPayrollLineAccount(models.Model):
    _name = 'rv.payroll.line.account'
    
    
    rv_id = fields.Many2one('rv.payroll')
    state = fields.Selection(string="State", selection=KB_STATES, required=True, readonly=True, default=KB_STATES[0][0], track_visibility='onchange',)
    account_id = fields.Many2one('account.account', 'Account')
    description = fields.Text(string="Description", required=False, track_visibility='onchange',)
    amount_debit = fields.Float(string='Debit', compute="compute_amount")
    amount_credit = fields.Float(string='Credit')

    def compute_amount(self):
        print("======compute_amount======")
        query = """ select * from rv_payroll_account where id = 1; """
        self._cr.execute(query)
        results = self._cr.dictfetchall()
        print("=======Result=======")
        print(results)
        for rec in self:
            rec.amount_debit = 99