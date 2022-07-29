from odoo import fields, models, api, _
from odoo.exceptions import UserError
from io import BytesIO
import base64
import xlsxwriter
from datetime import datetime
from . import add_workbook_format as awf

class LaporanOrderMarketingXlsx(models.TransientModel):
    _name = 'lap.order_marketing.xlsx'

    
    partner_id  = fields.Many2many(comodel_name='res.partner', string='Customer')
    sales_id    = fields.Many2many(comodel_name='hr.employee', string='Sales')
    product_id  = fields.Many2many(comodel_name='product.template', string='Product')
    date_start  = fields.Date(string='Date Start')
    date_end    = fields.Date(string='Date End')
    data        = fields.Binary(string='Data')


    def generate_excel(self):
        where_start_date = " 1=1 "
        if self.date_start :
            where_start_date = " TO_DATE(to_char(so.date_order, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= '%s' "%self.date_start

        where_end_date = " 1=1 "
        if self.date_end :
            where_end_date = " TO_DATE(to_char(so.date_order, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= '%s' "%self.date_end

        where_partner = " 1=1 "
        if self.partner_id :
            where_partner = " so.partner_id = %s "%self.partner_id.id

        where_sales = " 1=1 "
        if self.sales_id :
            where_sales = " so.employee_id = %s "%self.sales_id.id

        where_product = " 1=1 "
        if self.product_id :
            where_product = " so.product_id = %s "%self.product_id.id


        query = """
            select 
                so.date_order as tanggal_om,
                so.name as no_om,
                he.name as sales,
                rp.name as customer,
                pt.name as nama_kain,
                md.name as design,
                so.harga as harga,
                so.amount_total as total_harga,
                so.amount_qty as quantity
            from sale_order as so
            left join res_partner as rp on so.partner_id = rp.id
            left join product_template as pt on so.product_id = pt.id
            left join master_design as md on so.design_id = md.id
            left join hr_employee as he on so.employee_id = he.id
            where
                so.state = 'sale'
                and """+ where_start_date +"""
                and """+ where_end_date +"""
                and """+ where_partner +"""
                and """+ where_sales +"""
                and """+ where_product +"""
            """
        self._cr.execute(query)
        rslt = self._cr.dictfetchall()

        fp = BytesIO()
        date_string = datetime.now().strftime("%Y-%m-%d")
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = awf.add_workbook_format(workbook)

        # WKS 1
        report_name = 'Laporan Penjualan'
        worksheet = workbook.add_worksheet(report_name)        
        
        worksheet.set_column('A6:A6', 20)
        worksheet.set_column('B6:B6', 20)
        worksheet.set_column('C6:C6', 20)
        worksheet.set_column('D6:D6', 20)
        worksheet.set_column('E6:E6', 20)
        worksheet.set_column('F6:F6', 20)
        worksheet.set_column('G6:G6', 20)
        worksheet.set_column('H6:H6', 20)
        worksheet.set_column('I6:I6', 20)
        worksheet.set_column('J6:J6', 20)
        # WKS 1

        worksheet.merge_range('A2:J2', report_name , wbf['merge_format'])
        worksheet.merge_range('A3:J3', 'PERIODE ' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format_2'])

        row = 6
        worksheet.write('A%s' % (row), 'Tanggal OM', wbf['header'])
        worksheet.write('B%s' % (row), 'Sales', wbf['header'])
        worksheet.write('C%s' % (row), 'NP/SC.', wbf['header'])
        worksheet.write('D%s' % (row), 'No OM.', wbf['header'])
        worksheet.write('E%s' % (row), 'Nama Customer.', wbf['header'])
        worksheet.write('F%s' % (row), 'Nama Kain', wbf['header'])
        worksheet.write('G%s' % (row), 'Design', wbf['header'])
        worksheet.write('H%s' % (row), 'Harga', wbf['header'])
        worksheet.write('I%s' % (row), 'Total Harga', wbf['header'])
        worksheet.write('J%s' % (row), 'Quantity OM', wbf['header'])


        row += 1
        
        for rec in rslt:
            tanggal_om   = rec.get('tanggal_om', '').strftime('%Y-%m-%d')

            worksheet.write('A%s' % (row), tanggal_om, wbf['content_left'])
            worksheet.write('B%s' % (row), rec.get('sales', ''), wbf['content_left'])
            worksheet.write('C%s' % (row), rec.get(''), wbf['content_left'])
            worksheet.write('D%s' % (row), rec.get('no_om', ''), wbf['content_left'])
            worksheet.write('E%s' % (row), rec.get('customer', ''), wbf['content_left'])
            worksheet.write('F%s' % (row), rec.get('nama_kain', ''), wbf['content_left'])
            worksheet.write('G%s' % (row), rec.get('design', ''), wbf['content_left'])
            worksheet.write('H%s' % (row), rec.get('harga', ''), wbf['content_float'])
            worksheet.write('I%s' % (row), rec.get('total_harga', ''), wbf['content_float'])
            worksheet.write('J%s' % (row), rec.get('quantity', ''), wbf['content_float'])
            row += 1

        for a in range(7):
            if a > 0:
                if a == 2:
                    worksheet.merge_range('A%s:C%s' % (row, row), 'Dibuat Oleh', wbf['merge_format_2'])
                    worksheet.merge_range('H%s:J%s' % (row, row), 'Mengetahui', wbf['merge_format_2'])
                else:
                    worksheet.merge_range('A%s:C%s' % (row, row), '' , wbf['merge_format_2'])
                    worksheet.merge_range('H%s:J%s' % (row, row), '' , wbf['merge_format_2'])
                row += 1

        worksheet.merge_range('A%s:C%s' % (row, row), '(      %s       )' % (self.env.user.name) , wbf['merge_format_2'])
        worksheet.merge_range('H%s:J%s' % (row, row), '(                                         )' , wbf['merge_format_2'])

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