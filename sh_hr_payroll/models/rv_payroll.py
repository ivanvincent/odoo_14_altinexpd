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
    
class RvPayrollLine(models.Model):
    _name = 'rv.payroll.line'
    
    
    name = fields.Char(string='No Voucher', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    description = fields.Text(string="Description", required=False, track_visibility='onchange',)
    rv_id = fields.Many2one('rv.payroll')
    state = fields.Selection(string="State", selection=KB_STATES, required=True, readonly=True, default=KB_STATES[0][0], track_visibility='onchange',)
    amount = fields.Float(string='Amount', store=False)
    
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