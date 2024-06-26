from odoo import api, fields, models, _
import time
from datetime import datetime
import csv
from odoo.modules import get_modules, get_module_path
from odoo.exceptions import UserError
import codecs

class efaktur_pk_wizard(models.TransientModel):
    _name = 'vit.efaktur_pk'

    # @api.multi
    def confirm_button(self):
        """
        export pk yang is_efaktur_exported = False
        update setelah export
        :return: 
        """
        cr = self.env.cr

        headers = [
            'FK',
            'KD_JENIS_TRANSAKSI',
            'FG_PENGGANTI',
            'NOMOR_FAKTUR',
            'MASA_PAJAK',
            'TAHUN_PAJAK',
            'TANGGAL_FAKTUR',
            'NPWP',
            'NAMA',
            'ALAMAT_LENGKAP',
            'JUMLAH_DPP',
            'JUMLAH_PPN',
            'JUMLAH_PPNBM',
            'ID_KETERANGAN_TAMBAHAN',
            'FG_UANG_MUKA',
            'UANG_MUKA_DPP',
            'UANG_MUKA_PPN',
            'UANG_MUKA_PPNBM',
            'REFERENSI'
        ]


        mpath = get_module_path('tj_vit_efaktur')
        csvfile = open(mpath + '/static/fpk.csv', 'w')
        # csvfile = open('/home/tanjung/efaktur/fpk.csv', 'w')
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow([h.upper() for h in headers])

        onv_obj = self.env['account.move']  
        invoices = onv_obj.search([('is_efaktur_exported','=',False),
                                   ('state','=','posted'),
                                   ('efaktur_id','!=', False),
                                   ('move_type','=','out_invoice')])

        company = self.env.user.company_id.partner_id

        i=0
        self.baris2(headers, csvwriter)
        self.baris3(headers, csvwriter)

        for invoice in invoices:
            self.baris4(headers, csvwriter, invoice)
            self.baris5(headers, csvwriter, company )

            for line in invoice.invoice_line_ids:
                self.baris6(headers, csvwriter, line)

            invoice.is_efaktur_exported=True
            invoice.date_efaktur_exported=time.strftime("%Y-%m-%d %H:%M:%S")
            # invoice.date_efaktur_exported=time.strftime("%d-%m-%Y %H:%M:%S")
            i+=1

        cr.commit()
        csvfile.close()

        raise UserError("Export %s record(s) Done!" % i)

    def baris2(self, headers, csvwriter):
        data = {
            'FK': 'LT',
            'KD_JENIS_TRANSAKSI': 'NPWP',
            'FG_PENGGANTI': 'NAMA',
            'NOMOR_FAKTUR': 'JALAN',
            'MASA_PAJAK': 'BLOK',
            'TAHUN_PAJAK': 'NOMOR',
            'TANGGAL_FAKTUR': 'RT',
            'NPWP': 'RW',
            'NAMA': 'KECAMATAN',
            'ALAMAT_LENGKAP': 'KELURAHAN',
            'JUMLAH_DPP': 'KABUPATEN',
            'JUMLAH_PPN': 'PROPINSI',
            'JUMLAH_PPNBM': 'KODE_POS',
            'ID_KETERANGAN_TAMBAHAN': 'NOMOR_TELEPON',
            'FG_UANG_MUKA': '',
            'UANG_MUKA_DPP': '',
            'UANG_MUKA_PPN': '',
            'UANG_MUKA_PPNBM': '',
            'REFERENSI': ''
        }
        csvwriter.writerow([data[v] for v in headers])

    def baris3(self, headers, csvwriter):
        data = {
            'FK': 'OF',
            'KD_JENIS_TRANSAKSI': 'KODE_OBJEK',
            'FG_PENGGANTI': 'NAMA',
            'NOMOR_FAKTUR': 'HARGA_SATUAN',
            'MASA_PAJAK': 'JUMLAH_BARANG',
            'TAHUN_PAJAK': 'HARGA_TOTAL',
            'TANGGAL_FAKTUR': 'DISKON',
            'NPWP': 'DPP',
            'NAMA': 'PPN',
            'ALAMAT_LENGKAP': 'TARIF_PPNBM',
            'JUMLAH_DPP': 'PPNBM',
            'JUMLAH_PPN': '',
            'JUMLAH_PPNBM': '',
            'ID_KETERANGAN_TAMBAHAN': '',
            'FG_UANG_MUKA': '',
            'UANG_MUKA_DPP': '',
            'UANG_MUKA_PPN': '',
            'UANG_MUKA_PPNBM': '',
            'REFERENSI': ''
        }
        csvwriter.writerow([data[v] for v in headers])


    def baris4(self, headers, csvwriter, inv):

        if not inv.partner_id.npwp:
            raise UserError("Harap masukkan NPWP Customer %s" % inv.partner_id.name)

        if not inv.efaktur_id:
            raise UserError("Harap masukkan Nomor Seri Faktur Pajak Keluaran Invoice Nomor %s" % inv.number)

        # yyyy-mm-dd to dd/mm/yyyy

        # d  = inv.invoice_date.split("-")
        date_invoice = datetime.strptime(datetime.strftime(inv.invoice_date,'%Y/%m/%d'),'%Y/%m/%d')
        # date_invoice = datetime.strptime(datetime.strftime(inv.invoice_date,'%d/%m/%Y'),'%d/%m/%Y')
        # date_invoice = "%s/%s/%s" %(d[2],d[1],d[0])
        npwp = inv.partner_id.npwp.replace(".","").replace("-","")
        # nik = inv.partner_id.nik.replace(".","").replace("-","")
        faktur = inv.efaktur_id.name.replace(".","").replace("-","")

        data = {
            'FK': 'FK',
            # 'KD_JENIS_TRANSAKSI': str(inv.kode_faktur_pajak_id.kode),
            'KD_JENIS_TRANSAKSI': "01",
            'FG_PENGGANTI': '01',
            'NOMOR_FAKTUR': faktur,
            'MASA_PAJAK': inv.masa_pajak or '',
            'TAHUN_PAJAK': inv.tahun_pajak or '',
            'TANGGAL_FAKTUR': date_invoice.strftime('%d/%m/%Y'),
            'NPWP': npwp,
            'NAMA': inv.partner_id.name or '',
            'ALAMAT_LENGKAP': inv.partner_id.alamat_lengkap or '',
            # 'JUMLAH_DPP': float("{0:.2f}".format(inv.amount_untaxed)) or 0,
            'JUMLAH_DPP': int(inv.amount_untaxed) or 0,
            # 'JUMLAH_PPN': float("{0:.2f}".format(inv.amount_tax)) or 0,
            'JUMLAH_PPN': int(inv.amount_tax) or 0,
            'JUMLAH_PPNBM': 0,
            'ID_KETERANGAN_TAMBAHAN': '',
            'FG_UANG_MUKA': 0,
            'UANG_MUKA_DPP': 0,
            'UANG_MUKA_PPN': 0,
            'UANG_MUKA_PPNBM': 0,
            'REFERENSI': inv.partner_id.name or ''
        }
        csvwriter.writerow([data[v] for v in headers])

    def baris5(self, headers, csvwriter, company):
        data = {
            'FK': 'FAPR',
            'KD_JENIS_TRANSAKSI': company.name,
            'FG_PENGGANTI': company.alamat_lengkap,
            'NOMOR_FAKTUR': '',
            'MASA_PAJAK': '',
            'TAHUN_PAJAK': '',
            'TANGGAL_FAKTUR': '',
            'NPWP': '',
            'NAMA': '',
            'ALAMAT_LENGKAP': '',
            'JUMLAH_DPP': '',
            'JUMLAH_PPN': '',
            'JUMLAH_PPNBM': '',
            'ID_KETERANGAN_TAMBAHAN': '',
            'FG_UANG_MUKA': '',
            'UANG_MUKA_DPP': '',
            'UANG_MUKA_PPN': '',
            'UANG_MUKA_PPNBM': '',
            'REFERENSI': ''
        }
        csvwriter.writerow([data[v] for v in headers])

    def baris6(self, headers, csvwriter, line):        
        harga_total = float("{0:.2f}".format(line.price_unit * line.quantity/1.1))
        dpp = float("{0:.2f}".format(harga_total))
        ppn = float("{0:.2f}".format(dpp*0.1)) #TODO ambil dari Tax many2many

        product_name = ''
        product_name += ' '
        if line.product_id.name :
            product_name += line.product_id.name
    
        product_name += ' '
        if line.warna:
            product_name += line.warna

        data = {
            'FK': 'OF',
            'KD_JENIS_TRANSAKSI': line.product_id.default_code or '',
            'FG_PENGGANTI': product_name,
            'NOMOR_FAKTUR': float("{0:.2f}".format(line.price_unit/1.1)),
            'MASA_PAJAK': line.quantity ,
            'TAHUN_PAJAK': harga_total,
            'TANGGAL_FAKTUR': line.discount or 0,
            'NPWP': dpp,
            'NAMA': ppn,
            'ALAMAT_LENGKAP': '0',
            'JUMLAH_DPP': '0',
            'JUMLAH_PPN': '',
            'JUMLAH_PPNBM': '',
            'ID_KETERANGAN_TAMBAHAN': '',
            'FG_UANG_MUKA': '',
            'UANG_MUKA_DPP': '',
            'UANG_MUKA_PPN': '',
            'UANG_MUKA_PPNBM': '',
            'REFERENSI': ''
        }
        csvwriter.writerow([data[v] for v in headers])

