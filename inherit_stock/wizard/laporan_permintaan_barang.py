from odoo import fields, models, api, _
from odoo.exceptions import UserError
from io import BytesIO
import base64
import xlsxwriter
from datetime import datetime
from . import add_workbook_format as awf

class LaporanPermintaanWizard(models.TransientModel):
    _name = 'laporan.permintaan.wizard'

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', domain=[('id', 'in', [58, 7, 19, 31, 5, 2, 4, 30, 46])], default=4, required=True, )
    date_start = fields.Date(string='Date Start', required=True, )
    date_end = fields.Date(string='Date End', required=True, )
    data = fields.Binary(string='Image')

    def action_export_xlsx(self):
        query = """
            SELECT
                rr.name,
                rrl.request_date,
                pp.default_code,
                pl.name AS product_name,
                rrl.quantity AS qty,
                split_part(rr.name, '/', 2) AS departement_code,
                rp.name AS requested_by,
                rrl.name AS keterangan
            FROM
                request_requisition_line rrl
                LEFT JOIN request_requisition rr ON rr.id = rrl.order_id
                LEFT JOIN product_product pp ON pp.id = rrl.product_id
                LEFT JOIN product_template pl ON pp.product_tmpl_id = pl.id
                LEFT JOIN res_users ru ON rr.requested_by = ru.id
                LEFT JOIN res_partner rp ON ru.partner_id = rp.id
            WHERE
                rr.warehouse_id = %s
                AND rrl.request_date BETWEEN '%s' AND '%s'
        """ % (self.warehouse_id.id, self.date_start, self.date_end)
        self._cr.execute(query)
        rslt = self._cr.dictfetchall()
        fp = BytesIO()
        date_string = datetime.now().strftime("%Y-%m-%d")
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = awf.add_workbook_format(workbook)

        # WKS 1
        report_name = 'LAPORAN PERMINTAAN BARANG'
        worksheet = workbook.add_worksheet(report_name)        
        
        worksheet.set_column('A6:A6', 3)
        worksheet.set_column('B6:B6', 14)
        worksheet.set_column('C6:C6', 15)
        worksheet.set_column('D6:D6', 15)
        worksheet.set_column('E6:E6', 35)
        worksheet.set_column('F6:F6', 15)
        worksheet.set_column('G6:G6', 20)
        worksheet.set_column('H6:H6', 30)
        worksheet.set_column('I6:I6', 40)
        # WKS 1

        worksheet.merge_range('A2:I2', report_name , wbf['merge_format'])
        worksheet.merge_range('A3:I3', 'PERIODE ' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format_2'])
        worksheet.merge_range('A4:I4', '' , wbf['merge_format'])

        row = 6
        worksheet.write('A%s' % (row), 'No', wbf['header'])
        worksheet.write('B%s' % (row), 'NO RR', wbf['header'])
        worksheet.write('C%s' % (row), 'REQUEST DATE', wbf['header'])
        worksheet.write('D%s' % (row), 'KODE BARANG', wbf['header'])
        worksheet.write('E%s' % (row), 'NAMA BARANG', wbf['header'])
        worksheet.write('F%s' % (row), 'QUANTITY', wbf['header'])
        worksheet.write('G%s' % (row), 'KODE DEPARTEMENT', wbf['header'])
        worksheet.write('H%s' % (row), 'REQUESTED BY', wbf['header'])
        worksheet.write('I%s' % (row), 'KETERANGAN', wbf['header'])

        row += 1

        no = 1
        for rec in rslt:
            worksheet.write('A%s' % (row), no, wbf['content_number_center'])
            worksheet.write('B%s' % (row), rec.get('name', ''), wbf['content_center'])
            worksheet.write('C%s' % (row), rec.get('request_date', '').strftime('%Y-%m-%d'), wbf['content_center'])
            worksheet.write('D%s' % (row), rec.get('default_code', ''), wbf['content_center'])
            worksheet.write('E%s' % (row), rec.get('product_name', ''), wbf['content_center'])
            worksheet.write('F%s' % (row), rec.get('qty', ''), wbf['content_number'])
            worksheet.write('G%s' % (row), rec.get('departement_code', ''), wbf['content_center'])
            worksheet.write('H%s' % (row), rec.get('requested_by', ''), wbf['content_center'])
            worksheet.write('I%s' % (row), rec.get('keterangan', ''), wbf['content_center'])

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
            'name': 'Laporan Permintaan Barang XLSX',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'download',
        }
        return result