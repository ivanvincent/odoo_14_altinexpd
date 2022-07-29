from odoo import fields, models, api, _
from odoo.exceptions import UserError
from io import BytesIO
import base64
import xlsxwriter
from datetime import datetime
from . import add_workbook_format as awf

class LaporanPenjualanXlsx(models.TransientModel):
    _name = 'lap.penjualan.xlsx'

    date_start  = fields.Date(string='Date Start')
    date_end    = fields.Date(string='Date End')
    data        = fields.Binary(string='Data')

    def _partner(self):
        partner_str = """
            (select 
                aml.partner_id as id_customer,
                sum(aml.price_subtotal) as amount
            from account_move_line as aml
            join account_move as am on aml.move_id = am.id
            where
                aml.product_id is not null and am.state = 'posted' and am.journal_id = 36
                and TO_DATE(to_char(aml.date, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= '%s'
                and TO_DATE(to_char(aml.date, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= '%s'
            group by aml.partner_id)
        """% (self.date_start, self.date_end)
        return partner_str

    def _grade_a(self):
        grade_a_str = """
            (select 
                aml.partner_id as id_customer, 
                sum(aml.price_subtotal) as amount 
            from account_move_line as aml 
            join account_move as am on aml.move_id = am.id
            join makloon_grade as mg on aml.grade_id = mg.id 
            where
                aml.product_id is not null and mg.kelompok = 'A' and am.state = 'posted' and am.journal_id = 36
                and TO_DATE(to_char(aml.date, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= '%s'
                and TO_DATE(to_char(aml.date, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= '%s'
            group by aml.partner_id)
        """% (self.date_start, self.date_end)
        return grade_a_str

    def _grade_b(self):
        grade_b_str = """
            (select 
                aml.partner_id as id_customer, 
                sum(aml.price_subtotal) as amount 
            from account_move_line as aml 
            join account_move as am on aml.move_id = am.id
            join makloon_grade as mg on aml.grade_id = mg.id 
            where
                aml.product_id is not null and mg.kelompok = 'B' and am.state = 'posted' and am.journal_id = 36
                and TO_DATE(to_char(aml.date, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= '%s'
                and TO_DATE(to_char(aml.date, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= '%s'
            group by aml.partner_id)
        """% (self.date_start, self.date_end)
        return grade_b_str

    def _grade_c(self):
        grade_c_str = """
            (select 
                aml.partner_id as id_customer, 
                sum(aml.price_subtotal) as amount 
            from account_move_line as aml 
            join account_move as am on aml.move_id = am.id
            join makloon_grade as mg on aml.grade_id = mg.id 
            where
                aml.product_id is not null and mg.kelompok = 'C' and am.state = 'posted' and am.journal_id = 36
                and TO_DATE(to_char(aml.date, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= '%s'
                and TO_DATE(to_char(aml.date, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= '%s'
            group by aml.partner_id)
        """% (self.date_start, self.date_end)
        return grade_c_str

    def _grade_x(self):
        grade_x_str = """
            (select 
                aml.partner_id as id_customer, 
                sum(aml.price_subtotal) as amount 
            from account_move_line as aml 
            join account_move as am on aml.move_id = am.id
            join makloon_grade as mg on aml.grade_id = mg.id 
            where
                aml.product_id is not null and mg.kelompok = 'X' and am.state = 'posted' and am.journal_id = 36
                and TO_DATE(to_char(aml.date, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= '%s'
                and TO_DATE(to_char(aml.date, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= '%s'
            group by aml.partner_id)
        """% (self.date_start, self.date_end)
        return grade_x_str

    def generate_excel(self):
        query = """
            select 
                rp.name as customer,
                b.amount as amount_grade_a,
                c.amount as amount_grade_b,
                d.amount as amount_grade_c,
                e.amount as amount_grade_x,
                a.amount as subtotal
            from %s as a
            join res_partner as rp on a.id_customer = rp.id
            left join %s as b on b.id_customer = a.id_customer
            left join %s as c on c.id_customer = a.id_customer
            left join %s as d on d.id_customer = a.id_customer
            left join %s as e on e.id_customer = a.id_customer
            order by rp.name
            """ % (
                self._partner(),
                self._grade_a(),
                self._grade_b(),
                self._grade_c(),
                self._grade_x()
            )
            
        self._cr.execute(query)
        rslt = self._cr.dictfetchall()

        fp = BytesIO()
        date_string = datetime.now().strftime("%Y-%m-%d")
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = awf.add_workbook_format(workbook)

        # WKS 1
        report_name = 'Laporan Penjualan'
        worksheet = workbook.add_worksheet(report_name)        
        
        worksheet.set_column('A6:A6', 30)
        worksheet.set_column('B6:B6', 20)
        worksheet.set_column('C6:C6', 20)
        worksheet.set_column('D6:D6', 20)
        worksheet.set_column('E6:E6', 20)
        worksheet.set_column('F6:F6', 20)
        # WKS 1

        worksheet.merge_range('A2:F2', report_name , wbf['merge_format'])
        worksheet.merge_range('A3:F3', 'PERIODE ' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format_2'])

        row = 6
        worksheet.write('A%s' % (row), 'Customer', wbf['header'])
        worksheet.write('B%s' % (row), 'Grade A Rp.', wbf['header'])
        worksheet.write('C%s' % (row), 'Grade B Rp.', wbf['header'])
        worksheet.write('D%s' % (row), 'Grade C Rp.', wbf['header'])
        worksheet.write('E%s' % (row), 'Lain-Lain', wbf['header'])
        worksheet.write('F%s' % (row), 'Jumlah', wbf['header'])


        row += 1
        
        for rec in rslt:
            worksheet.write('A%s' % (row), rec.get('customer', ''), wbf['content_left'])
            worksheet.write('B%s' % (row), rec.get('amount_grade_a', ''), wbf['content_float'])
            worksheet.write('C%s' % (row), rec.get('amount_grade_b', ''), wbf['content_float'])
            worksheet.write('D%s' % (row), rec.get('amount_grade_c', ''), wbf['content_float'])
            worksheet.write('E%s' % (row), rec.get('amount_grade_x', ''), wbf['content_float'])
            worksheet.write('F%s' % (row), rec.get('subtotal', ''), wbf['content_float'])
            row += 1

        for a in range(7):
            if a > 0:
                if a == 2:
                    worksheet.merge_range('B%s:C%s' % (row, row), 'Dibuat Oleh', wbf['merge_format_2'])
                    worksheet.merge_range('E%s:F%s' % (row, row), 'Mengetahui', wbf['merge_format_2'])
                else:
                    worksheet.merge_range('B%s:C%s' % (row, row), '' , wbf['merge_format_2'])
                    worksheet.merge_range('E%s:F%s' % (row, row), '' , wbf['merge_format_2'])
                row += 1

        worksheet.merge_range('B%s:C%s' % (row, row), '(      %s       )' % (self.env.user.name) , wbf['merge_format_2'])
        worksheet.merge_range('E%s:F%s' % (row, row), '(                                         )' , wbf['merge_format_2'])

        filename = '%s %s%s' % (report_name, date_string, '.xlsx')
        workbook.close()
        out = base64.encodestring(fp.getvalue())
        self.write({'data': out})
        fp.close()

        self.write({'data': out})
        url = "web/content/?model=" + self._name + "&id=" + str(self.id) + "&field=data&download=true&filename=" + filename
        result = {
            'name': 'Laporan Penjualan XLSX',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'download',
        }
        return result