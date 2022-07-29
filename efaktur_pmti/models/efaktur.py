import base64
import re
import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.modules import get_modules, get_module_path
import csv


FK_HEAD_LIST = ['FK', 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR', 'MASA_PAJAK', 'TAHUN_PAJAK', 'TANGGAL_FAKTUR', 'NPWP', 'NAMA', 'ALAMAT_LENGKAP', 'JUMLAH_DPP', 'JUMLAH_PPN', 'JUMLAH_PPNBM', 'ID_KETERANGAN_TAMBAHAN', 'FG_UANG_MUKA', 'UANG_MUKA_DPP', 'UANG_MUKA_PPN', 'UANG_MUKA_PPNBM', 'REFERENSI']

LT_HEAD_LIST = ['LT', 'NPWP', 'NAMA', 'JALAN', 'BLOK', 'NOMOR', 'RT', 'RW', 'KECAMATAN', 'KELURAHAN', 'KABUPATEN', 'PROPINSI', 'KODE_POS', 'NOMOR_TELEPON']

OF_HEAD_LIST = ['OF', 'KODE_OBJEK', 'NAMA', 'HARGA_SATUAN', 'JUMLAH_BARANG', 'HARGA_TOTAL', 'DISKON', 'DPP', 'PPN', 'TARIF_PPNBM', 'PPNBM']


def _csv_row(data, delimiter=',', quote='"'):
	return quote + (quote + delimiter + quote).join([str(x).replace(quote, '\\' + quote) for x in data]) + quote + '\n'
	
class pmti_efaktur_pk_wizard(models.TransientModel):
	_inherit = 'vit.efaktur_pk'

	# company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
	attachment_id	= fields.Many2one('ir.attachment', string='file id', copy=False)
	attachment_name	= fields.Char(string='file name', related='attachment_id.name')

	def confirm_button_pmti(self):
		invoices = self.env['account.move'].search([
			('is_efaktur_exported','=',False), 
			('state','=','posted'), 
			('efaktur_id','!=', False), 
			('move_type','=','out_invoice')
			])			

		self._generate_efaktur(',', invoices)
		# return self.download_csv(attachment)

	def download_csv(self):
		action = {
			'type': 'ir.actions.act_url',
			'url': "web/content/?model=ir.attachment&id="+str(self.attachment_id.id)+"&filename_field=name&field=datas&download=true&name="+str(self.attachment_id.name),
			'target': 'self'
			}
		return action

	def _generate_efaktur(self, delimiter, invoices):
		output_head = self._generate_efaktur_invoice(delimiter, invoices)
		my_utf8 = output_head.encode("utf-8")
		out = base64.b64encode(my_utf8)

		# attachment = self.env['ir.attachment'].create({
		attachment = self.attachment_id.create({			
			'datas': out,
			'name': 'efaktur_%s.csv' % (fields.Datetime.to_string(fields.Datetime.now()).replace(" ", "_")),
			'type': 'binary',
			})

		i=0
		for record in invoices:
			record.message_post(attachment_ids=[attachment.id])
			record.efaktur_attachment_id = attachment.id
			record.is_efaktur_exported = True
			record.date_efaktur_exported=time.strftime("%Y-%m-%d %H:%M:%S")
			i+=1

		# if i>0:
		# 	raise Warning("Export %s record(s) Done!" % i)

		# for rec in self:
		# 	if not rec.attachment_id:
		# 		raise UserError("Data Kosong %s")

		return {
			'type': 'ir.actions.client',
			'tag': 'reload',
		}		
		return self.download_csv()

	def _generate_efaktur_invoice(self, delimiter, invoices):
		# company_id = self.env.user.company_id.id
		dp_product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
		output_head = '%s%s%s' % (
			_csv_row(FK_HEAD_LIST, delimiter),
			_csv_row(LT_HEAD_LIST, delimiter),
			_csv_row(OF_HEAD_LIST, delimiter),
			)

		# invoices = self.env['account.move'].search([
		# 	('is_efaktur_exported','=',False), 
		# 	('state','=','posted'), 
		# 	('efaktur_id','!=', False), 
		# 	('move_type','=','out_invoice')
		# 	])

		for move in invoices:
			if not move.partner_id.npwp:
				raise UserError("Harap masukkan NPWP Customer %s" % move.partner_id.name)

			if not move.efaktur_id:
				raise UserError("Harap masukkan Nomor Seri Faktur Pajak Keluaran Invoice Nomor %s" % move.payment_reference)

			eTax = self._prepare_etax()
			nik = str(move.partner_id.mobile) if not move.partner_id.npwp else ''
			# l10n_id_tax_number = '011%s' % (rep_efaktur_str[3:])
			if move.payment_reference:
				number_ref = str(move.payment_reference) + " " + nik
			street = ', '.join([x for x in (move.partner_id.street, move.partner_id.street2) if x])

			partner_npwp = '000000000000000'
			if move.partner_id.npwp and len(move.partner_id.npwp) >= 15:
				partner_npwp = move.partner_id.npwp
			elif (not move.partner_id.npwp or len(move.partner_id.npwp) < 15) and move.partner_id.mobile:
				partner_npwp = nik

			partner_npwp = partner_npwp.replace('.', '').replace('-', '')
			faktur_no = move.efaktur_id.name.replace(".","").replace("-","")


			eTax['KD_JENIS_TRANSAKSI'] 		= '07' if move.set_berikat == True else '01'
			eTax['FG_PENGGANTI'] 			= '01'
			eTax['NOMOR_FAKTUR'] 			= faktur_no
			eTax['MASA_PAJAK'] 				= move.masa_pajak or ''
			eTax['TAHUN_PAJAK'] 			= move.tahun_pajak or ''
			eTax['TANGGAL_FAKTUR'] 			= '{0}/{1}/{2}'.format(move.invoice_date.day, move.invoice_date.month, move.invoice_date.year)
			eTax['NPWP'] 					= partner_npwp
			eTax['NAMA'] 					= move.partner_id.name or ''
			eTax['ALAMAT_LENGKAP'] 			= move.partner_id.alamat_lengkap or ''
			# eTax['JUMLAH_DPP'] 				= int(round(move.amount_untaxed, 0)) or 0
			eTax['JUMLAH_DPP'] 				= int(move.amount_untaxed) or 0
			# eTax['JUMLAH_PPN'] 				= int(round(move.amount_tax, 0)) or 0
			eTax['JUMLAH_PPN'] 				= int(move.amount_tax) or 0
			eTax['ID_KETERANGAN_TAMBAHAN'] 	= '1' if move.set_berikat == True else ''
			eTax['REFERENSI'] 				= move.partner_id.name or number_ref
			# Uang Muka
			dp_lines = move.line_ids.filtered(lambda x: x.product_id.id == int(dp_product_id) and x.price_unit < 0 and not x.display_type)
			eTax['FG_UANG_MUKA'] 			= 0
			# eTax['UANG_MUKA_DPP'] 			= int(abs(sum(dp_lines.mapped('price_subtotal'))))
			eTax['UANG_MUKA_DPP'] 			= 0
			# eTax['UANG_MUKA_PPN'] 			= int(abs(sum(dp_lines.mapped(lambda l: l.price_total - l.price_subtotal))))
			eTax['UANG_MUKA_PPN'] 			= 0

			company_npwp			= ''
			# move.company_id.partner_id.vat or '000000000000000'
			fk_values_list 			= ['FK'] + [eTax[f] for f in FK_HEAD_LIST[1:]]
			# eTax['JALAN']			= move.company_id.partner_id.alamat_lengkap or move.company_id.partner_id.street
			eTax['JALAN']			= ''
			# eTax['NOMOR_TELEPON'] 	= move.company_id.partner_id.phone or ''
			eTax['NOMOR_TELEPON'] 	= ''
			# lt_values_list 			= ['FAPR', company_npwp, move.company_id.name] + [eTax[f] for f in LT_HEAD_LIST[3:]]
			lt_values_list 			= ['FAPR', '', ''] + [eTax[f] for f in LT_HEAD_LIST[3:]]

			free, sales 			= [], []

			for line in move.line_ids.filtered(lambda l: not l.exclude_from_invoice_tab and not l.display_type):
				# *invoice_line_unit_price is price unit use for harga_satuan's column
				# *invoice_line_quantity is quantity use for jumlah_barang's column
				# *invoice_line_total_price is bruto price use for harga_total's column
				# *invoice_line_discount_m2m is discount price use for diskon's column
				# *line.price_subtotal is subtotal price use for dpp's column
				# *tax_line or free_tax_line is tax price use for ppn's column
				free_tax_line = tax_line = bruto_total = total_discount = 0.0

				for tax in line.tax_ids:
					if tax.amount > 0:
						tax_line += line.price_subtotal * (tax.amount / 100.0)

				# invoice_line_unit_price 	= line.price_unit
				# invoice_line_total_price 	= invoice_line_unit_price * line.quantity
				invoice_line_unit_price 	= line.price_unit / 1.1
				invoice_line_total_price 	= invoice_line_unit_price * line.quantity

				if line.warna:
					invoice_line_barang = line.product_id.name + ' No. ' + line.warna
				
				line_dict = {
					'KODE_OBJEK'	: line.product_id.default_code or '',
					# 'NAMA'			: line.product_id.name or '',
					'NAMA'			: invoice_line_barang or '',
					'JUMLAH_BARANG'	: line.quantity,
					# 'HARGA_SATUAN'	: int(round(invoice_line_unit_price, 2)) or 0,
					# 'HARGA_TOTAL'	: int(round(invoice_line_total_price, 2)),
					# 'DPP'			: int(line.price_subtotal) or 0,
					'HARGA_SATUAN'	: round(invoice_line_unit_price, 2) or 0,
					'HARGA_TOTAL'	: round(invoice_line_total_price, 2) or 0,					
					'DPP'			: round(line.price_subtotal, 2) or 0,
					'product_id'	: line.product_id.id,
				}

				if line.price_subtotal < 0:
					for tax in line.tax_ids:
						free_tax_line += (line.price_subtotal * (tax.amount / 100.0)) * -1.0

					line_dict.update({
						'DISKON': int(invoice_line_total_price - line.price_subtotal),
						# 'PPN': int(free_tax_line),
						'PPN': round(free_tax_line, 2) or 0,
					})

					free.append(line_dict)

				elif line.price_subtotal != 0.0:
					invoice_line_discount_m2m = invoice_line_total_price - line.price_subtotal
					line_dict.update({
						'DISKON': int(invoice_line_discount_m2m),
						# 'PPN': int(tax_line),
						'PPN': round(tax_line, 2) or 0,
					})
					sales.append(line_dict)

			sub_total_before_adjustment = sub_total_ppn_before_adjustment = 0.0

			# We are finding the product that has affected
			# by free product to adjustment the calculation
			# of discount and subtotal.
			# - the price total of free product will be
			# included as a discount to related of product.

			for sale in sales:
				for f in free:
					if f['product_id'] == sale['product_id']:
						sale['DISKON'] = sale['DISKON'] - f['DISKON'] + f['PPN']
						sale['DPP'] = sale['DPP'] + f['DPP']
						tax_line = 0

						for tax in line.tax_ids:
							if tax.amount > 0:
								tax_line += sale['DPP'] * (tax.amount / 100.0)
						sale['PPN'] = int(tax_line)
						free.remove(f)

				sub_total_before_adjustment += sale['DPP']
				sub_total_ppn_before_adjustment += sale['PPN']
				bruto_total += sale['DISKON']
				total_discount += round(sale['DISKON'], 2)

			output_head += _csv_row(fk_values_list, delimiter)
			output_head += _csv_row(lt_values_list, delimiter)

			for sale in sales:
				of_values_list = ['OF'] + [str(sale[f]) for f in OF_HEAD_LIST[1:-2]] + ['0', '0']
				output_head += _csv_row(of_values_list, delimiter)

		return output_head


	def _prepare_etax(self):
		return {'JUMLAH_PPNBM': 0, 'UANG_MUKA_PPNBM': 0, 'BLOK': '', 'NOMOR': '', 'RT': '', 'RW': '', 'KECAMATAN': '', 'KELURAHAN': '', 'KABUPATEN': '', 'PROPINSI': '', 'KODE_POS': '', 'JUMLAH_BARANG': 0, 'TARIF_PPNBM': 0, 'PPNBM': 0}

		
	# def confirm_button_pmti(self):
		# cr = self.env.cr


		# headers = [
		# 	'FK',
		# 	'KD_JENIS_TRANSAKSI',
		# 	'FG_PENGGANTI',
		# 	'NOMOR_FAKTUR',
		# 	'MASA_PAJAK',
		# 	'TAHUN_PAJAK',
		# 	'TANGGAL_FAKTUR',
		# 	'NPWP',
		# 	'NAMA',
		# 	'ALAMAT_LENGKAP',
		# 	'JUMLAH_DPP',
		# 	'JUMLAH_PPN',
		# 	'JUMLAH_PPNBM',
		# 	'ID_KETERANGAN_TAMBAHAN',
		# 	'FG_UANG_MUKA',
		# 	'UANG_MUKA_DPP',
		# 	'UANG_MUKA_PPN',
		# 	'UANG_MUKA_PPNBM',
		# 	'REFERENSI'
		# ]



		# mpath = get_module_path('efaktur_pmti')
		# csvfile = open(mpath + '/static/fpk.csv', 'w')
		# csvwriter = csv.writer(csvfile, delimiter=',')
		# csvwriter.writerow([h.upper() for h in headers])
		
		# company = self.env.user.company_id.partner_id
		# i=0
		# self.baris2(headers, csvwriter)
		# self.baris3(headers, csvwriter)


		# output_head = self._generate_efaktur_invoice(delimiter)
		# my_utf8 = csvfile.encode("utf-8")
		# out = base64.b64encode(my_utf8)

		# attachment = self.env['ir.attachment'].create({
		# 	'datas': csvwriter,
		# 	'name': 'fpk_%s.csv' % (fields.Datetime.to_string(fields.Datetime.now()).replace(" ", "_")),
		# 	'type': 'binary',
		# })

		# for invoice in invoices:
		# 	self.baris4(headers, csvwriter, invoice)
		# 	self.baris5(headers, csvwriter, company )
		# 	invoice.efaktur_attachment_id = attachment.id
		# 	invoice.message_post(attachment_ids=[attachment.id])
		# 	invoice.date_efaktur_exported=time.strftime("%Y-%m-%d %H:%M:%S")
		# 	invoice.is_efaktur_exported=True
		# 	for line in invoice.invoice_line_ids:
		# 		self.baris6(headers, csvwriter, line)		
		# 	i+=1

		# return {
		# 	'type': 'ir.actions.client',
		# 	'tag': 'reload',
		# }

		# cr.commit()
		# csvfile.close()
		# raise UserError("Export %s record(s) Done!" % i)

class AccountMove(models.Model):
	_inherit = "account.move"

	efaktur_attachment_id	= fields.Many2one('ir.attachment', readonly=True, copy=False)
	set_berikat				= fields.Boolean('Cust Kawasan Berikat', default=False, copy=False)