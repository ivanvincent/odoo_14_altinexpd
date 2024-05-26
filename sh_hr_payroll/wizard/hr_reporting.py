# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.modules import get_modules, get_module_path
from datetime import date, datetime, timedelta
import calendar
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
        ("pph21", "Laporan PPH 21"),
		("request", "Payment Request"),
	 	("csv", "BNI Direct CSV File"),         
]

class HrReporting(models.TransientModel):
	_name = 'hr.reporting.wizard'
	_description = 'Generate payslips for all selected employees'
	current_year = datetime.now().year
	date_start = fields.Date(string="Start date", required=False)
	date_end = fields.Date(string="End date", required=False)
	report_type     = fields.Selection(selection=_STATE, string='Report Type',default="pph21")
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
	data = fields.Binary(string='Data')
	payroll_send_date = fields.Date('Payroll Send Date')
	csv_data = fields.Binary()
	jabatan = fields.Selection(selection="_get_jabatan_list", string='Jabatan')
	coa = fields.Selection([
		('1','Produksi'),
		('2','Umum'),
		('3','All COA'),
	], string='COA')

	@api.depends('report_type')
	def _get_jabatan_list(self):
		manajer_payroll = self.env['res.groups'].sudo().browse(240)
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
			result.append(('20','SELURUH KARYAWAN'))
		else:
			result.append(('4','Staff'))
			result.append(('5','Operator'))
			result.append(('6','Staff + Operator'))
		
		return result

	def action_generate_excel(self):
		if self.report_type != 'pph21':
			raise UserError('Silakan pilih Report yang sesuai')
		else:
			# Cutoff Date
			date_rec = datetime(int(self.current_year), int(self.month_selection), 20)
			month_string = date_rec.strftime("%b")
			year_string = date_rec.strftime("%y")

			# Filter salary rule - appear on report
			rules_in = []
			name_arr = []
			rules = self.env['hr.salary.rule'].search([('appears_on_report','=',True)])
			for r in rules:
				rules_in.append(r.id)
				name_arr.append(r.name_on_payslip)
			rules_tuple = tuple(rules_in)

			# Filter employee sesuai jabatan DAN coa
			if self.coa == '3':
				if self.jabatan in ('1','2','3','4','5'):
					employees = self.env['hr.employee'].search([('jabatan','=',self.jabatan),('joining_date','<=',date_rec)])
				elif self.jabatan == '6':
					employees = self.env['hr.employee'].search([('jabatan','in',('4','5')),('joining_date','<=',date_rec)])
				elif self.jabatan == '7':
					employees = self.env['hr.employee'].search([('jabatan','in',('1','2','3')),('joining_date','<=',date_rec)])
				elif self.jabatan == '8':
					employees = self.env['hr.employee'].search([('jabatan','in',('2','3')),('joining_date','<=',date_rec)])
				else:
					employees = self.env['hr.employee'].search([('jabatan','in',('1','2','3','4','5')),('joining_date','<=',date_rec)])
			else:
				if self.jabatan in ('1','2','3','4','5'):
					employees = self.env['hr.employee'].search([('jabatan','=',self.jabatan),('coa','=',self.coa),('joining_date','<=',date_rec)])
				elif self.jabatan == '6':
					employees = self.env['hr.employee'].search([('jabatan','in',('4','5')),('coa','=',self.coa),('joining_date','<=',date_rec)])
				elif self.jabatan == '7':
					employees = self.env['hr.employee'].search([('jabatan','in',('1','2','3')),('coa','=',self.coa),('joining_date','<=',date_rec)])
				elif self.jabatan == '8':
					employees = self.env['hr.employee'].search([('jabatan','in',('2','3')),('coa','=',self.coa),('joining_date','<=',date_rec)])
				else:
					employees = self.env['hr.employee'].search([('jabatan','in',('1','2','3','4','5')),('coa','=',self.coa),('joining_date','<=',date_rec)])
			print(employees)

			# Query Execution
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
				where date_part('year',hp.create_date) = date_part('year',now())
				and hp.month_selection = '%s'
				and hp.employee_id = '%s'
				and he.active = true
				and he.identification_id is not null
				and hp.state = 'done'
				and hpl.salary_rule_id in %s
				order by he.name,hpl.sequence
			'''
			
			# Excel Writer Preparation
			fp = BytesIO()
			workbook = xlsxwriter.Workbook(fp)
			wbf, workbook = awf.add_workbook_format(workbook)
			header_format_1 = workbook.add_format({'bold':True, 'font_size':12, 'align':'center', 'valign':'vcenter', 'border':1, 'bg_color':'#9FFCFA','text_wrap':True})
			header_format_2 = workbook.add_format({'bold':True, 'font_size':12, 'align':'center', 'valign':'vcenter', 'border':1, 'num_format':40, 'bg_color':'#FBFB53'})

			# WKS 1
			if self.jabatan == '1':
				report_name = 'LAPORAN PAYROLL PPh 21 DIR / WAKIL DIR'
			elif self.jabatan == '2':
				report_name = 'LAPORAN PAYROLL PPh 21 MNG'
			elif self.jabatan == '3':
				report_name = 'LAPORAN PAYROLL PPh 21 SPV'
			elif self.jabatan == '4':
				report_name = 'LAPORAN PAYROLL PPh 21 STAFF'
			elif self.jabatan == '5':
				report_name = 'LAPORAN PAYROLL PPh 21 OPERATOR'
			elif self.jabatan == '6':
				report_name = 'LAPORAN PAYROLL PPh 21 STAFF + OP'
			elif self.jabatan == '7':
				report_name = 'LAPORAN PAYROLL PPh 21 DIR + MNG + SPV'
			elif self.jabatan == '8':
				report_name = 'LAPORAN PAYROLL PPh 21 MNG + SPV'
			else : 
				report_name = 'LAPORAN PAYROLL PPh 21 SELURUH KARYAWAN'
			worksheet = workbook.add_worksheet(report_name)        
			
			# WKS 1 - Header
			worksheet.merge_range('A6:A7','No',header_format_1)
			worksheet.merge_range('B6:B7','NIK',header_format_1)
			worksheet.merge_range('C6:C7','Nama',header_format_1)
			worksheet.merge_range('D6:D7','Kategori Tarif Efektif',header_format_1)
			header_kol = 4
			header_row = 5

			# WKS 1 - Iterasi untuk menampilkan header
			header_wo_sum = []
			for i in name_arr:
				worksheet.merge_range(header_row,header_kol,header_row+1,header_kol,'%s'%(i),header_format_1)
				if i in ('PTKP','Gaji Pokok','GAPOK BPJS Kesehatan','GAPOK BPJS TK','Tarif Efektif Pajak (persen)'):
					header_wo_sum.append(header_kol)
				header_kol +=1

			# WKS 1 - Set column width
			worksheet.set_column('A:A', 5)
			worksheet.set_column('B:B', 30)
			worksheet.set_column('C:C', 35)
			worksheet.set_column('D:AT', 20)

			# WKS 1 - Judul
			worksheet.merge_range('A2:AT2', report_name , wbf['merge_format'])
			worksheet.merge_range('A3:AT3', 'PERIODE ' + month_string + year_string , wbf['merge_format_2'])

			# WKS 1 - Iterasi gabungan untuk menampilkan data
			row = 7
			col = 0
			col_rec = 4
			no = 1
			for i in employees:
				self._cr.execute(query % (self.month_selection,i.id,rules_tuple))
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
				col_rec_end = col_rec
				col = 0
				col_rec = 4

			# File name
			filename = '%s_%s%s%s' % (report_name, month_string, year_string, '.xlsx')
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
	
	def action_generate_request(self):
		if self.report_type != 'request':
			raise UserError('Silakan pilih Report yang sesuai')
		else:
			# Cutoff Date
			date_rec = datetime(int(self.current_year), int(self.month_selection), 20)
			month_string = date_rec.strftime("%b")
			year_string = date_rec.strftime("%y")
			last_date = calendar.monthrange(date_rec.year, date_rec.month)[1]

			# QUERIES
			request_query = '''
				select total 
				from hr_payslip hp 
				left join hr_payslip_line hpl on hpl.slip_id = hp.id 
				left join hr_employee he on he.id = hp.employee_id
				left join hr_job hj on hj.id = he.job_id
				left join hr_contract hc on hc.id = he.contract_id
				where hpl.code = '%s'
				and he.active = true
				and hc.date_start <= '%s'
				and hp.month_selection = '%s'
				and date_part('year',hp.create_date) = date_part('year',now())
			'''

			gaji_query = '''
				select total 
				from hr_payslip hp 
				left join hr_payslip_line hpl on hpl.slip_id = hp.id 
				left join hr_employee he on he.id = hp.employee_id
				left join hr_job hj on hj.id = he.job_id
				left join hr_contract hc on hc.id = he.contract_id
				where hp.employee_id = '%s'
				and hpl.code = '%s'
				and he.active = true
				and hc.date_start <= '%s'
				and hp.month_selection = '%s'
				and date_part('year',hp.create_date) = date_part('year',now())
			'''
			employee_umum = self.env['hr.employee'].search([('coa','=','2')])
			employee_prod = self.env['hr.employee'].search([('coa','=','1')])
			hpl_code = ['BRUTO','PPH_CICIL','JHT2','JP2','KES2','JKK','JKM','JHT','JP','KES','THR','PIKA']
			var_name = {}

			for code in hpl_code:
				var_name['total_'+code] = 0
				var_name['total_prod_'+code] = 0
				var_name['total_umum_'+code] = 0
				self._cr.execute(request_query % (code,date_rec,self.month_selection))
				request1 = self._cr.dictfetchall() 
				for rec in request1:
					var_name['total_'+code] += float(rec['total'])
				for i in employee_prod:
					self._cr.execute(gaji_query % (i.id,code,date_rec,self.month_selection))
					request2 = self._cr.dictfetchall()
					for rec in request2: 
						var_name['total_prod_'+code] += float(0 if rec['total'] is None else rec['total'])
				for i in employee_umum:
					self._cr.execute(gaji_query % (i.id,code,date_rec,self.month_selection))
					request3 = self._cr.dictfetchall()
					for rec in request3: 
						var_name['total_umum_'+code] += float(0 if rec['total'] is None else rec['total'])
				locals().update(var_name)
			
			print(var_name)
			request_len = len(request1)
			gaji_prod = var_name['total_prod_BRUTO'] - var_name['total_prod_THR']
			gaji_umum = var_name['total_umum_BRUTO'] - var_name['total_umum_THR']
			
			# Excel Writer Prep
			fp = BytesIO()
			workbook = xlsxwriter.Workbook(fp)
			wbf, workbook = awf.add_workbook_format(workbook)
			title_format = workbook.add_format({'bold':True, 'underline':True, 'font_size':22, 'align':'center', 'valign':'vcenter'})
			title_format_2 = workbook.add_format({'bold':True, 'underline':True, 'font_size':12, 'align':'center', 'valign':'vcenter'})
			header_format_1 = workbook.add_format({'bold':True, 'font_size':12, 'align':'left', 'valign':'vcenter'})
			header_format_2 = workbook.add_format({'bold':True, 'font_size':12, 'align':'center', 'valign':'vcenter', 'border':1})
			content_format_1 = workbook.add_format({'font_size':12, 'align':'left', 'valign':'vcenter'})
			content_format_2 = workbook.add_format({'font_size':12, 'align':'left', 'valign':'vcenter', 'left':1, 'right':1, 'num_format':40})
			content_format_3 = workbook.add_format({'font_size':12, 'align':'right', 'valign':'vcenter', 'left':1, 'right':1, 'num_format':40})
			content_format_4 = workbook.add_format({'bold':True, 'font_size':12, 'align':'right', 'valign':'vcenter', 'border':1, 'num_format':40})

			# Sheet 1
			worksheet = workbook.add_worksheet('PAYMENT REQUEST')

			# Sheet 1 - Set column width
			worksheet.set_column('A:A', 5)
			worksheet.set_column('B:B', 5)
			worksheet.set_column('C:P', 8)

			# Sheet 1 - Title
			worksheet.merge_range('L2:M2','Nomor :',header_format_1)
			worksheet.merge_range('L3:M3','Tanggal :',header_format_1)
			worksheet.merge_range('N3:P3','%s %s %s' % (str(last_date), str(month_string), str(year_string)),content_format_1)
			worksheet.merge_range('L4:M4','Mata Uang :',header_format_1)
			worksheet.merge_range('N4:P4','Rp',content_format_1)
			worksheet.merge_range('L5:M5','Jumlah Data :',header_format_1)
			worksheet.merge_range('N5:P5',request_len,content_format_1)
			worksheet.merge_range('C6:P7','PAYMENT REQUEST',title_format)

			# Sheet 1 - Header
			worksheet.merge_range('C9:C10','No.',header_format_2)
			worksheet.merge_range('D9:K10','Uraian',header_format_2)
			worksheet.merge_range('L9:P10','Jumlah',header_format_2)

			# Sheet 1 - Table 1
			worksheet.write('C11','1',content_format_2)
			worksheet.merge_range('D11:K11','TOTAL BIAYA GAJI',content_format_2)
			worksheet.merge_range('L11:P11',var_name['total_BRUTO'],content_format_3)

			worksheet.write('C12','2',content_format_2)
			worksheet.merge_range('D12:K12','PPH 21',content_format_2)
			worksheet.merge_range('L12:P12',0-var_name['total_PPH_CICIL'],content_format_3)
			
			worksheet.write('C13','3',content_format_2)
			worksheet.merge_range('D13:K13','JHT (BY JAMSOSTEK)',content_format_2)
			worksheet.merge_range('L13:P13',0-var_name['total_JHT2'],content_format_3)
			
			worksheet.write('C14','4',content_format_2)
			worksheet.merge_range('D14:K14','JP (BY JAMSOSTEK)',content_format_2)
			worksheet.merge_range('L14:P14',0-var_name['total_JP2'],content_format_3)
			
			worksheet.write('C15','5',content_format_2)
			worksheet.merge_range('D15:K15','KES (BY JAMSOSTEK)',content_format_2)
			worksheet.merge_range('L15:P15',0-var_name['total_KES2'],content_format_3)
			
			worksheet.write('C16','6',content_format_2)
			worksheet.merge_range('D16:K16','TUNJ JKK (BY JAMSOSTEK)',content_format_2)
			worksheet.merge_range('L16:P16',0-(var_name['total_JKK']+var_name['total_JKM']),content_format_3)
			
			worksheet.write('C17','7',content_format_2)
			worksheet.merge_range('D17:K17','TOTAL JHT (BY JAMSOSTEK)',content_format_2)
			worksheet.merge_range('L17:P17',0-var_name['total_JHT'],content_format_3)
			
			worksheet.write('C18','8',content_format_2)
			worksheet.merge_range('D18:K18','JP (BY JAMSOSTEK)',content_format_2)
			worksheet.merge_range('L18:P18',0-var_name['total_JP'],content_format_3)
			
			worksheet.write('C19','9',content_format_2)
			worksheet.merge_range('D19:K19','TUNJ BPJS (BY JAMSOSTEK)',content_format_2)
			worksheet.merge_range('L19:P19',0-var_name['total_KES'],content_format_3)
			
			worksheet.write('C20','10',content_format_2)
			worksheet.merge_range('D20:K20','ASTEK',content_format_2)
			worksheet.merge_range('L20:P20',var_name['total_JHT']+var_name['total_JP'],content_format_3)

			worksheet.write('C21','11',content_format_2)
			worksheet.merge_range('D21:K21','THR',content_format_2)
			worksheet.merge_range('L21:P21',0-var_name['total_THR'],content_format_3)
			
			worksheet.write('C22','12',content_format_2)
			worksheet.merge_range('D22:K22','POTONGAN',content_format_2)
			worksheet.merge_range('L22:P22',0-var_name['total_PIKA'],content_format_3)
			
			worksheet.merge_range('C23:K23','TOTAL :',header_format_2)
			worksheet.merge_range('L23:P23','=SUM(L11:P22)',content_format_4)

			# Sheet 1 - Table 2
			worksheet.merge_range('C25:F25','COA GAJI BULANAN '+ '%s%s' % (str(month_string), str(year_string)), title_format_2)
			worksheet.merge_range('C26:D26','', header_format_2)
			worksheet.merge_range('E26:F26',month_string, header_format_2)
			worksheet.merge_range('C27:D27','Gaji Produksi',content_format_2)
			worksheet.merge_range('E27:F27',gaji_prod,content_format_3)
			worksheet.merge_range('C28:D28','Gaji Umum',content_format_2)
			worksheet.merge_range('E28:F28',gaji_umum,content_format_3)
			worksheet.merge_range('C29:D29','TOTAL',header_format_2)
			worksheet.merge_range('E29:F29','=SUM(E27:E28)',content_format_4)

			# Sheet 1 - Table 3
			worksheet.merge_range('C33:F33','COA THR ' + '%s%s' % (str(month_string), str(year_string)), title_format_2)
			worksheet.merge_range('C34:D34','', header_format_2)
			worksheet.merge_range('E34:F34',month_string, header_format_2)
			worksheet.merge_range('C35:D35','THR Produksi',content_format_2)
			worksheet.merge_range('E35:F35',var_name['total_prod_THR'],content_format_3)
			worksheet.merge_range('C36:D36','THR Umum',content_format_2)
			worksheet.merge_range('E36:F36',var_name['total_umum_THR'],content_format_3)
			worksheet.merge_range('C37:D37','TOTAL',header_format_2)
			worksheet.merge_range('E37:F37','=SUM(E35:E36)',content_format_4)

			# File name
			filename = 'PAYMENT REQUEST_%s%s%s' % (month_string, year_string, '.xlsx')
			workbook.close()
			out = base64.encodebytes(fp.getvalue())
			self.write({'data': out})
			fp.close()

			url = "web/content/?model=" + self._name + "&id=" + str(self.id) + "&field=data&download=true&filename=" + filename
			result = {
				'name': 'PAYMENT REQUEST XLS',
				'type': 'ir.actions.act_url',
				'url': url,
				'target': 'download',
			}
			return result

	def action_generate_csv(self):	
		if self.report_type != 'csv':
			raise UserError('Silakan pilih Report yang sesuai')
		elif self.payroll_send_date == '':
			raise UserError('Pilih Send Date!')
		else:
			date_rec = datetime(int(self.current_year), int(self.month_selection), 20)
			month_string = date_rec.strftime("%b")
			year_string = date_rec.strftime("%y")
			now = datetime.now() + timedelta(hours=7)
			create_datetime = now.strftime("%Y/%m/%d_%H.%M.%S")
			paycheck_date = self.payroll_send_date.strftime("%Y%m%d")
			if self.jabatan == '20':
				employees = self.env['hr.employee'].search([('domestic_bank_id','!=',''),('no_rekening','!=',''),('joining_date','<=',date_rec)])
			elif self.jabatan in ('1','2','3','4','5'):
				employees = self.env['hr.employee'].search([('domestic_bank_id','!=',''),('no_rekening','!=',''),('jabatan','=',self.jabatan),('joining_date','<=',date_rec)])
			elif self.jabatan == '6':
				employees = self.env['hr.employee'].search([('domestic_bank_id','!=',''),('no_rekening','!=',''),('jabatan','in',('4','5')),('joining_date','<=',date_rec)])
			elif self.jabatan == '7':
				employees = self.env['hr.employee'].search([('domestic_bank_id','!=',''),('no_rekening','!=',''),('jabatan','in',('1','2','3')),('joining_date','<=',date_rec)])
			else:
				employees = self.env['hr.employee'].search([('domestic_bank_id','!=',''),('no_rekening','!=',''),('jabatan','in',('2','3')),('joining_date','<=',date_rec)])
			
			
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
				for rec in thp:
					rec_sum += int(0 if rec['total'] is None else rec['total'])

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
					for rec in thp_val:
						row_3.append(int(0 if rec['total'] is None else rec['total']))
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
				if self.jabatan == '1':
					csv_name = 'Payroll Direktur / Wakil Direktur'
				elif self.jabatan == '2':
					csv_name = 'Payroll Manager'
				elif self.jabatan == '3':
					csv_name = 'Payroll Supervisor'
				elif self.jabatan == '4':
					csv_name = 'Payroll Staff'
				elif self.jabatan == '5':
					csv_name = 'Payroll Operator'
				elif self.jabatan == '6':
					csv_name = 'Payroll Staff + Operator'
				elif self.jabatan == '7':
					csv_name = 'Payroll DIR + MNG + SPV'
				elif self.jabatan == '8':
					csv_name = 'Payroll MNG + SPV'
				else : 
					csv_name = 'Payroll Seluruh Karyawan'
				
				filename = '%s %s%s%s' % (csv_name,month_string,year_string,'.csv')

				self.csv_data = base64.encodestring(data)
				url = "web/content/?model=" + self._name + "&id=" + str(self.id) + "&field=csv_data&download=true&filename=" + filename
				result = {
					'name': 'BNI Direct CSV',
					'type': 'ir.actions.act_url',
					'url': url,
					'target': 'download',
				}
				return result

# end
    
