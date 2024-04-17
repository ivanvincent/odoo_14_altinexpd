from odoo import fields, models, api, _
from odoo.exceptions import UserError
from io import BytesIO
import base64
import xlsxwriter
from datetime import datetime
from . import add_workbook_format as awf

class LaporanPenjualanWizard(models.TransientModel):
    _name = 'laporan.penjualan.wizard'

    type = fields.Selection([("laporan_penjualan","Laporan Penjualan"),("lp_grade_a","Laporan Penjualan Grade A"), ("lp_sakura", "Laporan Penjualan (Format Sakura)")], string='Type', required=True, )
    date_start = fields.Date(string='Date Start', required=True, )
    date_end = fields.Date(string='Date End', required=True, )
    data = fields.Binary(string='data')

    def action_generate_xslx(self):
        if self.type == 'laporan_penjualan':
            query = """
                select 
                    am.name as kd_keluar,
                    am.invoice_date,
                    rp.name as customer,
                    ppl.name as nama_barang,
                    aml.warna,
                    1 as jumlah,
                    aml.quantity,
                    aml.price_unit as harga_satuan,
                    (aml.price_unit * aml.quantity) as harga_faktur
                from account_move_line as aml
                    left join account_move am on aml.move_id = am.id
                    left join res_partner rp on am.partner_id = rp.id
                    left join product_product pp on pp.id = aml.product_id
                    left join product_template ppl on ppl.id = pp.product_tmpl_id
                where am.journal_id = 36 and
                    am.move_type = 'out_invoice'
                    and state = 'posted'
                    and account_id in (10858, 10862, 11926, 10859)
                    and am.invoice_date between '%s' and '%s'
            """ % (self.date_start, self.date_end)
            self._cr.execute(query)
            rslt = self._cr.dictfetchall()
            fp = BytesIO()
            date_string = datetime.now().strftime("%Y-%m-%d")
            workbook = xlsxwriter.Workbook(fp)
            wbf, workbook = awf.add_workbook_format(workbook)

            # WKS 1
            report_name = 'LAPORAN PENJUALAN'
            worksheet = workbook.add_worksheet(report_name)        
            
            worksheet.set_column('A6:A6', 3)
            worksheet.set_column('B6:B6', 35)
            worksheet.set_column('C6:C6', 15)
            worksheet.set_column('D6:D6', 35)
            worksheet.set_column('E6:E6', 35)
            worksheet.set_column('F6:F6', 10)
            worksheet.set_column('G6:G6', 10)
            worksheet.set_column('H6:H6', 10)
            worksheet.set_column('I6:I6', 15)
            worksheet.set_column('J6:J6', 15)
            # WKS 1

            worksheet.merge_range('A2:J2', report_name , wbf['merge_format'])
            worksheet.merge_range('A3:J3', 'PERIODE (' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format_2'])
            worksheet.merge_range('A4:J4', '' , wbf['merge_format'])

            row = 6
            worksheet.write('A%s' % (row), 'No', wbf['header'])
            worksheet.write('B%s' % (row), 'NO INVOICE', wbf['header'])
            worksheet.write('C%s' % (row), 'TANGGAL', wbf['header'])
            worksheet.write('D%s' % (row), 'CUSTOMER', wbf['header'])
            worksheet.write('E%s' % (row), 'NAMA BARANG', wbf['header'])
            worksheet.write('F%s' % (row), 'WARNA', wbf['header'])
            worksheet.write('G%s' % (row), 'JUMLAH', wbf['header'])
            worksheet.write('H%s' % (row), 'QUANTITY', wbf['header'])
            worksheet.write('I%s' % (row), 'HARGA SATUAN', wbf['header'])
            worksheet.write('J%s' % (row), 'HARGA FAKTUR', wbf['header'])

            row += 1
            
            no = 1
            for rec in rslt:

                worksheet.write('A%s' % (row), no, wbf['content_number_center'])
                worksheet.write('B%s' % (row), rec.get('kd_keluar', ''), wbf['content_center'])
                worksheet.write('C%s' % (row), rec.get('invoice_date', '').strftime('%Y-%m-%d'), wbf['content_center'])
                worksheet.write('D%s' % (row), rec.get('customer', ''), wbf['content_center'])
                worksheet.write('E%s' % (row), rec.get('nama_barang', ''), wbf['content_center'])
                worksheet.write('F%s' % (row), rec.get('warna', ''), wbf['content_center'])
                worksheet.write('G%s' % (row), rec.get('jumlah', ''), wbf['content_number'])
                worksheet.write('H%s' % (row), rec.get('quantity', ''), wbf['content_number'])
                worksheet.write('I%s' % (row), rec.get('harga_satuan', ''), wbf['content_number'])
                worksheet.write('J%s' % (row), rec.get('harga_faktur', ''), wbf['content_number'])

                no += 1
                row += 1

            filename = '%s %s%s' % (report_name, date_string, '.xlsx')
            workbook.close()
            out = base64.encodestring(fp.getvalue())
            self.write({'data': out})
            fp.close()

            self.write({'data': out})
            url = "web/content/?model=" + self._name + "&id=" + str(self.id) + "&field=data&download=true&filename=" + filename
            result = {
                'name': 'Laporan Penjualan Pmti XLSX',
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'download',
            }
            return result
        elif self.type == 'lp_grade_a':
            query = """
                select
                    ppl.name, sum(quantity) as qty, uu.name as uom, sum(price_total) as rp
                from account_move_line aml
                    left join account_move am on am.id = aml.move_id
                    left join product_product pp on pp.id = aml.product_id
                    left join product_template ppl on ppl.id = pp.product_tmpl_id
					left join uom_uom uu on uu.id = aml.product_uom_id
                where aml.account_id = 10858
                    and am.invoice_date BETWEEN '%s' and '%s'
                group by ppl.name, uu.name
            """ % (self.date_start, self.date_end)
            self._cr.execute(query)
            rslt = self._cr.dictfetchall()
            fp = BytesIO()
            date_string = datetime.now().strftime("%Y-%m-%d")
            workbook = xlsxwriter.Workbook(fp)
            wbf, workbook = awf.add_workbook_format(workbook)

            # WKS 1
            report_name = 'LAPORAN PENJUALAN GRADE A'
            worksheet = workbook.add_worksheet(report_name)        
            
            worksheet.set_column('B2:B2', 35)
            worksheet.set_column('C2:C2', 35)
            worksheet.set_column('D2:D2', 35)
            worksheet.set_column('E2:E2', 35)

            # WKS 1

            worksheet.merge_range('B2:E2', report_name , wbf['merge_format'])
            worksheet.merge_range('B3:E3', 'PERIODE (' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format_2'])

            row = 6
            worksheet.write('B%s' % (row), 'NAMA BARANG', wbf['header'])
            worksheet.write('C%s' % (row), 'QUANTITY', wbf['header'])
            worksheet.write('D%s' % (row), 'UOM', wbf['header'])
            worksheet.write('E%s' % (row), 'RP', wbf['header'])

            row += 1
            
            no = 1
            for rec in rslt:

                worksheet.write('B%s' % (row), rec.get('name', ''), wbf['content'])
                worksheet.write('C%s' % (row), rec.get('qty', ''), wbf['content_number'])
                worksheet.write('D%s' % (row), rec.get('uom', ''), wbf['content_number'])
                worksheet.write('E%s' % (row), rec.get('rp', ''), wbf['content_number'])

                no += 1
                row += 1

            worksheet.write('B%s' % (row), '', wbf['header'])
            worksheet.write('C%s' % (row), '', wbf['header'])
            worksheet.write('D%s' % (row), 'TOTAL', wbf['header'])
            worksheet.write('E%s' % (row), '=SUM(E7:E%s)' % str(row-1), wbf['content_number'])
            filename = '%s %s%s' % (report_name, date_string, '.xlsx')
            workbook.close()
            out = base64.encodestring(fp.getvalue())
            self.write({'data': out})
            fp.close()

            self.write({'data': out})
            url = "web/content/?model=" + self._name + "&id=" + str(self.id) + "&field=data&download=true&filename=" + filename
            result = {
                'name': 'Laporan Penjualan Grade A XLSX',
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'download',
            }
            return result
        elif self.type == 'lp_sakura':
            query = """
                select
                    customer,
                    total_grade_a,
                    total_grade_b,
                    total_grade_c,
                    ppl,
                    (total_grade_a + total_grade_b + total_grade_c + ppl) as jumlah
                from (
                    select
                        rp.name as customer,
                        sum(aml.price_total) as total_grade_a,
                        0 as total_grade_b,
                        0 as total_grade_c,
                        0 as ppl
                    from account_move_line aml 
                        left join account_move am on am.id = aml.move_id
                        left join res_partner rp on rp.id = am.partner_id
                    where 
                        aml.account_id = 10858
                        and am.invoice_date between '%s' and '%s'
                    group by rp.name
                    
                    UNION
                    
                    select
                        rp.name as customer,
                        0 as total_grade_a,
                        sum(aml.price_total) as total_grade_b,
                        0 as total_grade_c,
                        0 as ppl
                    from account_move_line aml 
                        left join account_move am on am.id = aml.move_id
                        left join res_partner rp on rp.id = am.partner_id
                    where 
                        aml.account_id = 10859
                        and am.invoice_date between '%s' and '%s'
                    group by rp.name
                    
                    UNION
                    
                    select
                        rp.name as customer,
                        0 as total_grade_a,
                        0 as total_grade_b,
                        sum(aml.price_total) as total_grade_c,
                        0 as ppl
                    from account_move_line aml 
                        left join account_move am on am.id = aml.move_id
                        left join res_partner rp on rp.id = am.partner_id
                    where 
                        aml.account_id = 10860
                        and am.invoice_date between '%s' and '%s'
                    group by rp.name
                    
                    UNION
                    
                    select
                        rp.name as customer,
                        0 as total_grade_a,
                        0 as total_grade_b,
                        0 as total_grade_c,
                        sum(aml.price_total) as pll
                    from account_move_line aml 
                        left join account_move am on am.id = aml.move_id
                        left join res_partner rp on rp.id = am.partner_id
                    where 
                        aml.account_id = 11926
                        and am.invoice_date between '%s' and '%s'
                    group by rp.name
                ) un
            """ % (self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end)
            self._cr.execute(query)
            rslt = self._cr.dictfetchall()
            fp = BytesIO()
            date_string = datetime.now().strftime("%Y-%m-%d")
            workbook = xlsxwriter.Workbook(fp)
            wbf, workbook = awf.add_workbook_format(workbook)

            # WKS 1
            report_name = 'LAPORAN PENJUALAN PT. PMTI'
            worksheet = workbook.add_worksheet(report_name)        
            
            worksheet.set_column('A2:A2', 35)
            worksheet.set_column('B2:B2', 35)
            worksheet.set_column('C2:C2', 35)
            worksheet.set_column('D2:D2', 35)
            worksheet.set_column('E2:E2', 35)
            worksheet.set_column('F2:F2', 35)

            # WKS 1

            worksheet.merge_range('A1:F1', report_name , wbf['merge_format'])
            worksheet.merge_range('A2:F4', 'PERIODE (' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format_2'])

            row = 5
            worksheet.write('A%s' % (row), 'CUSTOMER', wbf['header'])
            worksheet.write('B%s' % (row), 'GRADE A', wbf['header'])
            worksheet.write('C%s' % (row), 'GRADE B', wbf['header'])
            worksheet.write('D%s' % (row), 'GRADE C', wbf['header'])
            worksheet.write('E%s' % (row), 'LAIN-LAIN', wbf['header'])
            worksheet.write('F%s' % (row), 'JUMLAH', wbf['header'])


            row += 1
            
            no = 1
            for rec in rslt:
                worksheet.write('A%s' % (row), rec.get('customer', ''), wbf['content'])
                worksheet.write('B%s' % (row), rec.get('total_grade_a', '') if rec.get('total_grade_a', '') else '' , wbf['content'])
                worksheet.write('C%s' % (row), rec.get('total_grade_b', '') if rec.get('total_grade_b', '') else '' , wbf['content'])
                worksheet.write('D%s' % (row), rec.get('total_grade_c', '') if rec.get('total_grade_c', '') else '' , wbf['content'])
                worksheet.write('E%s' % (row), rec.get('ppl', '') if rec.get('ppl', '') else '', wbf['content'])
                worksheet.write('F%s' % (row), rec.get('jumlah', '') if rec.get('jumlah', '') else '', wbf['content'])

                no += 1
                row += 1

            filename = '%s %s%s' % (report_name, date_string, '.xlsx')
            workbook.close()
            out = base64.encodestring(fp.getvalue())
            self.write({'data': out})
            fp.close()

            self.write({'data': out})
            url = "web/content/?model=" + self._name + "&id=" + str(self.id) + "&field=data&download=true&filename=" + filename
            result = {
                'name': 'Laporan Penjualan Grade A (Format Sakura) XLSX',
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'download',
            }
            return result


    def get_ppn(self, move_line_id, total):
        move_line_obj = self.env['account.move.line'].browse(move_line_id)
        return total + [total * (tax.amount / 100 )for tax in move_line_obj.tax_ids]
