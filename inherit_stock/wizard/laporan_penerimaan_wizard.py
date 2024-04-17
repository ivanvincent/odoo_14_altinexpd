from odoo import fields, models, api, _
from odoo.exceptions import UserError
from io import BytesIO
import base64
import xlsxwriter
from datetime import datetime
from . import add_workbook_format as awf

class LaporanPenerimaanWizard(models.TransientModel):
    _name = 'laporan.penerimaan.wizard'

    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type', domain=[('code', '=', 'incoming')], )
    date_start = fields.Date(string='Date Start', required=True, )
    date_end = fields.Date(string='Date End',  required=True, default=fields.Date.today())
    data = fields.Binary(string='Data')
    is_all_warehouse = fields.Boolean(string='All Warehouse ?')

    def generate_excel(self):
        if self.is_all_warehouse:
            # self.generate_excel_all_warehouse()
            query = """
                SELECT 
                    sp.name,
                    to_char(sp.date_done, 'YYYY/MM/DD') as date_done,
                    rp.name as supplier,
                    sp.origin as no_po,
                    sp.surat_jalan_supplier as no_sj,
                    sm.product_id,
                    sm.product_qty,
                    sm.product_uom,
                    sp.create_uid,
                    sp.user_id,
                    sp.is_invoiced,
                    sm.id as sm_id,
                    po.id as po_id,
                    sp.id as picking_id,
                    purchase_line_id as po_line_id
                FROM stock_picking as sp
                    
                JOIN stock_move as sm
                    ON sp.id = sm.picking_id
                    
                LEFT JOIN res_partner as rp
                    ON sp.partner_id = rp.id
                
                LEFT JOIN purchase_order as po
                    ON po.name = sp.origin
            
                WHERE
                    sp.state = 'done'
                    AND sp.picking_type_id IN (select id from stock_picking_type where code = 'incoming')
                    AND TO_DATE(to_char(sp.date_done, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= '%s'
                    AND TO_DATE(to_char(sp.date_done, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= '%s'
                """ % (self.date_start, self.date_end)
                
            self._cr.execute(query)
            rslt = self._cr.dictfetchall()

            fp = BytesIO()
            date_string = datetime.now().strftime("%Y-%m-%d")
            workbook = xlsxwriter.Workbook(fp)
            wbf, workbook = awf.add_workbook_format(workbook)

            # WKS 1
            report_name = 'LAPORAN PENERIMAAN BARANG SEMUA GUDANG'
            worksheet = workbook.add_worksheet(report_name)        
            
            worksheet.set_column('A6:A6', 3)
            worksheet.set_column('B6:B6', 14)
            worksheet.set_column('C6:C6', 15)
            worksheet.set_column('D6:D6', 40)
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
            worksheet.set_column('P6:P6', 15)
            worksheet.set_column('Q6:Q6', 15)
            worksheet.set_column('R6:R6', 15)
            worksheet.set_column('S6:S6', 15)
            # WKS 1

            worksheet.merge_range('A2:P2', report_name , wbf['merge_format'])
            worksheet.merge_range('A3:P3', 'PERIODE ' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format_2'])
            worksheet.merge_range('A4:P4', '' , wbf['merge_format'])
            worksheet.merge_range('A5:P5', 'SEMUA GUDANG', wbf['merge_format_3'])

            row = 6
            worksheet.write('A%s' % (row), 'No', wbf['header'])
            worksheet.write('B%s' % (row), 'DATE', wbf['header'])
            worksheet.write('C%s' % (row), 'NO PICKING', wbf['header'])
            worksheet.write('D%s' % (row), 'SUPPLIER', wbf['header'])
            worksheet.write('E%s' % (row), 'NO PO', wbf['header'])
            worksheet.write('F%s' % (row), 'NO SJ', wbf['header'])
            worksheet.write('G%s' % (row), 'CATEGORY', wbf['header'])
            worksheet.write('H%s' % (row), 'CODE PRODUCT', wbf['header'])
            worksheet.write('I%s' % (row), 'PRODUCT', wbf['header'])
            worksheet.write('J%s' % (row), 'QUANTITY', wbf['header'])
            worksheet.write('K%s' % (row), 'HARGA', wbf['header'])
            worksheet.write('L%s' % (row), 'DPP', wbf['header'])
            worksheet.write('M%s' % (row), 'STATUS', wbf['header'])
            worksheet.write('N%s' % (row), 'JUMLAH PPN', wbf['header'])
            worksheet.write('O%s' % (row), 'TOTAL', wbf['header'])
            worksheet.write('P%s' % (row), 'UOM', wbf['header'])
            worksheet.write('Q%s' % (row), 'CREATE BY', wbf['header'])
            worksheet.write('R%s' % (row), 'RESPONSIBLE', wbf['header'])
            worksheet.write('S%s' % (row), 'INVOICED ?', wbf['header'])
            worksheet.write('T%s' % (row), 'NO BILL', wbf['header'])


            row += 1
            
            no = 1
            user_obj = self.env['res.users']
            po_line_obj = self.env['purchase.order.line']
            product_obj = self.env['product.product']
            stock_move_obj = self.env['stock.move']
            for rec in rslt:
                move = self.env['account.move'].search([('picking_id', '=', rec.get('picking_id'))])
                code_product = product_obj.browse(int(rec['product_id'])).default_code  if rec['product_id'] else ''
                product = product_obj.browse(int(rec['product_id'])).name  if rec['product_id'] else ''
                uom = self.env['uom.uom'].browse(int(rec['product_uom'])).name  if rec['product_uom'] else ''
                create_by = user_obj.browse(int(rec['create_uid'])).name  if rec['create_uid'] else ''
                responsible = user_obj.browse(int(rec['user_id'])).name  if rec['user_id'] else ''
                invoiced = 'YES' if rec.get('is_invoiced') else 'NO'
                # price = po_line_obj.search([('order_id', '=', rec.get('po_id', False)), ('product_id', '=', int(rec['product_id']))], limit=1).price_unit
                # qty = rec.get('product_qty', 0)
                qty = stock_move_obj.browse(rec.get('sm_id', 0)).quantity_done
                # price = po_line_obj.browse(rec['po_line_id']).price_unit
                price = po_line_obj.browse(rec['po_line_id']).price_unit
                price_total = rec.get('product_qty', 0) * price
                categ = product_obj.browse(int(rec['product_id'])).categ_id.name
                taxes = ', '.join(po_line_obj.browse(rec['po_line_id']).taxes_id.mapped('name'))
                # price_subtotal = po_line_obj.browse(rec['po_line_id']).price_subtotal
                dpp = qty * price
                ppn = dpp * 0.1 if taxes else 0
                total = dpp + ppn

                worksheet.write('A%s' % (row), no, wbf['content_number_center'])
                worksheet.write('B%s' % (row), rec.get('date_done', ''), wbf['content_center'])
                worksheet.write('C%s' % (row), rec.get('name', ''), wbf['content_center'])
                worksheet.write('D%s' % (row), rec.get('supplier', ''), wbf['content_center'])
                worksheet.write('E%s' % (row), rec.get('no_po', ''), wbf['content_center'])
                worksheet.write('F%s' % (row), rec.get('no_sj', ''), wbf['content_center'])
                worksheet.write('G%s' % (row), categ, wbf['content_center'])
                worksheet.write('H%s' % (row), code_product, wbf['content_center'])
                worksheet.write('I%s' % (row), product, wbf['content_center'])
                worksheet.write('J%s' % (row), qty or '', wbf['content_number'])
                worksheet.write('K%s' % (row), price, wbf['content_number'])
                worksheet.write('L%s' % (row), dpp, wbf['content_number'])
                worksheet.write('M%s' % (row), taxes  or '', wbf['content_number'])
                worksheet.write('N%s' % (row), ppn  or '', wbf['content_number'])
                worksheet.write('O%s' % (row), total or '', wbf['content_number'])
                worksheet.write('P%s' % (row), uom, wbf['content_center'])
                worksheet.write('Q%s' % (row), create_by, wbf['content_center'])
                worksheet.write('R%s' % (row), responsible, wbf['content_center'])
                worksheet.write('S%s' % (row), invoiced, wbf['content_center'])
                worksheet.write('T%s' % (row), ', '.join(move.mapped('name')) or '', wbf['content_center'])
                no += 1
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
                'name': 'Laporan Penerimaan XLSX',
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
                    rp.name as supplier,
                    sp.origin as no_po,
                    sp.surat_jalan_supplier as no_sj,
                    sm.product_id,
                    sm.product_qty,
                    sm.product_uom,
                    sp.create_uid,
                    sp.user_id,
                    sm.id as sm_id,
                    sp.is_invoiced
                FROM stock_picking as sp
                    
                JOIN stock_move as sm
                    ON sp.id = sm.picking_id
                    
                LEFT JOIN res_partner as rp
                    ON sp.partner_id = rp.id
            
                WHERE
                    sp.state = 'done'
                    AND sp.picking_type_id = %s
                    AND TO_DATE(to_char(sp.date_done, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= '%s'
                    AND TO_DATE(to_char(sp.date_done, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= '%s'
                """ % (self.picking_type_id.id, self.date_start, self.date_end)
                # AND sp.date_done BETWEEN '%s' AND '%s'
                
            self._cr.execute(query)
            rslt = self._cr.dictfetchall()

            fp = BytesIO()
            date_string = datetime.now().strftime("%Y-%m-%d")
            workbook = xlsxwriter.Workbook(fp)
            wbf, workbook = awf.add_workbook_format(workbook)

            # WKS 1
            report_name = 'LAPORAN PENERIMAAN BARANG %s' % (self.picking_type_id.warehouse_id.name)
            worksheet = workbook.add_worksheet(report_name)        
            
            worksheet.set_column('A6:A6', 3)
            worksheet.set_column('B6:B6', 14)
            worksheet.set_column('C6:C6', 15)
            worksheet.set_column('D6:D6', 40)
            worksheet.set_column('E6:E6', 15)
            worksheet.set_column('F6:F6', 15)
            worksheet.set_column('G6:G6', 40)
            worksheet.set_column('H6:H6', 15)
            worksheet.set_column('I6:I6', 15)
            worksheet.set_column('J6:J6', 15)
            worksheet.set_column('K6:K6', 15)
            worksheet.set_column('L6:L6', 15)
            worksheet.set_column('M6:M6', 15)
            # WKS 1

            worksheet.merge_range('A2:K2', report_name , wbf['merge_format'])
            worksheet.merge_range('A3:K3', 'PERIODE ' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format_2'])
            worksheet.merge_range('A4:K4', '' , wbf['merge_format'])
            worksheet.merge_range('A5:K5', '' + self.picking_type_id.warehouse_id.name.upper(), wbf['merge_format_3'])

            row = 6
            worksheet.write('A%s' % (row), 'No', wbf['header'])
            worksheet.write('B%s' % (row), 'DATE', wbf['header'])
            worksheet.write('C%s' % (row), 'NO PICKING', wbf['header'])
            worksheet.write('D%s' % (row), 'SUPPLIER', wbf['header'])
            worksheet.write('E%s' % (row), 'NO PO', wbf['header'])
            worksheet.write('F%s' % (row), 'NO SJ', wbf['header'])
            worksheet.write('G%s' % (row), 'CODE PRODUCT', wbf['header'])
            worksheet.write('H%s' % (row), 'PRODUCT', wbf['header'])
            worksheet.write('I%s' % (row), 'QUANTITY', wbf['header'])
            worksheet.write('J%s' % (row), 'UOM', wbf['header'])
            worksheet.write('K%s' % (row), 'CREATE BY', wbf['header'])
            worksheet.write('L%s' % (row), 'RESPONSIBLE', wbf['header'])
            worksheet.write('M%s' % (row), 'INVOICED ?', wbf['header'])
            worksheet.write('N%s' % (row), 'NO BILL', wbf['header'])


            row += 1
            
            no = 1
            user_obj = self.env['res.users']
            stock_move_obj = self.env['stock.move']
            for rec in rslt:
                move = self.env['account.move'].search([('picking_id', '=', rec.get('picking_id'))])
                code_product = self.env['product.product'].browse(int(rec['product_id'])).default_code  if rec['product_id'] else ''
                product = self.env['product.product'].browse(int(rec['product_id'])).name  if rec['product_id'] else ''
                uom = self.env['uom.uom'].browse(int(rec['product_uom'])).name  if rec['product_uom'] else ''
                create_by = user_obj.browse(int(rec['create_uid'])).name  if rec['create_uid'] else ''
                responsible = user_obj.browse(int(rec['user_id'])).name  if rec['user_id'] else ''
                invoiced = 'YES' if rec.get('is_invoiced') else 'NO'
                qty = stock_move_obj.browse(rec.get('sm_id', 0)).quantity_done

                worksheet.write('A%s' % (row), no, wbf['content_number_center'])
                worksheet.write('B%s' % (row), rec.get('date_done', ''), wbf['content_center'])
                worksheet.write('C%s' % (row), rec.get('name', ''), wbf['content_center'])
                worksheet.write('D%s' % (row), rec.get('supplier', ''), wbf['content_center'])
                worksheet.write('E%s' % (row), rec.get('no_po', ''), wbf['content_center'])
                worksheet.write('F%s' % (row), rec.get('no_sj', ''), wbf['content_center'])
                worksheet.write('G%s' % (row), code_product, wbf['content_center'])
                worksheet.write('H%s' % (row), product, wbf['content_center'])
                worksheet.write('I%s' % (row), qty or '', wbf['content_number'])
                worksheet.write('J%s' % (row), uom, wbf['content_center'])
                worksheet.write('K%s' % (row), create_by, wbf['content_center'])
                worksheet.write('L%s' % (row), responsible, wbf['content_center'])
                worksheet.write('M%s' % (row), invoiced, wbf['content_center'])
                worksheet.write('N%s' % (row), ', '.join(move.mapped('name')) or '', wbf['content_center'])
                no += 1 
                row += 1

            for a in range(7):
                if a > 0:
                    if a == 2:
                        worksheet.merge_range('B%s:C%s' % (row, row), 'Dibuat Oleh', wbf['merge_format_2'])
                        worksheet.merge_range('E%s:F%s' % (row, row), 'Mengetahui', wbf['merge_format_2'])
                        print('dua', a)
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
                'name': 'Laporan Penerimaan XLSX',
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'download',
            }
            return result

    def generate_excel_all_warehouse(self):
        query = """
            SELECT 
                sp.name,
                to_char(sp.date_done, 'YYYY/MM/DD') as date_done,
                rp.name as supplier,
                sp.origin as no_po,
                sp.surat_jalan_supplier as no_sj,
                sm.product_id,
                sm.product_qty,
                sm.product_uom,
                sp.create_uid,
                sp.user_id,
                sp.is_invoiced,
                po.id as po_id
            FROM stock_picking as sp
                
            JOIN stock_move as sm
                ON sp.id = sm.picking_id
                
            LEFT JOIN res_partner as rp
                ON sp.partner_id = rp.id
            
            LEFT JOIN purchase_order as po
                ON po.name = sp.origin
        
            WHERE
                sp.state = 'done'
                AND sp.picking_type_id IN (select id from stock_picking_type where code = 'incoming')
                AND TO_DATE(to_char(sp.date_done, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= '%s'
                AND TO_DATE(to_char(sp.date_done, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= '%s'
            """ % (self.date_start, self.date_end)
            
        self._cr.execute(query)
        rslt = self._cr.dictfetchall()

        fp = BytesIO()
        date_string = datetime.now().strftime("%Y-%m-%d")
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = awf.add_workbook_format(workbook)

        # WKS 1
        report_name = 'LAPORAN PENERIMAAN BARANG SEMUA GUDANG'
        worksheet = workbook.add_worksheet(report_name)        
        
        worksheet.set_column('A6:A6', 3)
        worksheet.set_column('B6:B6', 14)
        worksheet.set_column('C6:C6', 15)
        worksheet.set_column('D6:D6', 40)
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

        worksheet.merge_range('A2:N2', report_name , wbf['merge_format'])
        worksheet.merge_range('A3:N3', 'PERIODE ' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format_2'])
        worksheet.merge_range('A4:N4', '' , wbf['merge_format'])
        worksheet.merge_range('A5:N5', 'SEMUA GUDANG', wbf['merge_format_3'])

        row = 6
        worksheet.write('A%s' % (row), 'No', wbf['header'])
        worksheet.write('B%s' % (row), 'DATE', wbf['header'])
        worksheet.write('C%s' % (row), 'NO PICKING', wbf['header'])
        worksheet.write('D%s' % (row), 'SUPPLIER', wbf['header'])
        worksheet.write('E%s' % (row), 'NO PO', wbf['header'])
        worksheet.write('F%s' % (row), 'CATEGORY', wbf['header'])
        worksheet.write('G%s' % (row), 'NO SJ', wbf['header'])
        worksheet.write('H%s' % (row), 'CODE PRODUCT', wbf['header'])
        worksheet.write('I%s' % (row), 'PRODUCT', wbf['header'])
        worksheet.write('J%s' % (row), 'QUANTITY', wbf['header'])
        worksheet.write('K%s' % (row), 'HARGA BELI', wbf['header'])
        worksheet.write('L%s' % (row), 'UOM', wbf['header'])
        worksheet.write('M%s' % (row), 'CREATE BY', wbf['header'])
        worksheet.write('N%s' % (row), 'RESPONSIBLE', wbf['header'])
        worksheet.write('O%s' % (row), 'INVOICED ?', wbf['header'])


        row += 1
        
        no = 1
        user_obj = self.env['res.users']
        po_line_obj = self.env['purchase.order.line']
        product_obj = self.env['product.product']
        for rec in rslt:
            code_product = product_obj.browse(int(rec['product_id'])).default_code  if rec['product_id'] else ''
            product = product_obj.browse(int(rec['product_id'])).name  if rec['product_id'] else ''
            uom = self.env['uom.uom'].browse(int(rec['product_uom'])).name  if rec['product_uom'] else ''
            create_by = user_obj.browse(int(rec['create_uid'])).name  if rec['create_uid'] else ''
            responsible = user_obj.browse(int(rec['user_id'])).name  if rec['user_id'] else ''
            invoiced = 'YES' if rec.get('is_invoiced') else 'NO'
            price = po_line_obj.search([('order_id', '=', rec.get('po_id', False)), ('product_id', '=', int(rec['product_id']))], limit=1).price_unit
            price_total = rec.get('product_qty', 0) * price
            categ = product_obj.browse(int(rec['product_id'])).categ_id.name

            worksheet.write('A%s' % (row), no, wbf['content_number_center'])
            worksheet.write('B%s' % (row), rec.get('date_done', ''), wbf['content_center'])
            worksheet.write('C%s' % (row), rec.get('name', ''), wbf['content_center'])
            worksheet.write('D%s' % (row), rec.get('supplier', ''), wbf['content_center'])
            worksheet.write('E%s' % (row), rec.get('no_po', ''), wbf['content_center'])
            worksheet.write('F%s' % (row), categ, wbf['content_center'])
            worksheet.write('G%s' % (row), rec.get('no_sj', ''), wbf['content_center'])
            worksheet.write('H%s' % (row), code_product, wbf['content_center'])
            worksheet.write('I%s' % (row), product, wbf['content_center'])
            worksheet.write('J%s' % (row), rec.get('product_qty', 0) or '', wbf['content_number'])
            worksheet.write('K%s' % (row), price_total or '', wbf['content_number'])
            worksheet.write('L%s' % (row), uom, wbf['content_center'])
            worksheet.write('M%s' % (row), create_by, wbf['content_center'])
            worksheet.write('N%s' % (row), responsible, wbf['content_center'])
            worksheet.write('O%s' % (row), invoiced, wbf['content_center'])
            no += 1
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
            'name': 'Laporan Penerimaan XLSX',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'download',
        }
        return result
