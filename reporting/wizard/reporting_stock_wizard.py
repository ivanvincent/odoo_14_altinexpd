from odoo import fields, models, api, _
from odoo.exceptions import UserError
from . import add_workbook_format as awf
from io import BytesIO
import base64
import xlsxwriter
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)
import xlwt

class ReportingStockXlsx(models.TransientModel):
    _name = 'reporting.stock.xlsx'


    reporting_id    = fields.Many2one('reporting.stock', string='Reporting', required=True,)
    type            = fields.Selection([("detail","Detail"),("in","Receipt"),("out","Release"),("return_in","Return In"),("return_out","Return Out"),("adjustment_in","Adjustment In"),("adjustment_out","Adjustment Out")], string='Type')
    data            = fields.Binary(string='Data')

    @api.model
    def default_get(self,fields):
        res = super().default_get(fields)
        res["reporting_id"] = self.env.context.get('active_id')
        return res
        

    def action_export_xlsx(self):
        fp = BytesIO()
        date_string = datetime.now().strftime("%Y-%m-%d")
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = awf.add_workbook_format(workbook)

        # WKS 1
        report_name = ''
        if self.type == 'in':
            report_name = 'LAPORAN RECEIPT GUDANG %s' % (self.reporting_id.location_id.location_id.name)
        if self.type == 'out':
            report_name = 'LAPORAN RELEASE GUDANG %s' % (self.reporting_id.location_id.location_id.name)
        worksheet = workbook.add_worksheet(report_name)
        worksheet.merge_range('A1:J2', report_name + 'PERIODE ' + '(' + str(self.reporting_id.start_date) + ' - ' + str(self.reporting_id.end_date) + ')' , wbf['format_judul'])
        
        worksheet.set_column('A3:A3', 3)
        worksheet.set_column('B3:B3', 14)
        worksheet.set_column('C3:C3', 15)
        worksheet.set_column('D3:D3', 35)
        worksheet.set_column('E3:E3', 15)
        worksheet.set_column('F3:F3', 50)
        worksheet.set_column('G3:G3', 35)
        worksheet.set_column('H3:H3', 15)
        worksheet.set_column('I3:I3', 10)
        worksheet.set_column('J3:J3', 10)
        # WKS 1

        row = 3
        worksheet.write('A%s' % (row), 'NO', wbf['header'])
        worksheet.write('B%s' % (row), 'NO PICKING', wbf['header'])
        worksheet.write('C%s' % (row), 'DATE', wbf['header'])
        worksheet.write('D%s' % (row), 'PRODUCT CATEGORY', wbf['header'])
        worksheet.write('E%s' % (row), 'KODE BARANG', wbf['header'])
        worksheet.write('F%s' % (row), 'PRODUCT', wbf['header'])
        worksheet.write('G%s' % (row), 'DESCRIPTION', wbf['header'])
        worksheet.write('H%s' % (row), 'VARIASI', wbf['header'])
        worksheet.write('I%s' % (row), 'QUANTITY', wbf['header'])
        worksheet.write('J%s' % (row), 'UOM', wbf['header'])
            

        if self.type == 'detail':
            worksheet.set_column('A3:A3', 3)
            worksheet.set_column('B3:B3', 35)
            worksheet.set_column('C3:C3', 15)
            worksheet.set_column('D3:D3', 55)
            worksheet.set_column('E3:E3', 25)
            worksheet.set_column('F3:F3', 25)
            worksheet.set_column('G3:G3', 25)
            worksheet.set_column('H3:H3', 25)
            worksheet.set_column('I3:I3', 25)
            worksheet.set_column('J3:J3', 25)
            worksheet.set_column('K3:K3', 25)
            worksheet.set_column('L3:L3', 25)
            worksheet.set_column('M3:M3', 25)
            worksheet.set_column('N3:N3', 25)
            worksheet.write('A%s' % (row), 'NO', wbf['header'])
            worksheet.write('B%s' % (row), 'PRODUCT CATEGORY', wbf['header'])
            worksheet.write('C%s' % (row), 'KODE BARANG', wbf['header'])
            worksheet.write('D%s' % (row), 'PRODUCT', wbf['header'])
            worksheet.write('E%s' % (row), 'SALDO AWAL', wbf['header'])
            worksheet.write('F%s' % (row), 'QTY TERIMA', wbf['header'])
            worksheet.write('G%s' % (row), 'QTY KELUAR', wbf['header'])
            worksheet.write('H%s' % (row), 'RETURN TERIMA', wbf['header'])
            worksheet.write('I%s' % (row), 'RETURN KELUAR', wbf['header'])
            worksheet.write('J%s' % (row), 'PENYESUAIAN TERIMA', wbf['header'])
            worksheet.write('K%s' % (row), 'PENYESUAIAN KELUAR', wbf['header'])
            worksheet.write('L%s' % (row), 'SALDO AKHIR', wbf['header'])
            worksheet.write('M%s' % (row), 'PENYESUAIAN', wbf['header'])
            worksheet.write('N%s' % (row), 'UOM', wbf['header'])

        row += 1
        
        no = 1

        reporting_stock_line_ids = []
        if self.type == 'detail':
            reporting_stock_line_ids = self.reporting_id.line_ids
        elif self.type == 'in':
            reporting_stock_line_ids = self.reporting_id.history_ids.search([('stock_type','=','receipt'),('reporting_id','=',self.reporting_id.id)])
        elif self.type == 'out':
            reporting_stock_line_ids = self.reporting_id.history_ids.search([('stock_type','=','release'),('reporting_id','=',self.reporting_id.id)])
        elif self.type == 'return_in':
            reporting_stock_line_ids = self.reporting_id.history_ids.search([('stock_type','=','return_in'),('reporting_id','=',self.reporting_id.id)])
        elif self.type == 'return_out':
            reporting_stock_line_ids = self.reporting_id.history_ids.search([('stock_type','=','return_out'),('reporting_id','=',self.reporting_id.id)])
        elif self.type == 'adjustment_in':
            reporting_stock_line_ids = self.reporting_id.history_ids.search([('stock_type','=','adjustment_in'),('reporting_id','=',self.reporting_id.id)])
        elif self.type == 'adjustmen_out':
            reporting_stock_line_ids = self.reporting_id.history_ids.search([('stock_type','=','adjustmen_out'),('reporting_id','=',self.reporting_id.id)])
        if self.type != 'detail':
            for rec in reporting_stock_line_ids:
                worksheet.write('A%s' % (row), no, wbf['content_center'])
                worksheet.write('B%s' % (row), rec.picking_id.name or '', wbf['content_left'])
                worksheet.write('C%s' % (row), rec.date or '', wbf['content_left'])
                worksheet.write('D%s' % (row), rec.categ_id.name or '', wbf['content_center'])
                worksheet.write('E%s' % (row), rec.product_code or '', wbf['content_left'])
                worksheet.write('F%s' % (row), rec.product_id.name or '', wbf['content_left'])
                worksheet.write('G%s' % (row), rec.description or '', wbf['content_left'])
                worksheet.write('H%s' % (row), rec.variasi or '', wbf['content_left'])
                worksheet.write('I%s' % (row), rec.qty or '', wbf['content_float'])
                worksheet.write('J%s' % (row), rec.uom_id.name or '', wbf['content_left'])
                no += 1
                row += 1
        else:
            for rec in reporting_stock_line_ids:
                worksheet.write('A%s' % (row), no, wbf['content_center'])
                worksheet.write('B%s' % (row), rec.categ_id.name or '', wbf['content_center'])
                worksheet.write('C%s' % (row), rec.product_code or '', wbf['content_left'])
                worksheet.write('D%s' % (row), rec.product_id.name or '', wbf['content_left'])
                worksheet.write('E%s' % (row), rec.qty_start or '', wbf['content_float'])
                worksheet.write('F%s' % (row), rec.qty_in or '', wbf['content_float'])
                worksheet.write('G%s' % (row), rec.qty_out or '', wbf['content_float'])
                worksheet.write('H%s' % (row), rec.return_in or '', wbf['content_float'])
                worksheet.write('I%s' % (row), rec.return_out or '', wbf['content_float'])
                worksheet.write('J%s' % (row), rec.adjustment_in or '', wbf['content_float'])
                worksheet.write('K%s' % (row), rec.adjustment_out or '', wbf['content_float'])
                worksheet.write('L%s' % (row), rec.qty_balance or '', wbf['content_float'])
                worksheet.write('M%s' % (row), rec.penyesuaian or '', wbf['content_float'])
                worksheet.write('N%s' % (row), rec.uom_id.name or '', wbf['content_left'])
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
            'name'      : 'Laporan XLSX',
            'type'      : 'ir.actions.act_url',
            'url'       : url,
            'target'    : 'download',
        }
        return result