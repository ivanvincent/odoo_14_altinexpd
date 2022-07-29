from odoo import models, fields, api
from io import BytesIO
import base64
import xlsxwriter
from datetime import datetime
from . import add_workbook_format as awf

class MutasiPersedidaan(models.Model):
    _name = 'mutasi.persediaan'

    name = fields.Char(string='Name')
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')
    line_ids = fields.One2many('mutasi.persediaan.line', 'mutasi_persediaan_id', 'Line')
    data = fields.Binary(string='Data')

    def action_generate(self):
        columns = 'account_id, account, location_id, product_id, lok, saldo_awal, qty_start, penerimaan, qty_in, pengeluaran, qty_out, saldo_akhir, qty_balance, mutasi_persediaan_id'
        # -- DELETE FROM mutasi_persediaan_line where mutasi_persediaan_id = %s;
        start = self.date_start.strftime("%Y-%m-%d")
        end = self.date_end.strftime("%Y-%m-%d")
        print('date_start',start)
        print('date_end',end)
        persediaan_percent = 'Persediaan%'
        query = """
            DELETE FROM mutasi_persediaan_line where mutasi_persediaan_id = %s;

            INSERT INTO mutasi_persediaan_line (%s) (
            select 
                account_id, 
                account, 
                location_id, 
                product_id,
                lok, 
                sum(sa) as saldo_awal,
                sum(qty_start) as qty_start,
                sum(penerimaan) as penerimaan,
                sum(qty_in) as qty_in,
                sum(pengeluaran) as pngeluaran,
                sum(qty_out) as qty_out,
                sum(saldo_akhir) as saldo_akhir,
                sum(qty_start) + sum(qty_in) + sum(qty_out) as qty_balance,
                %s as mutasi_persediaan_id
                from 
                (
                    select 
                    a.account_id, 
                    b.name account, 
                    a.location_id, 
                    a.product_id,
                    c.name as lok, 
                    sum(debit - credit) as sa,
                    sum(a.quantity) as qty_start,
                    0 as penerimaan, 
                    0 as qty_in,
                    0 as pengeluaran, 
                    0 as qty_out,
                    sum(debit - credit) as saldo_akhir,
                    0 as qty_balance
                    from 
                    account_move_line a 
                    left join account_account b on a.account_id = b.id 
                    left join stock_location c on a.location_id = c.id
                    left join account_move d on a.move_id = d.id
                    where 
                    a.date < '%s'
                    and b.name like '%s'    
                    and d.state = 'posted'
                    group by 
                    a.account_id, 
                    b.name, 
                    a.location_id,
                    a.product_id,
                    c.name 
                    union 
                    select 
                    a.account_id, 
                    b.name account, 
                    a.location_id, 
                    a.product_id,
                    c.name as lok, 
                    0 as sa, 
                    0 as qty_start,
                    sum(debit - credit) as penerimaan, 
                    sum(a.quantity) as qty_in,
                    0 as pengeluaran, 
                    0 as qty_out,
                    sum(debit - credit) as saldo_akhir,
                    0 as qty_balance
                    from 
                    account_move_line a 
                    left join account_account b on a.account_id = b.id 
                    left join stock_location c on a.location_id = c.id
                    left join account_move d on a.move_id = d.id
                    where 
                    a.date between '%s' 
                    and '%s' 
                    and b.name like '%s' 
                    and a.debit > 0
                    and d.state = 'posted'
                    group by 
                    a.account_id, 
                    b.name, 
                    a.location_id, 
                    a.product_id,
                    c.name 
                    union 
                    select 
                    a.account_id, 
                    b.name account, 
                    a.location_id, 
                    a.product_id,
                    c.name as lok, 
                    0 as sa, 
                    0 as qty_start,
                    0 as penerimaan, 
                    0 as qty_in,
                    sum(debit - credit) as pengeluaran, 
                    sum(a.quantity) as qty_out,
                    sum(debit - credit) as saldo_akhir,
                    0 as qty_balance
                    from 
                    account_move_line a 
                    left join account_account b on a.account_id = b.id 
                    left join stock_location c on a.location_id = c.id
                    left join account_move d on a.move_id = d.id
                    where 
                    a.date between '%s' 
                    and '%s' 
                    and b.name like '%s' 
                    and a.credit > 0
                    and d.state = 'posted'
                    group by 
                    a.account_id, 
                    b.name, 
                    a.location_id,
                    a.product_id,
                    c.name
                ) as a 
                group by 
                account_id, 
                account, 
                location_id,
                product_id,
                lok
            )
            """ % (self.id, columns, self.id, start, persediaan_percent, start, end, persediaan_percent, start, end, persediaan_percent)
        self._cr.execute(query)

    def action_export_xlsx(self):
        print('action_export_xlsx')
        fp = BytesIO()
        date_string = datetime.now().strftime("%Y-%m-%d")
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = awf.add_workbook_format(workbook)

        # WKS 1
        report_name = 'LAPORAN MUTASI PERSEDIAAN %s' % (self.name)
        worksheet = workbook.add_worksheet(report_name)        
        
        worksheet.set_column('A6:A6', 3)
        worksheet.set_column('B6:B6', 14)
        worksheet.set_column('C6:C6', 15)
        worksheet.set_column('D6:D6', 15)
        worksheet.set_column('E6:E6', 15)
        worksheet.set_column('F6:F6', 15)
        worksheet.set_column('G6:G6', 40)
        # WKS 1

        worksheet.merge_range('A2:G2', report_name , wbf['merge_format'])
        worksheet.merge_range('A3:G3', 'PERIODE ' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format_2'])
        worksheet.merge_range('A4:G4', '' , wbf['merge_format'])

        row = 6
        worksheet.write('A%s' % (row), 'No', wbf['header'])
        worksheet.write('B%s' % (row), 'ACCOUNT', wbf['header'])
        worksheet.write('C%s' % (row), 'LOCATION', wbf['header'])
        worksheet.write('D%s' % (row), 'SALDO AWAL', wbf['header'])
        worksheet.write('E%s' % (row), 'PENERIMAAN', wbf['header'])
        worksheet.write('F%s' % (row), 'PENGELUARAN', wbf['header'])
        worksheet.write('G%s' % (row), 'SALDO AKHIR', wbf['header'])

        row += 1
        
        no = 1
        for rec in self.line_ids:
            worksheet.write('A%s' % (row), no, wbf['content_number_center'])
            worksheet.write('B%s' % (row), rec.account_id.name, wbf['content_center'])
            worksheet.write('C%s' % (row), rec.location_id.display_name or '', wbf['content_center'])
            worksheet.write('D%s' % (row), rec.saldo_awal, wbf['content_center'])
            worksheet.write('E%s' % (row), rec.penerimaan, wbf['content_center'])
            worksheet.write('F%s' % (row), rec.pengeluaran, wbf['content_center'])
            worksheet.write('G%s' % (row), rec.saldo_akhir, wbf['content_center'])
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
            'name': 'Laporan Mutasi Persediaan XLSX',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'download',
        }
        return result