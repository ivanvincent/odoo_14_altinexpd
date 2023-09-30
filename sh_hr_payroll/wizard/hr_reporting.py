# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
import logging
logger = logging.getLogger(__name__)
from io import BytesIO
import base64
import xlsxwriter
from datetime import datetime
from . import add_workbook_format as awf


_STATE =[("bpjs", "Laporan Gaji pada BPJS"),
         ("gs", "Laporan Gaji pada GS"),
]

class HrReporting(models.TransientModel):
    _name = 'hr.reporting.wizard'
    _description = 'Generate payslips for all selected employees'

    current_year = datetime.now().year
    date_start = fields.Date(string="Start date", required=False)
    date_end = fields.Date(string="End date", required=False)
    report_type     = fields.Selection(selection=_STATE, string='Report Type',default="bpjs")
    month_selection = fields.Selection([
                        ("01","Januari %s" % current_year),   
                        ("02","Februari %s" % current_year),
                        ("03","Maret %s" % current_year),
                        ("04","April %s" % current_year),
                        ("05","Mei %s" % current_year),
                        ("06","Juni %s" % current_year),
                        ("07","Juli %s" % current_year),
                        ("08","Agustus %s" % current_year),
                        ("09","September %s" % current_year),
                        ("10","Oktober %s" % current_year),
                        ("11","November %s" % current_year),
                        ("12","Desember %s" % current_year),
                        ],string='Month Selection')
    job_ids = fields.Many2many('hr.job', string='Access Job', compute='compute_job_ids', compute_sudo=True)
    data = fields.Binary(string='Data')

    def query(self):
        job_ids = str(tuple(self.job_ids.ids)).replace(',)',')')
        if not self.job_ids:
            raise UserError('Mohon maaf anda tidak memiliki akses ..')
        query =f"""
                SELECT 
                he.name, 
				he.identification_id as nik,
				hc.gapok_bpjs_kes as bpjs_kesehatan,
				hc.gapok_bpjs_tk as bpjs_tk,
                sum(payslip.total_gapok) as total_gapok,
                sum(payslip.total_gapok_bpjs) as total_gapok_bpjs,
                sum(payslip.total_ahli) as total_ahli,
                sum(payslip.total_shift3) as total_shift3,
                sum(payslip.total_faskes) as total_faskes,
                sum(payslip.total_lembur) as total_lembur,
                sum(payslip.total_bonus) as total_bonus,
                sum(payslip.total_total_tunjangan) as total_tunjangan,
                sum(payslip.total_tpph) as total_tpph,
                sum(payslip.total_kes) as total_kes,
                sum(payslip.total_jkk) as total_jkk,
                sum(payslip.total_jkm) as total_jkm,
                sum(payslip.total_bota) as total_bota,
                sum(payslip.total_thr) as total_thr,
                sum(payslip.total_total_ktt) as total_ktt,
                sum(payslip.total_bruto) as total_bruto,
                sum(payslip.total_jht2) as total_jht2,
                sum(payslip.total_jp2) as total_jp2,
                sum(payslip.total_jabat) as total_jabat,
                sum(payslip.total_potong) as total_potong,
                sum(payslip.total_net) as total_net,
                sum(payslip.total_net_annual) as total_net_annual,
                sum(payslip.total_ptkp) as total_ptkp,
                sum(payslip.total_pkp_1) as total_pkp_1,
				floor (sum(payslip.total_pkp_1) / 1000) * 1000 as pkp_pembulatan,
                sum(payslip.total_pkp_2) as total_pkp_2,
                sum(payslip.total_pph21_1) as total_pph21_1,
                sum(payslip.total_pph21_2) as total_pph21_2,
                sum(payslip.total_thp_1) as total_thp,
                sum(payslip.jht) as jht,
                sum(payslip.total_jp) as total_jp,
                sum(payslip.kes2) as kes2,
				sum(payslip.gaji_bpjs_kes) as total_bpjs_kes,
                sum(payslip.gaji_bpjs_tk) as total_bpjs_tk,
				sum(payslip.thp_2) as thp_2,
				sum(payslip.thp_3) as thp_3,
				sum(payslip.total_bpjs_perusahaan) as total_bpjs_perusahaan
            FROM (
                    SELECT 
						hpl.code, 
						hpl.total as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id
                    FROM
                hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
				left join hr_employee he on he.id = hp.employee_id
				left join hr_job hj on hj.id = he.job_id
				left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'GAPOK'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}

                    UNION
                    SELECT 
						hpl.code, 
						0 as total_gapok, 
						hpl.total as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'GAPOK_BPJS_KES'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
					UNION
                    SELECT 
						hpl.code, 
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						hpl.total as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'AHLI'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						hpl.total as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'SHIFT3'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
					
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						hpl.total as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'FASKES'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						hpl.total as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'LEMBUR'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						hpl.total as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'BONUS'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}

					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						hpl.total as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'TOTAL_TUNJANGAN'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						hpl.total as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'TPPH'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
					
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						hpl.total as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'KES'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						hpl.total as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'JKK'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						hpl.total as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'JKM'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						hpl.total as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'BOTA'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						hpl.total as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'THR'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
					
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						hpl.total as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'TOTAL_KTT'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						hpl.total as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'BRUTO'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						hpl.total as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'JHT2'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}

				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						hpl.total as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'JP2'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						hpl.total as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'JABAT'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						hpl.total as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'POTONG'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						hpl.total as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'NET'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						hpl.total as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'NET_ANNUAL'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						hpl.total as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'PTKP'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						hpl.total as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'PKP_1'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						hpl.total as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'TOTAL_BPJS_KARYAWAN'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						hpl.total as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'PPH21_1_SETAHUN'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}

				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						hpl.total as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'PPH21_1_SEBULAN'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						hpl.total as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'THP_1'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						hpl.total as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'JHT'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						hpl.total as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'JP'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						hpl.total as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'KES2'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						hc.gapok_bpjs_kes as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						hc.gapok_bpjs_tk as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on  hc.id = he.contract_id
                    WHERE hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
					
				UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						hpl.total as thp_2,
						0 as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'THP_2'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
				
					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						hpl.total as thp_3,
						0 as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'THP_3'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}

					UNION
                    SELECT 
						hpl.code,
						0 as total_gapok, 
						0 as total_gapok_bpjs,
						0 as total_ahli,
						0 as total_shift3,
						0 as total_faskes,
						0 as total_lembur,
						0 as total_bonus,
						0 as total_total_tunjangan,
						0 as total_tpph, 
						0 as total_kes,
						0 as total_jkk,
						0 as total_jkm,
						0 as total_bota,
						0 as total_thr,
						0 as total_total_ktt,
						0 as total_bruto,
						0 as total_jht2, 
						0 as total_jp2,
						0 as total_jabat,
						0 as total_potong,
						0 as total_net,
						0 as total_net_annual,
						0 as total_ptkp,
						0 as total_pkp_1,
						0 as total_pkp_2, 
						0 as total_pph21_1,
						0 as total_pph21_2,
						0 as total_thp_1,
						0 as jht,
						0 as total_jp,
						0 as kes2,
						0 as gaji_bpjs_kes,
						0 as gaji_bpjs_tk,
						0 as thp_2,
						0 as thp_3,
						hpl.total as total_bpjs_perusahaan,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
					left join hr_contract hc on hc.id = he.contract_id
                    WHERE hpl.code = 'TOTAL_BPJS_PERUSAHAAN'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
                ) AS payslip 
            left join hr_employee he on he.id = payslip.employee_id
			left join hr_job hj on hj.id = he.job_id
			left join hr_contract hc on  hc.id = he.contract_id
            GROUP BY he.name, he.identification_id, hc.gapok_bpjs_kes, hc.gapok_bpjs_tk
            """ 
        self._cr.execute(query)
        return self._cr.dictfetchall()
    
    def action_form_voucher_payroll(self):
        print('action_form_voucher_payroll')
        rslt = self.query()
        uid = self.env.user.id
        # for rec in rslt:
        #     rec.l
        # lines = [(0,0,{
        #     # "date":self.date,
        #     "name":'-',
        #     # "amount":self.nominal*-1,
        #     # "account_id":1616
            
        #     })]
        lines = []
        for lot in rslt:
            lines.append((0, 0, {
                    "nik_id": lot.get('nik', ''),
                    "karyawan": lot.get('name', ''),
                    "total_gapok": lot.get('total_gapok', ''),
                    "bpjs_kesehatan": lot.get('total_gapok_bpjs', ''),
                    "bpjs_tk": lot.get('bpjs_tk', ''),
                    "total_ahli": lot.get('total_ahli', ''),
                    "total_shift3": lot.get('total_shift3', ''),
                    "total_faskes": lot.get('total_faskes', ''),
                    "total_lembur": lot.get('total_lembur', ''),
                    "total_bonus": lot.get('total_bonus', ''),
                    "total_tunjangan": lot.get('total_tunjangan', ''),
                    "total_tpph": lot.get('total_tpph', ''),
                    "total_kes": lot.get('total_kes', ''),
                    "jht": lot.get('jht', ''),
                    "total_jkk": lot.get('total_jkk', ''),
                    "total_jp": lot.get('total_jp', ''),
                    "total_jkm": lot.get('total_jkm', ''),
                    "total_bpjs_perusahaan": lot.get('total_bpjs_perusahaan', ''),
                    "tot_pph21_perusahaan": lot.get('tot_pph21_perusahaan', ''),
                    "total_bota": lot.get('total_bota', ''),
                    "total_thr": lot.get('total_thr', ''),
                    "total_ktt": lot.get('total_ktt', ''),
                    "total_bruto": lot.get('total_bruto', ''),
                    "kes2": lot.get('kes2', ''),
                    "total_jht2": lot.get('total_jht2', ''),
                    "total_jp2": lot.get('total_jp2', ''),
                    "total_pkp_2": lot.get('total_pkp_2', ''),
                    "tot_pph21_karyawan": lot.get('tot_pph21_karyawan', ''),
                    "total_jabat": lot.get('total_jabat', ''),
                    "total_potong": lot.get('total_potong', ''),
                    "total_net": lot.get('total_net', ''),
                    "total_net_annual": lot.get('total_net_annual', ''),
                    "total_ptkp": lot.get('total_ptkp', ''),
                    "total_pkp_1": lot.get('total_pkp_1', '')  ,
                    "pkp_pembulatan": lot.get('pkp_pembulatan', '') if lot.get('pkp_pembulatan', '') > 0 else 0,
                    "total_pph21_1": lot.get('total_pph21_1', ''),
                    "total_pph21_2": lot.get('total_pph21_2', ''),
                    # "total_thp": lot.get('total_gapok', '') + lot.get('total_tpph', ''),
                    "total_thp": lot.get('tot_thp', ''),
                }))

        # bs = self.env['rv.payroll'].search([('journal_id', '=', self.journal_src_id.id)], order="id desc", limit=1)

        abs = self.env['rv.payroll'].sudo().create({
            # "balance_start": bs.balance_end_real,
            # "request_kasbon_id": self.id,
            # "journal_id": self.journal_src_id.id,
            "tanggal":self.date_end,
            "name":self.month_selection,
            "rvp_line_ids":lines,
            "create_uid": uid
            })

        # abs.write({
        #     "balance_end_real": abs.balance_end
        # })
	
    def action_generate_pdf(self):
        record = self.query()
        data = {
			'me': self,
			'ids': self.ids,
			'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'month_selection': self.month_selection,
                'record' : record,
            },
        }
        if self.report_type == 'bpjs': 
            return self.env.ref('sh_hr_payroll.action_report_salary_bpjs').report_action(None, data=data)
        else:
            return self.env.ref('sh_hr_payroll.action_report_salary_gs').report_action(None, data=data)

    @api.depends('report_type')
    def compute_job_ids(self):
        manajer_payroll = self.env['res.groups'].sudo().browse(240)
        payroll_staff = self.env['res.groups'].sudo().browse(241)
        payroll_spv = self.env['res.groups'].sudo().browse(244)
        uid = self.env.user.id
        if uid in manajer_payroll.users.ids:
            rule = manajer_payroll.rule_groups.filtered(lambda x: x.model_id.name == 'Pay Slip')
        elif uid in payroll_staff.users.ids:
            rule = payroll_staff.rule_groups.filtered(lambda x: x.model_id.name == 'Pay Slip')
        elif uid in payroll_spv.users.ids:
            rule = payroll_spv.rule_groups.filtered(lambda x: x.model_id.name == 'Pay Slip')
        else:
            self.job_ids = [(6, 0, [])]
            return
        job_ids = rule.domain_force.split(",'in',")[1].replace(")])", "")
        for rec in self:
            rec.job_ids = [(6, 0, list(map(int, job_ids[1:-1].split(','))) if job_ids else [])]

    def action_generate_excel(self):
        print("action_generate_excel")
        rslt = self.query()
        fp = BytesIO()
        date_string = datetime.now().strftime("%Y-%m-%d")
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = awf.add_workbook_format(workbook)

            # # WKS 1
        report_name = 'LAPORAN GAJI KE GITA SARANA'
        worksheet = workbook.add_worksheet(report_name)        
            
        worksheet.set_column('A2:A2', 10)
        worksheet.set_column('B2:B2', 35)
        worksheet.set_column('C2:C2', 35)
        worksheet.set_column('D2:D2', 20)
        worksheet.set_column('E2:E2', 20)
        worksheet.set_column('F2:F2', 20)
        worksheet.set_column('G2:G2', 20)
        worksheet.set_column('H2:H2', 20)
        worksheet.set_column('I2:I2', 20)
        worksheet.set_column('J2:J2', 20)
        worksheet.set_column('K2:K2', 20)
        worksheet.set_column('L2:L2', 20)
        worksheet.set_column('M2:M2', 20)
        worksheet.set_column('N2:N2', 20)
        worksheet.set_column('O2:O2', 20)
        worksheet.set_column('P2:P2', 20)
        worksheet.set_column('Q2:Q2', 20)
        worksheet.set_column('R2:R2', 20)
        worksheet.set_column('S2:S2', 20)
        worksheet.set_column('T2:T2', 20)
        worksheet.set_column('U2:U2', 20)
        worksheet.set_column('V2:V2', 20)
        worksheet.set_column('W2:W2', 20)
        worksheet.set_column('X2:X2', 20)
        worksheet.set_column('Y2:Y2', 20)
        worksheet.set_column('Z2:Z2', 20)
        worksheet.set_column('AA2:AA2', 20)
        worksheet.set_column('AB2:AB2', 20)
        worksheet.set_column('AC2:AC2', 20)
        worksheet.set_column('AD2:AD2', 20)
        worksheet.set_column('AE2:AE2', 20)
        worksheet.set_column('AF2:AF2', 20)
        worksheet.set_column('AG2:AG2', 20)
        worksheet.set_column('AH2:AH2', 20)
        worksheet.set_column('AI2:AI2', 20)
        worksheet.set_column('AJ2:AJ2', 20)
        worksheet.set_column('AK2:AK2', 20)
        worksheet.set_column('AL2:AL2', 20)
        worksheet.set_column('AM2:AM2', 20)
        worksheet.set_column('AN2:AN2', 20)
    

            # # WKS 1

        worksheet.merge_range('A2:AN2', report_name , wbf['merge_format'])
        worksheet.merge_range('A3:AN3', 'PERIODE (' + str(self.month_selection) + ')' , wbf['merge_format_2'])

        row = 6
        worksheet.write('A%s' % (row), 'No', wbf['header'])
        worksheet.write('B%s' % (row), 'NIK', wbf['header'])
        worksheet.write('C%s' % (row), 'Nama', wbf['header'])
        worksheet.write('D%s' % (row), 'Gaji Pokok', wbf['header'])
        worksheet.write('E%s' % (row), 'Gaji Pokok BPJS Kes', wbf['header'])
        worksheet.write('F%s' % (row), 'Gaji Pokok BPJS TK', wbf['header'])
        worksheet.write('G%s' % (row), 'Tunjangan Keahlian', wbf['header'])
        worksheet.write('H%s' % (row), 'Tunjangan Shift 3', wbf['header'])
        worksheet.write('I%s' % (row), 'Tunjangan Kes Non BPJS', wbf['header'])
        worksheet.write('J%s' % (row), 'Bonus Proyek', wbf['header'])
        worksheet.write('K%s' % (row), 'Bonus Bulanan', wbf['header'])
        worksheet.write('L%s' % (row), 'Total Tjg selain Tjg PPh', wbf['header'])
        worksheet.write('M%s' % (row), 'Tunjangan PPh 21', wbf['header'])
        worksheet.write('N%s' % (row), 'BPJS Kes (Perusahaan)', wbf['header'])
        worksheet.write('O%s' % (row), 'BPJS JHT (Perusahaan)', wbf['header'])
        worksheet.write('P%s' % (row), 'BPJS JKK (Perusahaan)', wbf['header'])
        worksheet.write('Q%s' % (row), 'BPJS JP (Perusahaan)', wbf['header'])
        worksheet.write('R%s' % (row), 'BPJS JKM (Perusahaan)', wbf['header'])
        worksheet.write('S%s' % (row), 'Total BPJS bayar Perusahaan', wbf['header'])
        worksheet.write('T%s' % (row), 'Total BPJS untuk PPh21', wbf['header'])
        worksheet.write('U%s' % (row), 'Bonus Tahunan', wbf['header'])
        worksheet.write('V%s' % (row), 'THR', wbf['header'])
        worksheet.write('W%s' % (row), 'Total Komponen Tidak Tetap', wbf['header'])
        worksheet.write('X%s' % (row), 'Penghasilan Bruto', wbf['header'])
        worksheet.write('Y%s' % (row), 'BPJS Kes (Karyawan)', wbf['header'])
        worksheet.write('Z%s' % (row), 'BPJS JHT (Karyawan)', wbf['header'])
        worksheet.write('AA%s' % (row), 'BPJS JP (Karyawan)', wbf['header'])
        worksheet.write('AB%s' % (row), 'Total BPJS bayar Karyawan', wbf['header'])
        worksheet.write('AC%s' % (row), 'Total pot BPJS u/ PPh21', wbf['header'])
        worksheet.write('AD%s' % (row), 'Biaya Jabatan', wbf['header'])
        worksheet.write('AE%s' % (row), 'Potongan Resmi lainnya', wbf['header'])
        worksheet.write('AF%s' % (row), 'Penghasilan Netto', wbf['header'])
        worksheet.write('AG%s' % (row), 'Penghasilan Netto disetahunkan', wbf['header'])
        worksheet.write('AH%s' % (row), 'PTKP', wbf['header'])
        worksheet.write('AI%s' % (row), 'PKP', wbf['header'])
        worksheet.write('AJ%s' % (row), 'PKP Pembulatan', wbf['header'])
        worksheet.write('AK%s' % (row), 'PPh 21 Terutang', wbf['header'])
        worksheet.write('AL%s' % (row), 'PPh 21 Dicicil', wbf['header'])
        worksheet.write('AM%s' % (row), 'Bayar di Muka', wbf['header'])
        worksheet.write('AN%s' % (row), 'THP', wbf['header'])

        row += 1
        no = 1 
        tot_thp = 0
        tot_pph21_perusahaan = 0
        tot_pph21_karyawan = 0
        sum_total_gapok = 0
        sum_bpjs_kesehatan = 0
        sum_bpjs_tk = 0
        sum_total_ahli = 0
        sum_total_shift3 = 0
        sum_total_faskes = 0
        sum_total_lembur = 0
        sum_total_bonus = 0
        sum_total_tunjangan = 0
        sum_total_tpph = 0
        sum_total_kes = 0
        sum_total_jkk = 0
        sum_total_jkm = 0
        # sum_total_bpjs_perusahaan = 0
        sum_total_bota = 0
        sum_total_thr = 0
        sum_total_ktt = 0
        sum_total_bruto = 0
        sum_total_jht2 = 0
        sum_total_jp2 = 0
        # sum_total_bpjs_karyawan = 0
        sum_total_jabat = 0
        sum_total_potong = 0
        sum_total_net = 0
        sum_total_net_annual = 0
        sum_total_ptkp = 0 
        sum_total_pkp_1 = 0
        sum_pkp_pembulatan = 0
        sum_total_pph21_1 = 0
        sum_total_pph21_2 = 0
        sum_total_thp = 0
        sum_total_jp = 0
        sum_jht = 0
        sum_total_bpjs_perusahaan = 0
        sum_kes2 = 0
        sum_total_pkp_2 = 0
        sum_thp = 0
        sum_tot_pph21_perusahaan = 0
        sum_tot_pph21_karyawan = 0

        for rec in rslt:
            tot_thp = float(rec['total_gapok'] + rec['total_tpph'] + rec['total_ktt'] - rec['total_pkp_2'] - rec['total_potong'])
            tot_pph21_perusahaan = float(rec['total_kes'] + rec['total_jkk'] + rec['total_jkm'])
            tot_pph21_karyawan = float(rec['total_jht2'] + rec['total_jp2'])
            worksheet.write('A%s' % (row), no, wbf['content_center'])
            worksheet.write('B%s' % (row), rec.get('nik', ''), wbf['content_center'])
            worksheet.write('C%s' % (row), rec.get('name', ''), wbf['content_center'])
            worksheet.write('D%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_gapok'])), wbf['content_float'])
            worksheet.write('E%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_gapok_bpjs'])), wbf['content_float'])
            # worksheet.write('E%s' % (row), 'Rp.' + '{0:,.0f}'.format(rec['total_gapok_bpjs'] if rec['total_gapok_bpjs'] else 0).replace(',',','), wbf['content_float'])
            worksheet.write('F%s' % (row), 'Rp.' + '{0:,.0f}'.format(rec['bpjs_tk'] if rec['bpjs_tk'] else 0).replace(',',','), wbf['content_float'])
            worksheet.write('G%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_ahli'])), wbf['content_float'])
            worksheet.write('H%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_shift3'])), wbf['content_float'])
            worksheet.write('I%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_faskes'])), wbf['content_float'])
            worksheet.write('J%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_lembur'])), wbf['content_float'])
            worksheet.write('K%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_bonus'])), wbf['content_float'])
            worksheet.write('L%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_tunjangan'])), wbf['content_float'])
            worksheet.write('M%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_tpph'])), wbf['content_float'])
            worksheet.write('N%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_kes'])), wbf['content_float'])
            worksheet.write('O%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['jht'])), wbf['content_float'])
            worksheet.write('P%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_jkk'])), wbf['content_float'])
            worksheet.write('Q%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_jp'])), wbf['content_float'])
            worksheet.write('R%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_jkm'])), wbf['content_float'])
            worksheet.write('S%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_bpjs_perusahaan'])), wbf['content_float'])
            worksheet.write('T%s' % (row), 'Rp.' + '{0:,.0f}'.format(tot_pph21_perusahaan), wbf['content_float'])
            worksheet.write('U%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_bota'])), wbf['content_float'])
            worksheet.write('V%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_thr'])), wbf['content_float'])
            worksheet.write('W%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_ktt'])), wbf['content_float'])
            worksheet.write('X%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_bruto'])), wbf['content_float'])
            worksheet.write('Y%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['kes2'])), wbf['content_float'])
            worksheet.write('Z%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_jht2'])), wbf['content_float'])
            worksheet.write('AA%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_jp2'])), wbf['content_float'])
            worksheet.write('AB%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_pkp_2'])), wbf['content_float'])
            worksheet.write('AC%s' % (row), 'Rp.' + '{0:,.0f}'.format(tot_pph21_karyawan), wbf['content_float'])
            worksheet.write('AD%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_jabat'])), wbf['content_float'])
            worksheet.write('AE%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_potong'])), wbf['content_float'])
            worksheet.write('AF%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_net'])), wbf['content_float'])
            worksheet.write('AG%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_net_annual'])), wbf['content_float'])
            worksheet.write('AH%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_ptkp'])), wbf['content_float'])
            worksheet.write('AI%s' % (row), 'Rp.' + '{0:,.0f}'.format(rec['total_pkp_1'] if rec['total_pkp_1'] > 0 else 0).replace(',',','), wbf['content_float'])
            worksheet.write('AJ%s' % (row), 'Rp.' + '{0:,.0f}'.format(rec['pkp_pembulatan'] if rec['pkp_pembulatan'] > 0 else 0).replace(',',','), wbf['content_float'])
            worksheet.write('AK%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_pph21_1'])), wbf['content_float'])
            worksheet.write('AL%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_pph21_2'])), wbf['content_float'])
            # worksheet.write('AM%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_kes'])), wbf['content_float'])
            worksheet.write('AN%s' % (row), 'Rp.' + '{0:,.0f}'.format(tot_thp), wbf['content_float'])

			
            sum_total_gapok += float(rec['total_gapok'])
            sum_bpjs_kesehatan += float(rec['bpjs_kesehatan'] if rec['bpjs_kesehatan'] else 0)
            sum_bpjs_tk += float(rec['bpjs_tk'] if rec['bpjs_tk'] else 0)
            sum_total_ahli += float(rec['total_ahli'])
            sum_total_shift3 += float(rec['total_shift3'])
            sum_total_faskes += float(rec['total_faskes'])
            sum_total_lembur += float(rec['total_lembur'])
            sum_total_bonus += float(rec['total_bonus'])
            sum_total_tunjangan += float(rec['total_tunjangan'])
            sum_total_tpph += float(rec['total_tpph'])
            sum_total_kes += float(rec['total_kes'])
            sum_total_jkk += float(rec['total_jkk'])
            sum_total_jkm += float(rec['total_jkm'])
            # sum_total_bpjs_perusahaan += float(rec['total_bpjs_perusahaan'])
            sum_total_bota += float(rec['total_bota'])
            sum_total_thr += float(rec['total_thr'])
            sum_total_ktt += float(rec['total_ktt'])
            sum_total_bruto += float(rec['total_bruto'])
            sum_total_jht2 += float(rec['total_jht2'])
            sum_total_jp2 += float(rec['total_jp2'])
            # sum_total_bpjs_karyawan += float(rec['total_bpjs_karyawan'])
            sum_total_jabat += float(rec['total_jabat'])
            sum_total_potong += float(rec['total_potong'])
            sum_total_net += float(rec['total_net'])
            sum_total_net_annual += float(rec['total_net_annual'])
            sum_total_ptkp += float(rec['total_ptkp']) 
            sum_total_pkp_1 += float(rec['total_pkp_1'] if rec['total_pkp_1'] > 0 else 0)
            sum_pkp_pembulatan += float(rec['pkp_pembulatan'] if rec['pkp_pembulatan'] > 0 else 0)
            sum_total_pph21_1 += float(rec['total_pph21_1'])
            sum_total_pph21_2 += float(rec['total_pph21_2'])
            sum_total_thp += float(tot_thp)
            sum_total_jp += float(rec['total_jp'])
            sum_jht += float(rec['jht'])
            sum_total_bpjs_perusahaan += float(rec['total_bpjs_perusahaan'])
            sum_kes2 += float(rec['kes2'])
            sum_total_pkp_2 += float(rec['total_pkp_2'])
            sum_thp += float(tot_thp)
            sum_tot_pph21_perusahaan += float(tot_pph21_perusahaan)
            sum_tot_pph21_karyawan += float(tot_pph21_karyawan)

            no += 1
            row += 1
            
        # TOTAL
        worksheet.merge_range('A%s:C%s' % (row, row), 'TOTAL', wbf['foot_merge_format'])
        worksheet.write('D%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_gapok), wbf['total_float'])
        worksheet.write('E%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_bpjs_kesehatan), wbf['total_float'])
        worksheet.write('F%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_bpjs_tk), wbf['total_float'])
        worksheet.write('G%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_ahli), wbf['total_float'])
        worksheet.write('H%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_shift3), wbf['total_float'])
        worksheet.write('I%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_faskes), wbf['total_float'])
        worksheet.write('J%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_lembur), wbf['total_float'])
        worksheet.write('K%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_bonus), wbf['total_float'])
        worksheet.write('L%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_tunjangan), wbf['total_float'])
        worksheet.write('M%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_tpph), wbf['total_float'])
        worksheet.write('N%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_kes), wbf['total_float'])
        worksheet.write('O%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_jht), wbf['total_float'])
        worksheet.write('P%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_jkk), wbf['total_float'])
        worksheet.write('Q%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_jp), wbf['total_float'])
        worksheet.write('R%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_jkm), wbf['total_float'])
        worksheet.write('S%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_bpjs_perusahaan), wbf['total_float'])
        worksheet.write('T%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_tot_pph21_perusahaan), wbf['total_float'])
        worksheet.write('U%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_bota), wbf['total_float'])
        worksheet.write('V%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_thr), wbf['total_float'])
        worksheet.write('W%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_ktt), wbf['total_float'])
        worksheet.write('X%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_bruto), wbf['total_float'])
        worksheet.write('Y%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_kes2), wbf['total_float'])
        worksheet.write('Z%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_jht2), wbf['total_float'])
        worksheet.write('AA%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_jp2), wbf['total_float'])
        worksheet.write('AB%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_pkp_2), wbf['total_float'])
        worksheet.write('AC%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_tot_pph21_karyawan), wbf['total_float'])
        worksheet.write('AD%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_jabat), wbf['total_float'])
        worksheet.write('AE%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_potong), wbf['total_float'])
        worksheet.write('AF%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_net), wbf['total_float'])
        worksheet.write('AG%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_net_annual), wbf['total_float'])
        worksheet.write('AH%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_ptkp), wbf['total_float'])
        worksheet.write('AI%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_pkp_1), wbf['total_float'])
        worksheet.write('AJ%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_pkp_pembulatan), wbf['total_float'])
        worksheet.write('AK%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_pph21_1), wbf['total_float'])
        worksheet.write('AL%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_pph21_2), wbf['total_float'])
        # worksheet.write('AM%s' % (row), 'Rp.' + '{0:,.0f}'.format(), wbf['total_float'])
        worksheet.write('AN%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_thp), wbf['total_float'])

        filename = '%s %s%s' % (report_name, date_string, '.xlsx')
        workbook.close()
        out = base64.encodebytes(fp.getvalue())
        self.write({'data': out})
        fp.close()


        url = "web/content/?model=" + self._name + "&id=" + str(self.id) + "&field=data&download=true&filename=" + filename
        result = {
			'name': 'LAPORAN GAJI KE GITA SARANA XLSX',
			'type': 'ir.actions.act_url',
			'url': url,
			'target': 'download',
		}
        return result
 
 
class HrReportingBpjs(models.AbstractModel):
    _name = 'report.sh_hr_payroll.report_salary_bpjs'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('_get_report_values')
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        record = data['form']['record']
        return {
            'me': self,
            'date_start': date_start,
            'date_end': date_end,
            'doc_ids': data['ids'],
            'docs': record,
        }

class HrReportingGS(models.AbstractModel):
    _name = 'report.sh_hr_payroll.report_salary_gs'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('_get_report_values')
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        record = data['form']['record']
        return {
            'me': self,
            'date_start': date_start,
            'date_end': date_end,
            'doc_ids': data['ids'],
            'docs': record,
        }