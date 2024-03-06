# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.modules import get_modules, get_module_path
from datetime import date, datetime, timedelta
import logging
logger = logging.getLogger(__name__)
from io import BytesIO
import base64
import xlsxwriter
import csv
import io
from datetime import datetime
from . import add_workbook_format as awf


_STATE =[
        ("gs", "Laporan Gaji pada GS"),
        ("bpjs", "Laporan Gaji pada BPJS"),
	 	("csv", "BNI Direct CSV File"),
         
]

class HrReporting(models.TransientModel):
	_name = 'hr.reporting.wizard'
	_description = 'Generate payslips for all selected employees'
	current_year = datetime.now().year
	date_start = fields.Date(string="Start date", required=False)
	date_end = fields.Date(string="End date", required=False)
	report_type     = fields.Selection(selection=_STATE, string='Report Type',default="gs")
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
	payroll_send_date = fields.Date('Payroll Send Date')
	csv_data = fields.Binary()
	# jabatan = fields.Many2many('hr.employee',string='Jabatan')
	jabatan = fields.Selection(selection="_get_jabatan_list", string='Jabatan')

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

	@api.depends('report_type')
	def _get_jabatan_list(self):
		manajer_payroll = self.env['res.groups'].sudo().browse(237)
		uid = self.env.user.id
		result = []
		
		if uid in manajer_payroll.users.ids:
			result.append(('1','Direktur / Wakil Direktur'))
			result.append(('2','Manager'))
			result.append(('3','Supervisor'))
			result.append(('4','Staff'))
			result.append(('5','Operator'))
			result.append(('6','Staff + Operator'))
			result.append(('7','DIR + MNG + SPV'))
			result.append(('8','MNG + SPV'))
		else:
			result.append(('4','Staff'))
			result.append(('5','Operator'))
			result.append(('6','Staff + Operator'))
		return result

	def action_generate_excel(self):
		if self.report_type != 'gs':
			raise UserError('Silakan pilih Report yang sesuai')
		else:
			rules_in = []
			name_arr = []
			rules = self.env['hr.salary.rule'].search([('appears_on_report','=',True)])
			if self.jabatan in ('1','2','3','4','5'):
				employees = self.env['hr.employee'].search([('jabatan','=',self.jabatan)])
			elif self.jabatan == '6':
				employees = self.env['hr.employee'].search([('jabatan','in',('4','5'))])
			elif self.jabatan == '7':
				employees = self.env['hr.employee'].search([('jabatan','in',('1','2','3'))])
			else:
				employees = self.env['hr.employee'].search([('jabatan','in',('2','3'))])
			for r in rules:
				rules_in.append(r.id)
				name_arr.append(r.name_on_payslip)
			rules_tuple = tuple(rules_in)
			print(employees)
			# query_name = '''
			# 	select
			# 		he.name as nama,
			# 		he.identification_id as nik,
			# 		he.id as employee_id,
			# 		he.tax_category as kategori
			# 	from hr_employee he
			# 	where he.active = true
			# 	and he.identification_id is not null
			# 	order by nama
			# '''
			# self._cr.execute(query_name)
			# res_name = self._cr.dictfetchall() 

			query = '''
				select 
					hpl.employee_id,
					hpl.name as nama_kol,
					hpl.total,
					hpl.code,
					hpl.sequence
				from hr_payslip hp 
				left join hr_payslip_line hpl on hpl.slip_id = hp.id
				left join hr_employee he on he.id = hp.employee_id
				left join hr_job hj on hj.id = he.job_id
				left join hr_contract hc on hc.id = he.contract_id
				where hp.employee_id = '%s'
				and hpl.salary_rule_id in %s
				and date_part('year',hp.create_date) = date_part('year',now())
				and hp.month_selection = '%s'
				and he.active = true
				and he.identification_id is not null
				and hp.state = 'done'
				order by he.name,hpl.sequence
			'''
			
			
			fp = BytesIO()
			date_string = datetime.now().strftime("%Y-%m-%d")
			workbook = xlsxwriter.Workbook(fp)
			wbf, workbook = awf.add_workbook_format(workbook)

			# WKS 1
			report_name = 'LAPORAN PAYROLL PPh 21'
			worksheet = workbook.add_worksheet(report_name)        
			
			worksheet.merge_range('A6:A7','No',wbf['header'])
			worksheet.merge_range('B6:B7','NIK',wbf['header'])
			worksheet.merge_range('C6:C7','Nama',wbf['header'])
			worksheet.merge_range('D6:D7','Kategori Tarif Efektif',wbf['header'])
			header_kol = 4
			header_row = 5

			# iterasi untuk menampilkan header
			for i in name_arr:
				
				worksheet.merge_range(header_row,header_kol,header_row+1,header_kol,'%s'%(i),wbf['header'])
				header_kol +=1

			#set column width
			worksheet.set_column('A:A', 5)
			worksheet.set_column('B:B', 30)
			worksheet.set_column('C:C', 35)
			worksheet.set_column('D:AT', 20)

			# WKS 1

			worksheet.merge_range('A2:AT2', report_name , wbf['merge_format'])
			worksheet.merge_range('A3:AT3', 'PERIODE (' + str(self.month_selection) + ')' , wbf['merge_format_2'])

			row = 7
			col = 0
			col_rec = 4
			no = 1

			# # iterasi untuk menampilkan nama karyawan		
			# for res in res_name:
			# 	worksheet.write(row_name,col_name, no, wbf['content_center'])
			# 	worksheet.write(row_name,col_name + 1, res.get('nik', ''), wbf['content_center'])
			# 	worksheet.write(row_name,col_name + 2, res.get('nama', ''), wbf['content_center'])
			# 	worksheet.write(row_name,col_name + 3, res.get('kategori', ''), wbf['content_center'])
			# 	no += 1
			# 	row_name +=1

			# # iterasi untuk menampilkan nominal
			# for index, rec in enumerate(rslt):
			# 	prev_rec = rslt[index-1]
			# 	curr_rec = rec
			# 	if(curr_rec['employee_id'] == prev_rec['employee_id']):
			# 		worksheet.write(row,col, rec['total'],wbf['content_float'])
			# 	else:
			# 		row += 1
			# 		col = 4
			# 		worksheet.write(row,col, rec['total'],wbf['content_float'])
			# 	col += 1

			#iterasi gabungan untuk menampilkan data
			for i in employees:
				self._cr.execute(query % (i.id,rules_tuple,self.month_selection))
				rslt = self._cr.dictfetchall() 
				worksheet.write(row,col, no, wbf['content_center'])
				worksheet.write(row,col + 1, i.identification_id, wbf['content_center'])
				worksheet.write(row,col + 2, i.name, wbf['content_center'])
				worksheet.write(row,col + 3, i.tax_category, wbf['content_center'])
				for rec in rslt:
					worksheet.write(row,col_rec,rec['total'],wbf['content_float'])
					col_rec += 1
				no += 1
				row += 1
				col = 0
				col_rec = 4

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
	
	def action_generate_csv(self):
		
		if self.report_type != 'csv':
			raise UserError('Silakan pilih Report yang sesuai')
		else:
			now = datetime.now() + timedelta(hours=7)
			create_datetime = now.strftime("%Y/%m/%d_%H.%M.%S")
			paycheck_date = self.payroll_send_date.strftime("%Y%m%d")
			if self.jabatan in ('1','2','3','4','5'):
				employees = self.env['hr.employee'].search([('domestic_bank_id','!=',''),('no_rekening','!=',''),('jabatan','=',self.jabatan)])
			elif self.jabatan == '6':
				employees = self.env['hr.employee'].search([('domestic_bank_id','!=',''),('no_rekening','!=',''),('jabatan','in',('4','5'))])
			elif self.jabatan == '7':
				employees = self.env['hr.employee'].search([('domestic_bank_id','!=',''),('no_rekening','!=',''),('jabatan','in',('1','2','3'))])
			else:
				employees = self.env['hr.employee'].search([('domestic_bank_id','!=',''),('no_rekening','!=',''),('jabatan','in',('2','3'))])
			
			
			thp_query = '''
				select total 
				from hr_payslip hp 
				left join hr_payslip_line hpl on hpl.slip_id = hp.id 
				where hp.employee_id = '%s'
				and hpl.code = 'THP'
				and hp.month_selection = '%s'
				and date_part('year',hp.create_date) = date_part('year',now())
			'''
			rec_sum = 0

			# menghitung sum dari seluruh gaji karyawan
			for i in employees:
				self._cr.execute(thp_query % (i.id,self.month_selection))
				thp = self._cr.dictfetchall() 
				rec_sum += thp[0]['total']

			# tulis record ke dalam file
			# modif menggunakan mpath = get_module_path(sh_hr_payroll)
			# atur chmod 777 dan chown 
			mpath = get_module_path('sh_hr_payroll')
			with open(mpath + '/static/payroll.csv',mode='w') as file:
				writer = csv.writer(file, delimiter=',',dialect='excel',quoting=csv.QUOTE_MINIMAL,lineterminator="\n")
				row_1 = [create_datetime,len(employees)+2]
				for x in range(18):
					row_1.append('')
				row_2 = ['P',paycheck_date,'6663777999',len(employees),int(rec_sum)]
				for x in range(15):
					row_2.append('')
				row_3 = []

				writer.writerow(row_1)
				writer.writerow(row_2)
				
				for i in employees:
					self._cr.execute(thp_query % (i.id,self.month_selection))
					thp_val = self._cr.dictfetchall() 
					row_3.clear()
					row_3.append(i.no_rekening)
					row_3.append(i.name)
					row_3.append(int(thp_val[0]['total']))
					row_3.append('GAJI '+self.month_selection+'-24')
					row_3.append('')
					row_3.append('')
					if (i.domestic_bank_id.bank_code != "000000"):
						row_3.append(i.domestic_bank_id.bank_code)
						row_3.append(i.domestic_bank_id.bank_name)
					else:
						row_3.append('')
						row_3.append('')
					for t in range(8):
						row_3.append('')
					if (i.domestic_bank_id.bank_code != "000000"):
						row_3.append('Y')
						row_3.append('stefi@altinex.co')
					else:
						row_3.append('N')
						row_3.append('')
					row_3.append('')
					row_3.append('N')
					writer.writerow(row_3)
					
			# baca record dari file
			with open(mpath + '/static/payroll.csv', 'r', encoding="utf-8") as file2:
				data = str.encode(file2.read(), 'utf-8')
				# print(data)
				filename = 'payroll.csv'
				self.csv_data = base64.encodestring(data)
				url = "web/content/?model=" + self._name + "&id=" + str(self.id) + "&field=csv_data&download=true&filename=" + filename
				result = {
					'name': 'BNI Direct CSV',
					'type': 'ir.actions.act_url',
					'url': url,
					'target': 'download',
				}
				return result
            
        #     tot_thp = float(rec['total_gapok'] + rec['total_tpph'] + rec['total_ktt'] - rec['total_pkp_2'] - rec['total_potong'])
        #     tot_pph21_perusahaan = float(rec['total_kes'] + rec['total_jkk'] + rec['total_jkm'])
        #     tot_pph21_karyawan = float(rec['total_jht2'] + rec['total_jp2'])
			
            # worksheet.write('A%s' % (row), no, wbf['content_center'])
            # if (rec[index]['employee_id'] != rec[index-1]['employee_id']):
            # 	worksheet.write('B%s' % (row), rec.get('nik', ''), wbf['content_center'])
	       
            
                
            	# worksheet.write('C%s' % (row), rec.get('nama', ''), wbf['content_center'])
            # elif(rec['code'] == 'GAPOK'):
            #       worksheet.write('D%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total'])), wbf['content_float'])
            # elif(rec['code'] == 'GAPOK_BPJS_KES'):
            #       worksheet.write('E%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total'])), wbf['content_float'])
            # elif(rec['code'] == 'GAPOK_BPJS_TK'):
            #       worksheet.write('F%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total'])), wbf['content_float'])
            
        #     worksheet.write('E%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_gapok_bpjs'])), wbf['content_float'])
        #     # worksheet.write('E%s' % (row), 'Rp.' + '{0:,.0f}'.format(rec['total_gapok_bpjs'] if rec['total_gapok_bpjs'] else 0).replace(',',','), wbf['content_float'])
        #     worksheet.write('F%s' % (row), 'Rp.' + '{0:,.0f}'.format(rec['bpjs_tk'] if rec['bpjs_tk'] else 0).replace(',',','), wbf['content_float'])
        #     worksheet.write('G%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_ahli'])), wbf['content_float'])
        #     worksheet.write('H%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_shift3'])), wbf['content_float'])
        #     worksheet.write('I%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_faskes'])), wbf['content_float'])
        #     worksheet.write('J%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_lembur'])), wbf['content_float'])
        #     worksheet.write('K%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_bonus'])), wbf['content_float'])
        #     worksheet.write('L%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_tunjangan'])), wbf['content_float'])
        #     worksheet.write('M%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_tpph'])), wbf['content_float'])
        #     worksheet.write('N%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_kes'])), wbf['content_float'])
        #     worksheet.write('O%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['jht'])), wbf['content_float'])
        #     worksheet.write('P%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_jkk'])), wbf['content_float'])
        #     worksheet.write('Q%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_jp'])), wbf['content_float'])
        #     worksheet.write('R%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_jkm'])), wbf['content_float'])
        #     worksheet.write('S%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_bpjs_perusahaan'])), wbf['content_float'])
        #     worksheet.write('T%s' % (row), 'Rp.' + '{0:,.0f}'.format(tot_pph21_perusahaan), wbf['content_float'])
        #     worksheet.write('U%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_bota'])), wbf['content_float'])
        #     worksheet.write('V%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_thr'])), wbf['content_float'])
        #     worksheet.write('W%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_ktt'])), wbf['content_float'])
        #     worksheet.write('X%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_pengurangan_bruto'])), wbf['content_float'])
        #     worksheet.write('Y%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_bruto'])), wbf['content_float'])
        #     worksheet.write('Z%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['kes2'])), wbf['content_float'])
        #     worksheet.write('AA%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_jht2'])), wbf['content_float'])
        #     worksheet.write('AB%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_jp2'])), wbf['content_float'])
        #     worksheet.write('AC%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_pkp_2'])), wbf['content_float'])
        #     worksheet.write('AD%s' % (row), 'Rp.' + '{0:,.0f}'.format(tot_pph21_karyawan), wbf['content_float'])
        #     worksheet.write('AE%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_jabat'])), wbf['content_float'])
        #     worksheet.write('AF%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_potong'])), wbf['content_float'])
        #     worksheet.write('AG%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_net'])), wbf['content_float'])
        #     worksheet.write('AH%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_net_annual'])), wbf['content_float'])
        #     worksheet.write('AI%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_ptkp'])), wbf['content_float'])
        #     worksheet.write('AJ%s' % (row), 'Rp.' + '{0:,.0f}'.format(rec['total_pkp_1'] if rec['total_pkp_1'] > 0 else 0).replace(',',','), wbf['content_float'])
        #     worksheet.write('AK%s' % (row), 'Rp.' + '{0:,.0f}'.format(rec['pkp_pembulatan'] if rec['pkp_pembulatan'] > 0 else 0).replace(',',','), wbf['content_float'])
        #     worksheet.write('AL%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_pph21_1'])), wbf['content_float'])
        #     worksheet.write('AM%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_pph21_2'])), wbf['content_float'])
        #     # worksheet.write('AM%s' % (row), 'Rp.' + '{0:,.0f}'.format(float(rec['total_kes'])), wbf['content_float'])
        #     worksheet.write('AO%s' % (row), 'Rp.' + '{0:,.2f}'.format(float(rec['thp_2'])), wbf['content_float'])
			
        #     sum_total_gapok += float(rec['total_gapok'])
        #     sum_bpjs_kesehatan += float(rec['bpjs_kesehatan'] if rec['bpjs_kesehatan'] else 0)
        #     sum_bpjs_tk += float(rec['bpjs_tk'] if rec['bpjs_tk'] else 0)
        #     sum_total_ahli += float(rec['total_ahli'])
        #     sum_total_shift3 += float(rec['total_shift3'])
        #     sum_total_faskes += float(rec['total_faskes'])
        #     sum_total_lembur += float(rec['total_lembur'])
        #     sum_total_bonus += float(rec['total_bonus'])
        #     sum_total_tunjangan += float(rec['total_tunjangan'])
        #     sum_total_tpph += float(rec['total_tpph'])
        #     sum_total_kes += float(rec['total_kes'])
        #     sum_total_jkk += float(rec['total_jkk'])
        #     sum_total_jkm += float(rec['total_jkm'])
        #     # sum_total_bpjs_perusahaan += float(rec['total_bpjs_perusahaan'])
        #     sum_total_bota += float(rec['total_bota'])
        #     sum_total_thr += float(rec['total_thr'])
        #     sum_total_ktt += float(rec['total_ktt'])
        #     sum_total_bruto += float(rec['total_bruto'])
        #     sum_total_jht2 += float(rec['total_jht2'])
        #     sum_total_jp2 += float(rec['total_jp2'])
        #     # sum_total_bpjs_karyawan += float(rec['total_bpjs_karyawan'])
        #     sum_total_jabat += float(rec['total_jabat'])
        #     sum_total_potong += float(rec['total_potong'])
        #     sum_total_net += float(rec['total_net'])
        #     sum_total_net_annual += float(rec['total_net_annual'])
        #     sum_total_ptkp += float(rec['total_ptkp']) 
        #     sum_total_pkp_1 += float(rec['total_pkp_1'] if rec['total_pkp_1'] > 0 else 0)
        #     sum_pkp_pembulatan += float(rec['pkp_pembulatan'] if rec['pkp_pembulatan'] > 0 else 0)
        #     sum_total_pph21_1 += float(rec['total_pph21_1'])
        #     sum_total_pph21_2 += float(rec['total_pph21_2'])
        #     sum_total_thp += float(tot_thp)
        #     sum_total_jp += float(rec['total_jp'])
        #     sum_jht += float(rec['jht'])
        #     sum_total_bpjs_perusahaan += float(rec['total_bpjs_perusahaan'])
        #     sum_kes2 += float(rec['kes2'])
        #     sum_total_pkp_2 += float(rec['total_pkp_2'])
        #     sum_thp += float(rec['thp_2'])
        #     sum_tot_pph21_perusahaan += float(tot_pph21_perusahaan)
        #     sum_tot_pph21_karyawan += float(tot_pph21_karyawan)
        #     sum_tot_pengurangan_bruto += float(rec['total_pengurangan_bruto'])
			          
            
        # # TOTAL
        # worksheet.merge_range('A%s:C%s' % (row, row), 'TOTAL', wbf['foot_merge_format'])
        # worksheet.write('D%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_gapok), wbf['total_float'])
        # worksheet.write('E%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_bpjs_kesehatan), wbf['total_float'])
        # worksheet.write('F%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_bpjs_tk), wbf['total_float'])
        # worksheet.write('G%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_ahli), wbf['total_float'])
        # worksheet.write('H%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_shift3), wbf['total_float'])
        # worksheet.write('I%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_faskes), wbf['total_float'])
        # worksheet.write('J%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_lembur), wbf['total_float'])
        # worksheet.write('K%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_bonus), wbf['total_float'])
        # worksheet.write('L%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_tunjangan), wbf['total_float'])
        # worksheet.write('M%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_tpph), wbf['total_float'])
        # worksheet.write('N%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_kes), wbf['total_float'])
        # worksheet.write('O%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_jht), wbf['total_float'])
        # worksheet.write('P%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_jkk), wbf['total_float'])
        # worksheet.write('Q%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_jp), wbf['total_float'])
        # worksheet.write('R%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_jkm), wbf['total_float'])
        # worksheet.write('S%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_bpjs_perusahaan), wbf['total_float'])
        # worksheet.write('T%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_tot_pph21_perusahaan), wbf['total_float'])
        # worksheet.write('U%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_bota), wbf['total_float'])
        # worksheet.write('V%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_thr), wbf['total_float'])
        # worksheet.write('W%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_ktt), wbf['total_float'])
        # worksheet.write('X%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_tot_pengurangan_bruto), wbf['total_float'])
        # worksheet.write('Y%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_bruto), wbf['total_float'])
        # worksheet.write('Z%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_kes2), wbf['total_float'])
        # worksheet.write('AA%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_jht2), wbf['total_float'])
        # worksheet.write('AB%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_jp2), wbf['total_float'])
        # worksheet.write('AC%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_pkp_2), wbf['total_float'])
        # worksheet.write('AD%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_tot_pph21_karyawan), wbf['total_float'])
        # worksheet.write('AE%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_jabat), wbf['total_float'])
        # worksheet.write('AF%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_potong), wbf['total_float'])
        # worksheet.write('AG%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_net), wbf['total_float'])
        # worksheet.write('AH%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_net_annual), wbf['total_float'])
        # worksheet.write('AI%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_ptkp), wbf['total_float'])
        # worksheet.write('AJ%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_pkp_1), wbf['total_float'])
        # worksheet.write('AK%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_pkp_pembulatan), wbf['total_float'])
        # worksheet.write('AL%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_pph21_1), wbf['total_float'])
        # worksheet.write('AM%s' % (row), 'Rp.' + '{0:,.0f}'.format(sum_total_pph21_2), wbf['total_float'])
        # # worksheet.write('AN%s' % (row), 'Rp.' + '{0:,.0f}'.format(), wbf['total_float'])
        # worksheet.write('AO%s' % (row), 'Rp.' + '{0:,.2f}'.format(sum_thp), wbf['total_float'])
 
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
    
