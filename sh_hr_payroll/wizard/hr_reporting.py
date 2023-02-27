# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta

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

    def action_generate_pdf(self):
        job_ids = str(tuple(self.job_ids.ids)).replace(',)',')')
        if not self.job_ids:
            raise UserError('Mohon maaf anda tidak memiliki akses ..')
        query =f"""
            SELECT 
                he.name, 
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
                sum(payslip.total_pkp_2) as total_pkp_2,
                sum(payslip.total_pph21_1) as total_pph21_1,
                sum(payslip.total_pph21_2) as total_pph21_2,
                sum(payslip.total_thp_1) as total_thp,
                sum(payslip.jht) as total_jht,
                sum(payslip.jp) as total_jp,
                sum(payslip.kes2) as total_kes2
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
						0 as jp,
						0 as kes2,
						hp.employee_id
                    FROM
                hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
				left join hr_employee he on he.id = hp.employee_id
				left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
                    WHERE hpl.code = 'GAPOK_BPJS'
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
                    WHERE hpl.code = 'PKP_2'
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
                    WHERE hpl.code = 'PPH21_2_SUM'
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
                    WHERE hpl.code = 'PPH21_2_SEBULAN'
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						hpl.total as jp,
						0 as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
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
						0 as jp,
						hpl.total as kes2,
						hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
					left join hr_employee he on he.id = hp.employee_id
					left join hr_job hj on hj.id = he.job_id
                    WHERE hpl.code = 'KES2'
                    AND hp.month_selection = '{self.month_selection}'
					AND hj.id in {job_ids}
                ) AS payslip 
            left join hr_employee he on he.id = payslip.employee_id
			left join hr_job hj on hj.id = he.job_id
            GROUP BY he.name
            """ 
			# % (self.month_selection, self.month_selection, self.month_selection, self.month_selection, self.month_selection, self.month_selection, self.month_selection,
            #        self.month_selection, self.month_selection, self.month_selection, self.month_selection, self.month_selection, self.month_selection, self.month_selection,
            #        self.month_selection, self.month_selection, self.month_selection, self.month_selection, self.month_selection, self.month_selection, self.month_selection,
            #        self.month_selection, self.month_selection, self.month_selection, self.month_selection, self.month_selection, self.month_selection, self.month_selection,
            #        self.month_selection, self.month_selection, self.month_selection
            # )
        self._cr.execute(query)
        record = self._cr.dictfetchall()
            
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
        else :
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