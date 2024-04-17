from odoo import fields, models, api, _
from odoo.exceptions import UserError
from io import BytesIO
import base64
import xlsxwriter
from datetime import datetime
from . import add_workbook_format as awf

class LaporanPemakaianWizard(models.TransientModel):
    _name = 'laporan.pemakaian.wizard'

    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type', required=True, domain=[('code', '=', 'internal')])
    date_start = fields.Date(string='Date Start', required=True, )
    date_end = fields.Date(string='Date End', required=True, )
    data = fields.Binary(string='Data')
    is_details = fields.Boolean(string='Details ?')

    def action_export_xlsx(self):
        if self.is_details:
            query = """
                SELECT 
                    sp.name,
                    to_char(sp.date_done, 'YYYY/MM/DD') as date_done,
                    sl.name as destination,
                    sp.origin as source_document,
                    sml.machine_no,
                    sml.product_id,
                    sml.qty_done,
                    uu.name as uom,
                    sml.move_id as sm_id,
                    sml.keterangan as ket,
                    sp.scheduled_date, 
                    sp.date_done
                FROM stock_picking as sp

                JOIN stock_move_line as sml
                    ON sp.id = sml.picking_id

                LEFT JOIN res_partner as rp
                    ON sp.partner_id = rp.id

                LEFT JOIN stock_location as sl
                    ON sl.id = sp.location_dest_id

                LEFT JOIN uom_uom as uu
                    ON uu.id = sml.product_uom_id
                    
                WHERE
                    sp.state = 'done'
                    AND sp.picking_type_id = %s
                    AND TO_DATE(to_char(sp.date_done, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= '%s'
                    AND TO_DATE(to_char(sp.date_done, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= '%s'
            """ % (self.picking_type_id.id, self.date_start, self.date_end)
            self._cr.execute(query)
            rslt = self._cr.dictfetchall()
            fp = BytesIO()
            date_string = datetime.now().strftime("%Y-%m-%d")
            workbook = xlsxwriter.Workbook(fp)
            wbf, workbook = awf.add_workbook_format(workbook)

            # WKS 1
            report_name = 'LAPORAN PEMAKAIAN GUDANG %s' % (self.picking_type_id.warehouse_id.name)
            worksheet = workbook.add_worksheet(report_name)        
            
            worksheet.set_column('A6:A6', 3)
            worksheet.set_column('B6:B6', 14)
            worksheet.set_column('C6:C6', 15)
            worksheet.set_column('D6:D6', 15)
            worksheet.set_column('E6:E6', 15)
            worksheet.set_column('F6:F6', 15)
            worksheet.set_column('G6:G6', 40)
            worksheet.set_column('H6:H6', 15)
            worksheet.set_column('I6:I6', 15)
            worksheet.set_column('J6:J6', 15)
            worksheet.set_column('K6:K6', 15)        
            worksheet.set_column('L6:L6', 15)        
            worksheet.set_column('M6:M6', 15)        
            worksheet.set_column('N6:N6', 15)        
            worksheet.set_column('O6:O6', 15)        
            # WKS 1

            worksheet.merge_range('A2:O2', report_name , wbf['merge_format'])
            worksheet.merge_range('A3:O3', 'PERIODE ' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format_2'])
            worksheet.merge_range('A4:O4', '' , wbf['merge_format'])

            row = 6
            worksheet.write('A%s' % (row), 'No', wbf['header'])
            worksheet.write('B%s' % (row), 'NO PICKING', wbf['header'])
            worksheet.write('C%s' % (row), 'DATE', wbf['header'])
            worksheet.write('D%s' % (row), 'DESTINATION', wbf['header'])
            worksheet.write('E%s' % (row), 'SOURCE DOCUMENT', wbf['header'])
            worksheet.write('F%s' % (row), 'NO MC', wbf['header'])
            worksheet.write('G%s' % (row), 'PRODUCT', wbf['header'])
            worksheet.write('H%s' % (row), 'CODE PRODUCT', wbf['header'])
            worksheet.write('I%s' % (row), 'QUANTITY', wbf['header'])
            worksheet.write('J%s' % (row), 'UOM', wbf['header'])
            worksheet.write('K%s' % (row), 'KET', wbf['header'])
            worksheet.write('L%s' % (row), 'HARGA', wbf['header'])
            worksheet.write('M%s' % (row), 'TOTAL HARGA', wbf['header'])
            worksheet.write('N%s' % (row), 'SCHEDULED DATE', wbf['header'])
            worksheet.write('O%s' % (row), 'EFFECTIVE DATE', wbf['header'])

            row += 1
            
            no = 1
            product_obj = self.env['product.product']
            stock_move_obj = self.env['stock.move']
            for rec in rslt:
                product = product_obj.browse(int(rec['product_id'])).name  if rec['product_id'] else ''
                qty = stock_move_obj.browse(rec.get('sm_id', 0)).quantity_done
                price = product_obj.browse(int(rec['product_id'])).standard_price
                code = product_obj.browse(int(rec['product_id'])).default_code
                total_price = qty * price

                worksheet.write('A%s' % (row), no, wbf['content_number_center'])
                worksheet.write('B%s' % (row), rec.get('name', ''), wbf['content_center'])
                worksheet.write('C%s' % (row), rec.get('date_done', '').strftime('%Y-%m-%d'), wbf['content_center'])
                worksheet.write('D%s' % (row), rec.get('destination', ''), wbf['content_center'])
                worksheet.write('E%s' % (row), rec.get('source_document', ''), wbf['content_center'])
                worksheet.write('F%s' % (row), rec.get('machine_no', ''), wbf['content_center'])
                worksheet.write('G%s' % (row), product, wbf['content_center'])
                worksheet.write('H%s' % (row), code, wbf['content_center'])
                worksheet.write('I%s' % (row), qty, wbf['content_number'])
                worksheet.write('J%s' % (row), rec.get('uom', ''), wbf['content_center'])
                worksheet.write('K%s' % (row), rec.get('ket', ''), wbf['content_center'])
                worksheet.write('L%s' % (row), price, wbf['content_number'])
                worksheet.write('M%s' % (row), total_price, wbf['content_number'])
                worksheet.write('N%s' % (row), rec.get('scheduled_date', '').strftime('%Y-%m-%d'), wbf['content_center'])
                worksheet.write('O%s' % (row), rec.get('date_done', '').strftime('%Y-%m-%d'), wbf['content_center'])
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
                'name': 'Laporan Pemakaian XLSX',
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'download',
            }
            return result
        else:
            query = """
                SELECT 
                    sp.name,
                    to_char(sp.date_done, 'YYYY/MM/DD') as date_done,
                    sl.name as destination,
                    sp.origin as source_document,
                    sm.machine_no,
                    sm.product_id,
                    sm.product_qty,
                    uu.name as uom,
                    sm.id as sm_id,
                    sm.keterangan as ket,
                    sp.scheduled_date, 
                    sp.date_done
                FROM stock_picking as sp

                JOIN stock_move as sm
                    ON sp.id = sm.picking_id

                LEFT JOIN res_partner as rp
                    ON sp.partner_id = rp.id
                    
                LEFT JOIN stock_location as sl
                    ON sl.id = sp.location_dest_id

                LEFT JOIN uom_uom as uu
                    ON uu.id = sm.product_uom

                WHERE
                    sp.state = 'done'
                    AND sp.picking_type_id = %s
                    AND TO_DATE(to_char(sp.date_done, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= '%s'
                    AND TO_DATE(to_char(sp.date_done, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= '%s'
            """ % (self.picking_type_id.id, self.date_start, self.date_end)
            self._cr.execute(query)
            rslt = self._cr.dictfetchall()
            fp = BytesIO()
            date_string = datetime.now().strftime("%Y-%m-%d")
            workbook = xlsxwriter.Workbook(fp)
            wbf, workbook = awf.add_workbook_format(workbook)

            # WKS 1
            report_name = 'LAPORAN PEMAKAIAN GUDANG %s' % (self.picking_type_id.warehouse_id.name)
            worksheet = workbook.add_worksheet(report_name)        
            
            worksheet.set_column('A6:A6', 3)
            worksheet.set_column('B6:B6', 14)
            worksheet.set_column('C6:C6', 15)
            worksheet.set_column('D6:D6', 15)
            worksheet.set_column('E6:E6', 15)
            worksheet.set_column('F6:F6', 15)
            worksheet.set_column('G6:G6', 40)
            worksheet.set_column('H6:H6', 15)
            worksheet.set_column('I6:I6', 15)
            worksheet.set_column('J6:J6', 15)
            worksheet.set_column('K6:K6', 15)        
            worksheet.set_column('L6:L6', 15)        
            worksheet.set_column('M6:M6', 15)        
            worksheet.set_column('N6:N6', 15)        
            worksheet.set_column('O6:O6', 15)        
            # WKS 1

            worksheet.merge_range('A2:O2', report_name , wbf['merge_format'])
            worksheet.merge_range('A3:O3', 'PERIODE ' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format_2'])
            worksheet.merge_range('A4:O4', '' , wbf['merge_format'])

            row = 6
            worksheet.write('A%s' % (row), 'No', wbf['header'])
            worksheet.write('B%s' % (row), 'NO PICKING', wbf['header'])
            worksheet.write('C%s' % (row), 'DATE', wbf['header'])
            worksheet.write('D%s' % (row), 'DESTINATION', wbf['header'])
            worksheet.write('E%s' % (row), 'SOURCE DOCUMENT', wbf['header'])
            worksheet.write('F%s' % (row), 'NO MC', wbf['header'])
            worksheet.write('G%s' % (row), 'PRODUCT', wbf['header'])
            worksheet.write('H%s' % (row), 'CODE PRODUCT', wbf['header'])
            worksheet.write('I%s' % (row), 'QUANTITY', wbf['header'])
            worksheet.write('J%s' % (row), 'UOM', wbf['header'])
            worksheet.write('K%s' % (row), 'KET', wbf['header'])
            worksheet.write('L%s' % (row), 'HARGA', wbf['header'])
            worksheet.write('M%s' % (row), 'TOTAL HARGA', wbf['header'])
            worksheet.write('N%s' % (row), 'SCHEDULED DATE', wbf['header'])
            worksheet.write('O%s' % (row), 'EFFECTIVE DATE', wbf['header'])

            row += 1
            
            no = 1
            product_obj = self.env['product.product']
            stock_move_obj = self.env['stock.move']
            for rec in rslt:
                product = product_obj.browse(int(rec['product_id'])).name  if rec['product_id'] else ''
                qty = stock_move_obj.browse(rec.get('sm_id', 0)).quantity_done
                price = product_obj.browse(int(rec['product_id'])).standard_price
                code = product_obj.browse(int(rec['product_id'])).default_code
                total_price = qty * price

                worksheet.write('A%s' % (row), no, wbf['content_number_center'])
                worksheet.write('B%s' % (row), rec.get('name', ''), wbf['content_center'])
                worksheet.write('C%s' % (row), rec.get('date_done', '').strftime('%Y-%m-%d'), wbf['content_center'])
                worksheet.write('D%s' % (row), rec.get('destination', ''), wbf['content_center'])
                worksheet.write('E%s' % (row), rec.get('source_document', ''), wbf['content_center'])
                worksheet.write('F%s' % (row), rec.get('machine_no', ''), wbf['content_center'])
                worksheet.write('G%s' % (row), product, wbf['content_center'])
                worksheet.write('H%s' % (row), code, wbf['content_center'])
                worksheet.write('I%s' % (row), qty, wbf['content_number'])
                worksheet.write('J%s' % (row), rec.get('uom', ''), wbf['content_center'])
                worksheet.write('K%s' % (row), rec.get('ket', ''), wbf['content_center'])
                worksheet.write('L%s' % (row), price, wbf['content_number'])
                worksheet.write('M%s' % (row), total_price, wbf['content_number'])
                worksheet.write('N%s' % (row), rec.get('scheduled_date', '').strftime('%Y-%m-%d'), wbf['content_center'])
                worksheet.write('O%s' % (row), rec.get('date_done', '').strftime('%Y-%m-%d'), wbf['content_center'])
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
                'name': 'Laporan Pemakaian XLSX',
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'download',
            }
            return result
