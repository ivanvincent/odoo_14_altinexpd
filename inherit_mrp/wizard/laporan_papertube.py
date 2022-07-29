from odoo import fields, models, api, _
from odoo.exceptions import UserError
from . import add_workbook_format as awf
from io import BytesIO
import base64
import xlsxwriter
from datetime import datetime

class LaporanPapertubeWizard(models.TransientModel):
    _name = 'laporan.papertube'

    date_start = fields.Date(string='Date Start', default=fields.Date.today())
    date_end = fields.Date(string='Date End', default=fields.Date.today())
    data = fields.Binary(string='Data')

    def action_generate_excel(self):
        print('action_generate_excel')
        query = """
                select 
                    to_char(date_planned_start, 'YYYY-mm-dd') as date, product_id, sum(product_qty) as product_qty, sum(waste) as waste, hr.name as pegawai, mp.id as id
                from mrp_production as mp
                join hr_employee as hr
                    on mp.employee_id = hr.id
                where 
                    type_id = 7 
                    and date_planned_start between '%s' AND '%s'
                group by
                    date, product_id, hr.name, mp.id
        """ % (self.date_start, self.date_end)
        self._cr.execute(query)
        result = self._cr.dictfetchall()
        fp = BytesIO()
        date_string = datetime.now().strftime("%Y-%m-%d")
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = awf.add_workbook_format(workbook)

        # WKS 1
        report_name = 'LAPORAN PRODUKSI PAPERTUBE'
        worksheet = workbook.add_worksheet(report_name)        
        
        worksheet.set_column('A6:A6', 3)
        worksheet.set_column('B6:B6', 15)
        worksheet.set_column('C6:C6', 15)
        worksheet.set_column('D6:D6', 12)
        worksheet.set_column('E6:E6', 12)
        worksheet.set_column('F6:F6', 12)
        worksheet.set_column('G6:G6', 12)
        worksheet.set_column('H6:H6', 12)
        worksheet.set_column('I6:I6', 12)
        worksheet.set_column('J6:J6', 12)
        worksheet.set_column('K6:K6', 12)
        worksheet.set_column('L6:L6', 12)
        worksheet.set_column('M6:M6', 12)
        worksheet.set_column('N6:N6', 12)
        worksheet.set_column('O6:O6', 12)
        worksheet.set_column('P6:P6', 15)
        worksheet.set_column('Q6:Q6', 15)
        worksheet.set_column('R6:R6', 15)
        worksheet.set_column('S6:S6', 15)
        worksheet.set_column('T6:T6', 15)
        # WKS 1

        worksheet.merge_range('A2:T2', report_name , wbf['merge_format'])
        worksheet.merge_range('A3:T3', 'PERIODE (' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format_2'])
        worksheet.merge_range('A4:T4', '' , wbf['merge_format'])

        row = 6
        worksheet.write('A%s' % (row), 'No', wbf['header'])
        worksheet.write('B%s' % (row), 'DATE', wbf['header'])
        worksheet.write('C%s' % (row), 'WASTE (Kg)', wbf['header'])
        worksheet.write('D%s' % (row), '114 CM', wbf['header'])
        worksheet.write('E%s' % (row), 'KG (0.12)', wbf['header'])
        worksheet.write('F%s' % (row), '118 CM', wbf['header'])
        worksheet.write('G%s' % (row), 'KG (0.13)', wbf['header'])
        worksheet.write('H%s' % (row), '140 CM', wbf['header'])
        worksheet.write('I%s' % (row), 'KG (0.16)', wbf['header'])
        worksheet.write('J%s' % (row), '150 CM', wbf['header'])
        worksheet.write('K%s' % (row), 'KG (0.17)', wbf['header'])
        worksheet.write('L%s' % (row), '154 CM', wbf['header'])
        worksheet.write('M%s' % (row), 'KG (0.18)', wbf['header'])
        worksheet.write('N%s' % (row), '162 CM (3``)', wbf['header'])
        worksheet.write('O%s' % (row), 'KG (0.75)', wbf['header'])
        worksheet.write('P%s' % (row), 'Total Produksi', wbf['header'])
        worksheet.write('Q%s' % (row), 'Total Kg', wbf['header'])
        worksheet.write('R%s' % (row), 'Lost Produksi %', wbf['header'])
        worksheet.write('S%s' % (row), 'Bantalan Folding', wbf['header'])
        worksheet.write('T%s' % (row), 'Pegawai', wbf['header'])

        row += 1
        
        no = 1

        paper_114  = 34310
        papert_118 = 34311
        paper_140  = 34312
        paper_150  = 184993

        for rec in result:
            product_id = rec.get('product_id')
            product_qty = rec.get('product_qty', 0)


            worksheet.write('A%s' % (row), no, wbf['content_number_center'])
            worksheet.write('B%s' % (row), rec.get('date', ''), wbf['content_center'])
            worksheet.write('C%s' % (row), rec.get('waste', ''), wbf['content_number'])
            worksheet.write('D%s' % (row), product_qty if product_id == paper_114 else '', wbf['content_number'])
            worksheet.write('E%s' % (row), '', wbf['content_number'])
            worksheet.write('F%s' % (row), product_qty if product_id == papert_118 else '', wbf['content_number'])
            worksheet.write('G%s' % (row), '', wbf['content_number'])
            worksheet.write('H%s' % (row), product_qty if product_id == paper_140 else '', wbf['content_number'])
            worksheet.write('I%s' % (row), '', wbf['content_number'])
            worksheet.write('J%s' % (row), product_qty if product_id == paper_150 else '', wbf['content_number'])
            worksheet.write('K%s' % (row), '', wbf['content_number'])
            worksheet.write('L%s' % (row), '', wbf['content_number'])
            worksheet.write('M%s' % (row), '', wbf['content_number'])
            worksheet.write('N%s' % (row), '', wbf['content_number'])
            worksheet.write('O%s' % (row), '', wbf['content_number'])
            worksheet.write('P%s' % (row), '=SUM(D%s:O%s)' % (row,row), wbf['content_number'])
            worksheet.write('Q%s' % (row), '', wbf['content_number'])
            worksheet.write('R%s' % (row), '', wbf['content_number'])
            worksheet.write('S%s' % (row), '', wbf['content_number'])
            worksheet.write('T%s' % (row), rec.get('pegawai', ''), wbf['content_center'])
        
            no += 1
            row += 1

        # TOTAL
        worksheet.merge_range('A%s:B%s' % (row, row), 'TOTAL', wbf['foot_merge_format'])
        worksheet.write('C%s' % (row), '=SUM(C7:C%s)' % (row-1), wbf['total_float'])
        worksheet.write('D%s' % (row), '=SUM(D7:D%s)' % (row-1), wbf['total_float'])
        worksheet.write('E%s' % (row), '=SUM(E7:E%s)' % (row-1), wbf['total_float'])
        worksheet.write('F%s' % (row), '=SUM(F7:F%s)' % (row-1), wbf['total_float'])
        worksheet.write('G%s' % (row), '=SUM(G7:G%s)' % (row-1), wbf['total_float'])
        worksheet.write('H%s' % (row), '=SUM(H7:H%s)' % (row-1), wbf['total_float'])
        worksheet.write('I%s' % (row), '=SUM(I7:I%s)' % (row-1), wbf['total_float'])
        worksheet.write('J%s' % (row), '=SUM(J7:J%s)' % (row-1), wbf['total_float'])
        worksheet.write('K%s' % (row), '=SUM(K7:K%s)' % (row-1), wbf['total_float'])
        worksheet.write('L%s' % (row), '=SUM(L7:L%s)' % (row-1), wbf['total_float'])
        worksheet.write('M%s' % (row), '=SUM(M7:M%s)' % (row-1), wbf['total_float'])
        worksheet.write('N%s' % (row), '=SUM(N7:N%s)' % (row-1), wbf['total_float'])
        worksheet.write('O%s' % (row), '=SUM(O7:O%s)' % (row-1), wbf['total_float'])
        worksheet.write('P%s' % (row), '=SUM(P7:P%s)' % (row-1), wbf['total_float'])
        worksheet.write('Q%s' % (row), '=SUM(Q7:Q%s)' % (row-1), wbf['total_float'])
        worksheet.write('R%s' % (row), '=SUM(R7:R%s)' % (row-1), wbf['total_float'])
        worksheet.write('S%s' % (row), '=SUM(S7:S%s)' % (row-1), wbf['total_float'])
        worksheet.write('T%s' % (row), '', wbf['foot_center'])


        qty_kertas_chip = 0
        qty_kertas_paper_print = 0
        qty_aci = 0
        # kertas_chip = self.env['stock.move'].search([('raw_material_production_id','=',rec.get('id')),('product_id','=',29570)])
        sql = """select a.product_id as product_id, a.product_uom_qty as qty from stock_move a left join mrp_production b on a.raw_material_production_id = b.id where b.date_planned_start between '%s' AND '%s'"""%(self.date_start, self.date_end)
        self._cr.execute(sql)
        res_q = self._cr.dictfetchall()
        for res in res_q:
            qty_kertas_chip += res.get('qty') if res.get('product_id') == 29570 else 0 #KERTAS CHIP BOARD 350 GR
            qty_kertas_paper_print += res.get('qty') if res.get('product_id') == 56433 else 0 #KERTAS PAPER PRINT
            qty_aci += res.get('qty') if res.get('product_id') == 30841 else 0 #ACI / TEPUNG KANJI


        worksheet.merge_range('A%s:C%s' % (row+2, row+2), 'Pemakaian Kertas Medium', wbf['merge_format_2'])
        worksheet.write('D%s' % (row+2), 0, wbf['total_float'])
        worksheet.merge_range('A%s:C%s' % (row+3, row+3), 'Pemakaian Lem Putih', wbf['merge_format_2'])
        worksheet.write('D%s' % (row+3), 0, wbf['total_float'])
        worksheet.merge_range('A%s:C%s' % (row+4, row+4), 'Pemakaian Kertas Chipboard', wbf['merge_format_2'])
        worksheet.write('D%s' % (row+4), qty_kertas_chip, wbf['total_float'])
        worksheet.merge_range('A%s:C%s' % (row+5, row+5), 'Pemakaian Kertas Paper Print', wbf['merge_format_2'])
        worksheet.write('D%s' % (row+5), qty_kertas_paper_print, wbf['total_float'])
        worksheet.merge_range('A%s:C%s' % (row+6, row+6), 'Pemakaian ACI', wbf['merge_format_2'])
        worksheet.write('D%s' % (row+6), qty_aci, wbf['total_float'])
        worksheet.merge_range('A%s:D%s' % (row+7, row+7), 'Total Pemakaian', wbf['header'])
        worksheet.write('D%s' % (row+7), 0, wbf['total_float'])

        worksheet.merge_range('A%s:D%s' % (row+9, row+9), 'STOCK OPNAME BAHAN BAKU', wbf['header'])
        worksheet.merge_range('A%s:C%s' % (row+10, row+10), 'Saldo Kertas Medium', wbf['merge_format_2'])
        worksheet.write('D%s' % (row+10), 0, wbf['total_float'])
        worksheet.merge_range('A%s:C%s' % (row+11, row+11), 'Saldo Kertas Chip Board', wbf['merge_format_2'])
        worksheet.write('D%s' % (row+11), 0, wbf['total_float'])
        worksheet.merge_range('A%s:C%s' % (row+12, row+12), 'Saldo ACI', wbf['merge_format_2'])
        worksheet.write('D%s' % (row+12), 0, wbf['total_float'])



        filename = '%s %s%s' % (report_name, date_string, '.xlsx')
        workbook.close()
        out = base64.encodestring(fp.getvalue())
        self.write({'data': out})
        fp.close()

        self.write({'data': out})
        url = "web/content/?model=" + self._name + "&id=" + str(self.id) + "&field=data&download=true&filename=" + filename
        result = {
            'name': 'Laporan Mutasi Persediaan XLSX',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'download',
        }
        return result
