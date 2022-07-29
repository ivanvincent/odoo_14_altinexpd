from odoo import fields, models, api, _
from odoo.exceptions import UserError
from io import BytesIO
import base64
import xlsxwriter
from datetime import datetime
from . import add_workbook_format as awf

class LaporanLpsmBenang(models.TransientModel):
    _name = 'laporan.lpsm.benang.wizard'

    date_start = fields.Date(string='Date Start', required=True, )
    date_end = fields.Date(string='Date End', required=True, )
    data = fields.Binary(string='Image',)


    def action_export_xlsx(self):
        query = """
            SELECT 
                pp.default_code AS kode_brg,
                pl.name AS product_name,
                spl.create_date::date,
                spl.name AS no_lot,
                (CURRENT_TIMESTAMP::date - spl.create_date::date)||' Days' as umur_lot,
                spl.qty,
                uu.name AS uom
            FROM stock_production_lot spl
                LEFT JOIN product_product pp ON spl.product_id = pp.id
                LEFT JOIN product_template pl ON pp.product_tmpl_id = pl.id
                LEFT JOIN uom_uom uu ON spl.product_uom_id = uu.id
            WHERE
                spl.location_id = 60
                AND spl.create_date BETWEEN '%s' AND '%s'
                AND spl.qty > 0
        """ % (self.date_start, self.date_end)
        self._cr.execute(query)
        rslt = self._cr.dictfetchall()
        fp = BytesIO()
        date_string = datetime.now().strftime("%Y-%m-%d")
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = awf.add_workbook_format(workbook)

        # WKS 1
        report_name = 'LAPORAN LPSM BENANG'
        worksheet = workbook.add_worksheet(report_name)        
        
        worksheet.set_column('A6:A6', 3)
        worksheet.set_column('B6:B6', 14)
        worksheet.set_column('C6:C6', 15)
        worksheet.set_column('D6:D6', 15)
        worksheet.set_column('E6:E6', 20)
        worksheet.set_column('F6:F6', 15)
        worksheet.set_column('G6:G6', 20)
        worksheet.set_column('H6:H6', 20)
        # WKS 1

        worksheet.merge_range('A2:I2', report_name , wbf['merge_format'])
        worksheet.merge_range('A3:I3', 'PERIODE ' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format_2'])
        worksheet.merge_range('A4:I4', '' , wbf['merge_format'])

        row = 6
        worksheet.write('A%s' % (row), 'No', wbf['header'])
        worksheet.write('B%s' % (row), 'KODE BARANG', wbf['header'])
        worksheet.write('C%s' % (row), 'NAMA PRODUK', wbf['header'])
        worksheet.write('D%s' % (row), 'TANGGAL', wbf['header'])
        worksheet.write('E%s' % (row), 'LOT', wbf['header'])
        worksheet.write('F%s' % (row), 'UMUR LOT', wbf['header'])
        worksheet.write('G%s' % (row), 'QUANTITY', wbf['header'])
        worksheet.write('H%s' % (row), 'UOM', wbf['header'])

        row += 1

        no = 1
        for rec in rslt:
            worksheet.write('A%s' % (row), no, wbf['content_number_center'])
            worksheet.write('B%s' % (row), rec.get('kode_brg', ''), wbf['content_center'])
            worksheet.write('C%s' % (row), rec.get('product_name', ''), wbf['content_center'])
            worksheet.write('D%s' % (row), rec.get('create_date', '').strftime('%Y-%m-%d'), wbf['content_center'])
            worksheet.write('E%s' % (row), rec.get('no_lot', ''), wbf['content_center'])
            worksheet.write('F%s' % (row), rec.get('umur_lot', ''), wbf['content_center'])
            worksheet.write('G%s' % (row), rec.get('qty', ''), wbf['content_number'])
            worksheet.write('H%s' % (row), rec.get('uom', ''), wbf['content_center'])

            row += 1
            no += 1
        
        filename = '%s %s%s' % (report_name, date_string, '.xlsx')
        workbook.close()
        out = base64.encodestring(fp.getvalue())
        self.write({'data': out})
        fp.close()

        self.write({'data': out})
        url = "web/content/?model=" + self._name + "&id=" + str(self.id) + "&field=data&download=true&filename=" + filename
        result = {
            'name': 'Laporan Lpsm Benang XLSX',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'download',
        }
        return result