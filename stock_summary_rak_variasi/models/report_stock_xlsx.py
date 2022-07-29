import xlsxwriter
import base64
from odoo import fields, models, api
from cStringIO import StringIO
import pytz
from pytz import timezone
from datetime import datetime
import PIL
import io
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import xlwt
import base64
import cStringIO
from datetime import datetime
from odoo.exceptions import Warning, ValidationError, UserError

class ReportStockXlsx(models.TransientModel):
    _name = "report.stock.xlsx"
    _description = "Report Stock Excel"

    name = fields.Char('Name')
    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone('Asia/Jakarta'))

    file_data = fields.Binary('File', readonly=True)
    type = fields.Selection([
        ('detail','Details'),
        ('history','History'),
    ], default='detail', string='Type')
    history = fields.Selection([
        ('all','ALL'),
        ('in','IN'),
        ('out','OUT'),
        ('return_in', 'Return IN'),
        ('return_out', 'Return OUT'),
        ('revision_in', 'Revision IN'),
        ('revision_out', 'Revision OUT'),
    ], string='History', default='all')


    is_excel = fields.Selection([
        ('1','Excel'),
        ('2','PDF'),
    ], default='1', string='Tipe File')


    @api.onchange('type')
    def set_default_is_excel(self):

        if(self.type):
            return {
                'value':{
                    'is_excel':'1',
                }
            }


    def add_workbook_format(self, workbook):
        colors = {
            'white_orange': '#FFFFDB',
            'orange': '#FFC300',
            'red': '#FF0000',
            'yellow': '#F6FA03',
        }

        wbf = {}
        wbf['header'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': '#FFFFDB','font_color': '#000000'})
        wbf['header'].set_border()

        wbf['header_orange'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': colors['orange'],'font_color': '#000000'})
        wbf['header_orange'].set_border()

        wbf['header_yellow'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': colors['yellow'],'font_color': '#000000'})
        wbf['header_yellow'].set_border()

        wbf['header_no'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': '#FFFFDB','font_color': '#000000'})
        wbf['header_no'].set_border()
        wbf['header_no'].set_align('vcenter')

        wbf['footer'] = workbook.add_format({'align':'left'})

        wbf['content_datetime'] = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
        wbf['content_datetime'].set_left()
        wbf['content_datetime'].set_right()

        wbf['content_date'] = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        wbf['content_date'].set_left()
        wbf['content_date'].set_right()

        wbf['title_doc'] = workbook.add_format({'bold': 1,'align': 'left'})
        wbf['title_doc'].set_font_size(12)

        wbf['company'] = workbook.add_format({'align': 'left'})
        wbf['company'].set_font_size(11)

        wbf['content'] = workbook.add_format()
        wbf['content'].set_left()
        wbf['content'].set_right()

        wbf['content_float'] = workbook.add_format({'align': 'right','num_format': '#,##0.00'})
        wbf['content_float'].set_right()
        wbf['content_float'].set_left()

        wbf['content_number'] = workbook.add_format({'align': 'right', 'num_format': '#,##0'})
        wbf['content_number'].set_right()
        wbf['content_number'].set_left()

        wbf['content_percent'] = workbook.add_format({'align': 'right','num_format': '0.00%'})
        wbf['content_percent'].set_right()
        wbf['content_percent'].set_left()

        wbf['total_float'] = workbook.add_format({'bold':1, 'bg_color':colors['white_orange'], 'align':'right', 'num_format':'#,##0.00'})
        wbf['total_float'].set_top()
        wbf['total_float'].set_bottom()
        wbf['total_float'].set_left()
        wbf['total_float'].set_right()

        wbf['total_number'] = workbook.add_format({'align':'right','bg_color': colors['white_orange'],'bold':1, 'num_format': '#,##0'})
        wbf['total_number'].set_top()
        wbf['total_number'].set_bottom()
        wbf['total_number'].set_left()
        wbf['total_number'].set_right()

        wbf['total'] = workbook.add_format({'bold':1, 'bg_color':colors['white_orange'], 'align':'center'})
        wbf['total'].set_left()
        wbf['total'].set_right()
        wbf['total'].set_top()
        wbf['total'].set_bottom()

        wbf['total_float_yellow'] = workbook.add_format({'bold':1, 'bg_color':colors['yellow'], 'align':'right', 'num_format':'#,##0.00'})
        wbf['total_float_yellow'].set_top()
        wbf['total_float_yellow'].set_bottom()
        wbf['total_float_yellow'].set_left()
        wbf['total_float_yellow'].set_right()

        wbf['total_number_yellow'] = workbook.add_format({'align':'right','bg_color': colors['yellow'],'bold':1, 'num_format': '#,##0'})
        wbf['total_number_yellow'].set_top()
        wbf['total_number_yellow'].set_bottom()
        wbf['total_number_yellow'].set_left()
        wbf['total_number_yellow'].set_right()

        wbf['total_yellow'] = workbook.add_format({'bold':1, 'bg_color':colors['yellow'], 'align':'center'})
        wbf['total_yellow'].set_left()
        wbf['total_yellow'].set_right()
        wbf['total_yellow'].set_top()
        wbf['total_yellow'].set_bottom()

        wbf['total_float_orange'] = workbook.add_format({'bold':1, 'bg_color':colors['orange'], 'align':'right', 'num_format':'#,##0.00'})
        wbf['total_float_orange'].set_top()
        wbf['total_float_orange'].set_bottom()
        wbf['total_float_orange'].set_left()
        wbf['total_float_orange'].set_right()

        wbf['total_number_orange'] = workbook.add_format({'align':'right','bg_color': colors['orange'],'bold':1, 'num_format': '#,##0'})
        wbf['total_number_orange'].set_top()
        wbf['total_number_orange'].set_bottom()
        wbf['total_number_orange'].set_left()
        wbf['total_number_orange'].set_right()

        wbf['total_orange'] = workbook.add_format({'bold':1, 'bg_color':colors['orange'], 'align':'center'})
        wbf['total_orange'].set_left()
        wbf['total_orange'].set_right()
        wbf['total_orange'].set_top()
        wbf['total_orange'].set_bottom()

        wbf['header_detail_space'] = workbook.add_format({})
        wbf['header_detail_space'].set_left()
        wbf['header_detail_space'].set_right()
        wbf['header_detail_space'].set_top()
        wbf['header_detail_space'].set_bottom()

        wbf['header_detail'] = workbook.add_format({'bg_color': '#E0FFC2'})
        wbf['header_detail'].set_left()
        wbf['header_detail'].set_right()
        wbf['header_detail'].set_top()
        wbf['header_detail'].set_bottom()

        wbf['end_content'] = workbook.add_format()
        wbf['end_content'].set_left()
        wbf['end_content'].set_right()
        wbf['end_content'].set_bottom()

        wbf['end_content_float'] = workbook.add_format({'align': 'right','num_format': '#,##0.00'})
        wbf['end_content_float'].set_right()
        wbf['end_content_float'].set_left()
        wbf['end_content_float'].set_bottom()

        return wbf, workbook

    @api.multi
    def action_print(self):
        summary_id = self.env[self._context['active_model']].browse(self._context['active_id'])
        # print("\n summary_id",summary_id.summary_line[:1].history_in_ids._name)
        if self.type == 'detail' :
            report_name = 'Details Stock Summary %s'%summary_id.name
        else:
            if self.history == 'in':
                history_type = 'IN'
            elif self.history == 'out':
                history_type = 'OUT'
            elif self.history == 'return_in':
                history_type = 'Return IN'
            elif self.history == 'return_out':
                history_type = 'Return OUT'
            else:
                history_type = 'ALL'
            report_name = 'History Stock Summary %s (%s)'%(summary_id.name, history_type)
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = self.add_workbook_format(workbook)
        worksheet = workbook.add_worksheet(summary_id.name)

        # konten di sini
        if self.type == 'detail':
            worksheet.set_column('A1:A1', 40)
            worksheet.set_column('B1:B1', 20)
            worksheet.set_column('C1:C1', 20)
            worksheet.set_column('D1:D1', 20)
            worksheet.set_column('E1:E1', 20)
            worksheet.set_column('F1:F1', 20)
            worksheet.set_column('G1:G1', 20)
            worksheet.set_column('J1:J1', 20)
            worksheet.set_column('K1:K1', 20)
            worksheet.set_column('L1:L1', 20)


            worksheet.write('A1', 'Product', wbf['header'])
            worksheet.write('B1', 'Code', wbf['header'])
            worksheet.write('C1', 'Rak No', wbf['header'])
            worksheet.write('D1', 'Start', wbf['header'])
            worksheet.write('E1', 'Qty In', wbf['header'])
            worksheet.write('F1', 'Return In', wbf['header'])
            worksheet.write('G1', 'Qty Out', wbf['header'])
            worksheet.write('H1', 'Return Out', wbf['header'])
            worksheet.write('I1', 'Balance', wbf['header'])
            worksheet.write('J1', 'UOM', wbf['header'])
            worksheet.write('K1', 'HPP', wbf['header'])
            worksheet.write('L1', 'Balance HPP', wbf['header'])


            row = 2
            for line in summary_id.summary_line:
                hpp_balance = 0
                hpp = 0
                rak = ''
                variasi_temp = ''
                supplier = ''
                variasi_temp_cust = ''
                lot_number = ''
                try:
                    if self.env.user.has_group('account.group_account_user'):
                        hpp_balance = line.hpp_balance
                        hpp = line.hpp
                except:
                    pass
                try :
                    rak = line.rak_id.name or ''
                except :
                    pass
                try :
                    variasi_temp = line.variasi_id.name
                    variasi_temp_cust = line.variasi_id.partner_cust_id.name
                    supplier = line.variasi_id.partner_id.name
                except :
                    pass
                try :
                    supplier = line.lot_id.partner_id.name
                except :
                    pass
                try :
                    lot_number = line.lot_id.name
                except :
                    pass
                worksheet.write('A%s' % row, line.product_id.name, wbf['content'])
                worksheet.write('B%s' % row, line.product_code, wbf['content'])
                worksheet.write('C%s' % row, rak, wbf['content'])
                worksheet.write('D%s' % row, line.qty_start, wbf['content_float'])
                worksheet.write('E%s' % row, line.qty_in, wbf['content_float'])
                worksheet.write('F%s' % row, line.return_in, wbf['content_float'])
                worksheet.write('G%s' % row, line.qty_out, wbf['content_float'])
                worksheet.write('H%s' % row, line.return_out, wbf['content_float'])
                worksheet.write('I%s' % row, line.qty_balance, wbf['content_float'])
                worksheet.write('J%s' % row, line.uom_id.name, wbf['content'])
                worksheet.write('K%s' % row, hpp, wbf['content_float'])
                worksheet.write('L%s' % row, hpp_balance, wbf['content_float'])
                row += 1
            worksheet.write('A%s' % (row), 'Total', wbf['total'])
            worksheet.write_formula('B%s' % row, '{=subtotal(9,B2:B%s)}' % (row - 1), wbf['total_float'])
            worksheet.write('C%s' % row, '', wbf['total_float'])
            worksheet.write_formula('D%s' % row, '{=subtotal(9,D2:D%s)}' % (row - 1), wbf['total_float'])
            worksheet.write_formula('E%s' % row, '{=subtotal(9,E2:E%s)}' % (row - 1), wbf['total_float'])
            worksheet.write_formula('F%s' % row, '{=subtotal(9,F2:F%s)}' % (row - 1), wbf['total_float'])
            worksheet.write_formula('G%s' % row, '{=subtotal(9,G2:G%s)}' % (row - 1), wbf['total_float'])
            worksheet.write_formula('H%s' % row, '{=subtotal(9,H2:H%s)}' % (row - 1), wbf['total_float'])
            worksheet.write_formula('I%s' % row, '{=subtotal(9,I2:I%s)}' % (row - 1), wbf['total_float'])
            worksheet.write('J%s' % row, '', wbf['total_float'])
            worksheet.write_formula('K%s' % row, '{=subtotal(9,K2:K%s)}' % (row - 1), wbf['total_float'])
            worksheet.write_formula('L%s' % row, '{=subtotal(9,L2:L%s)}' % (row - 1), wbf['total_float'])

        else :
            worksheet.set_column('A1:A1', 40)
            worksheet.set_column('B1:B1', 20)
            worksheet.set_column('C1:C1', 20)
            worksheet.set_column('D1:D1', 20)
            worksheet.set_column('E1:E1', 20)
            worksheet.set_column('F1:F1', 20)
            worksheet.set_column('G1:G1', 20)
            worksheet.set_column('H1:H1', 20)
            worksheet.set_column('I1:I1', 20)
            worksheet.set_column('J1:J1', 20)
            worksheet.set_column('K1:K1', 20)
            worksheet.set_column('L1:L1', 20)
            worksheet.set_column('M1:M1', 20)
            worksheet.set_column('N1:N1', 20)
            worksheet.set_column('O1:O1', 20)
            worksheet.set_column('P1:P1', 20)

            worksheet.write('A1', 'No Transaksi', wbf['header'])
            worksheet.write('B1', 'Tanggal', wbf['header'])
            worksheet.write('C1', 'Kode Barang', wbf['header'])
            worksheet.write('D1', 'Product', wbf['header'])
            worksheet.write('E1', 'Purchase Order', wbf['header'])
            worksheet.write('F1', 'Supplier', wbf['header'])
            worksheet.write('G1', 'Lot Number', wbf['header'])
            worksheet.write('H1', 'Transaction Type', wbf['header'])
            worksheet.write('I1', 'Qty', wbf['header'])
            worksheet.write('J1', 'Box', wbf['header'])
            worksheet.write('K1', 'Harga', wbf['header'])
            worksheet.write('L1', 'Total', wbf['header'])
            row = 2
            domain = [('summary_id','=',summary_id.id)]
            if self.history == 'in' :
                domain.append(('type','=','in'))
            elif self.history == 'out' :
                domain.append(('type','=','out'))
            elif self.history == 'return_in' :
                domain.append(('type','=','return_in'))
            elif self.history == 'return_out' :
                domain.append(('type','=','return_out'))
            history_ids = self.env[summary_id.summary_line[:1].history_in_ids._name].search(domain)
            for history in history_ids :
                history_dict = history.read()[0]
                print "\n history_dict",history_dict
                worksheet.write('A%s'%row, history.name, wbf['content'])
                worksheet.write('B%s'%row, history.date, wbf['content'])
                worksheet.write('C%s'%row, history.product_code, wbf['content'])
                worksheet.write('D%s'%row, history_dict.get('product_id') and history_dict['product_id'][1] or '', wbf['content'])
                worksheet.write('E%s'%row, history_dict.get('purchase_id') and history_dict['purchase_id'][1] or '', wbf['content'])
                worksheet.write('F%s'%row, history_dict.get('supplier_id') and history_dict['supplier_id'][1] or '', wbf['content'])
                worksheet.write('G%s'%row, history_dict.get('lot_id') and history_dict['lot_id'][1] or '', wbf['content'])
                worksheet.write('H%s'%row, history_dict.get('picking_type_id') and history_dict['picking_type_id'][1] or '', wbf['content'])
                worksheet.write('I%s'%row, history.qty, wbf['content_float'])
                worksheet.write('J%s'%row, history_dict.get('box',0), wbf['content_float'])
                worksheet.write('K%s'%row, history.price, wbf['content_float'])
                worksheet.write('L%s'%row, history.total, wbf['content_float'])
                row += 1
            worksheet.merge_range('A%s:H%s'%(row,row), 'Total', wbf['total'])
            worksheet.write_formula('I%s' %row, '{=subtotal(9,I2:I%s)}'%(row-1), wbf['total_float'])
            worksheet.write_formula('J%s' %row, '{=subtotal(9,J2:J%s)}'%(row-1), wbf['total_float'])
            worksheet.write_formula('K%s' %row, '{=subtotal(9,K2:K%s)}'%(row-1), wbf['total_float'])
            worksheet.write_formula('L%s' % row, '{=subtotal(9,L2:L%s)}' % (row - 1), wbf['total_float'])
        #sampai sini

        workbook.close()
        result = base64.encodestring(fp.getvalue())
        date_string = self.get_default_date_model().strftime("%Y-%m-%d")
        filename = '%s %s'%(report_name, date_string)
        filename += '%2Exlsx'
        self.write({'file_data':result})
        url = "web/content/?model="+self._name+"&id="+str(self.id)+"&field=file_data&download=true&filename="+filename
        print (url)
        return {
            'name': 'Stock Summary',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    @api.multi
    def action_print_benang(self):
        summary_id = self.env[self._context['active_model']].browse(self._context['active_id'])
        print("--------")
        print(summary_id)
        print(self._context)
        print("--------")
        if self.type == 'detail' :
            report_name = 'Details Stock Summary %s'%summary_id.name
        else:
            if self.history == 'in':
                history_type = 'IN'
            elif self.history == 'out':
                history_type = 'OUT'
            elif self.history == 'return_in':
                history_type = 'Return IN'
            elif self.history == 'return_out':
                history_type = 'Return OUT'
            else:
                history_type = 'ALL'
            report_name = 'History Stock Summary %s (%s)'%(summary_id.name, history_type)
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = self.add_workbook_format(workbook)
        worksheet = workbook.add_worksheet(summary_id.name)

        # konten di sini
        if self.type == 'detail':
            worksheet.set_column('A1:A1', 40)
            worksheet.set_column('B1:T1', 30)

            # worksheet.set_column('B1:B1', 20)
            # worksheet.set_column('C1:C1', 20)
            # worksheet.set_column('D1:D1', 20)
            # worksheet.set_column('E1:E1', 20)
            # worksheet.set_column('F1:F1', 20)
            # worksheet.set_column('G1:G1', 20)
            # worksheet.set_column('J1:J1', 20)
            # worksheet.set_column('K1:K1', 20)
            # worksheet.set_column('L1:L1', 20)


            row = 1

            worksheet.merge_range('A%s:D%s' % (row,row), 'Product', wbf['header'])
            worksheet.merge_range('E%s:F%s' % (row,row), 'Begining Balance', wbf['header'])
            worksheet.merge_range('G%s:H%s' % (row,row), 'Receive From PO', wbf['header'])
            worksheet.merge_range('I%s:J%s' % (row,row), 'Return Makloon', wbf['header'])
            worksheet.merge_range('K%s:L%s' % (row,row), 'Return From Production', wbf['header'])
            worksheet.merge_range('M%s:N%s' % (row,row), 'Release Makloon', wbf['header'])
            worksheet.merge_range('O%s:P%s' % (row,row), 'Release To Production', wbf['header'])
            worksheet.merge_range('Q%s:R%s' % (row,row), 'Ending Balance', wbf['header'])
            worksheet.merge_range('S%s:T%s' % (row,row), 'HPP', wbf['header'])

            row += 1

            worksheet.write('A%s' % (row), 'Product Name', wbf['header'])
            worksheet.write('B%s' % (row), 'Code', wbf['header'])
            worksheet.write('C%s' % (row), 'UOM', wbf['header'])
            worksheet.write('D%s' % (row), 'Rak No', wbf['header'])
            # worksheet.write('B%s' % (row), 'UoM', wbf['header'])
            # worksheet.write('C%s' % (row), 'Lot', wbf['header'])
            # worksheet.write('D%s' % (row), 'Supplier', wbf['header'])
            worksheet.write('E%s' % (row), 'Qty', wbf['header'])
            worksheet.write('F%s' % (row), 'Other', wbf['header'])
            worksheet.write('G%s' % (row), 'Qty', wbf['header'])
            worksheet.write('H%s' % (row), 'Other', wbf['header'])
            worksheet.write('I%s' % (row), 'Qty', wbf['header'])
            worksheet.write('J%s' % (row), 'Other', wbf['header'])
            worksheet.write('K%s' % (row), 'Qty', wbf['header'])
            worksheet.write('L%s' % (row), 'Other', wbf['header'])
            worksheet.write('M%s' % (row), 'Qty', wbf['header'])
            worksheet.write('N%s' % (row), 'Other', wbf['header'])
            worksheet.write('O%s' % (row), 'Qty', wbf['header'])
            worksheet.write('P%s' % (row), 'Other', wbf['header'])
            worksheet.write('Q%s' % (row), 'Qty', wbf['header'])
            worksheet.write('R%s' % (row), 'Other', wbf['header'])
            worksheet.write('S%s' % (row), 'HPP', wbf['header'])
            worksheet.write('T%s' % (row), 'Balance', wbf['header'])

            row += 1
            start_row = row
            # row = 2
            for line in summary_id.summary_line:
                hpp_balance = 0
                hpp = 0
                rak = ''
                variasi_temp = ''
                supplier = ''
                variasi_temp_cust = ''
                lot_number = ''
                try:
                    if self.env.user.has_group('account.group_account_user'):
                        hpp_balance = line.hpp_balance
                        hpp = line.hpp
                except:
                    pass
                try :
                    rak = line.rak_id.name or ''
                except :
                    pass
                try :
                    variasi_temp = line.variasi_id.name
                    variasi_temp_cust = line.variasi_id.partner_cust_id.name
                    supplier = line.variasi_id.partner_id.name
                except :
                    pass
                try :
                    supplier = line.lot_id.partner_id.name
                except :
                    pass
                try :
                    lot_number = line.lot_id.name
                except :
                    pass
                # worksheet.write('A%s' % row, line.product_id.name, wbf['content'])
                # worksheet.write('B%s' % row, line.product_code, wbf['content'])
                # worksheet.write('C%s' % row, rak, wbf['content'])
                # worksheet.write('D%s' % row, line.qty_start, wbf['content_float'])
                # worksheet.write('E%s' % row, line.qty_in, wbf['content_float'])
                # worksheet.write('F%s' % row, line.return_in, wbf['content_float'])
                # worksheet.write('G%s' % row, line.qty_out, wbf['content_float'])
                # worksheet.write('H%s' % row, line.return_out, wbf['content_float'])
                # worksheet.write('I%s' % row, line.qty_balance, wbf['content_float'])
                # worksheet.write('J%s' % row, line.uom_id.name, wbf['content'])
                # worksheet.write('K%s' % row, hpp, wbf['content_float'])
                # worksheet.write('L%s' % row, hpp_balance, wbf['content_float'])

                worksheet.write('A%s' % row, line.product_id.name, wbf['content'])
                worksheet.write('B%s' % row, line.product_code, wbf['content'])
                worksheet.write('C%s' % row, rak, wbf['content'])
                worksheet.write('D%s' % row, line.uom_id.name, wbf['content'])
                worksheet.write('E%s' % row, line.qty_start, wbf['content_float'])
                worksheet.write('F%s' % row, line.box_in, wbf['content_float'])
                worksheet.write('G%s' % row, line.po_qty, wbf['content_float'])
                worksheet.write('H%s' % row, line.po_other, wbf['content_float'])
                worksheet.write('I%s' % row, line.return_makloon_qty, wbf['content_float'])
                worksheet.write('J%s' % row, line.return_makloon_other, wbf['content_float'])
                worksheet.write('K%s' % row, line.return_prod_qty, wbf['content_float'])
                worksheet.write('L%s' % row, line.return_prod_other, wbf['content_float'])
                worksheet.write('M%s' % row, line.makloon_qty, wbf['content_float'])
                worksheet.write('N%s' % row, line.makloon_other, wbf['content_float'])
                worksheet.write('O%s' % row, line.prod_qty, wbf['content_float'])
                worksheet.write('P%s' % row, line.prod_other, wbf['content_float'])
                worksheet.write('Q%s' % row, line.qty_balance, wbf['content_float'])
                worksheet.write('R%s' % row, line.box_balance, wbf['content_float'])
                worksheet.write('S%s' % row, hpp, wbf['content'])
                worksheet.write('T%s' % row, hpp_balance, wbf['content'])
                row += 1
            # worksheet.write('A%s' % (row), 'Total', wbf['total'])
            # worksheet.write_formula('B%s' % row, '{=subtotal(9,B2:B%s)}' % (row - 1), wbf['total_float'])
            # worksheet.write('C%s' % row, '', wbf['total_float'])
            # worksheet.write_formula('D%s' % row, '{=subtotal(9,D2:D%s)}' % (row - 1), wbf['total_float'])
            # worksheet.write_formula('E%s' % row, '{=subtotal(9,E2:E%s)}' % (row - 1), wbf['total_float'])
            # worksheet.write_formula('F%s' % row, '{=subtotal(9,F2:F%s)}' % (row - 1), wbf['total_float'])
            # worksheet.write_formula('G%s' % row, '{=subtotal(9,G2:G%s)}' % (row - 1), wbf['total_float'])
            # worksheet.write_formula('H%s' % row, '{=subtotal(9,H2:H%s)}' % (row - 1), wbf['total_float'])
            # worksheet.write_formula('I%s' % row, '{=subtotal(9,I2:I%s)}' % (row - 1), wbf['total_float'])
            # worksheet.write('J%s' % row, '', wbf['total_float'])
            # worksheet.write_formula('K%s' % row, '{=subtotal(9,K2:K%s)}' % (row - 1), wbf['total_float'])
            # worksheet.write_formula('L%s' % row, '{=subtotal(9,L2:L%s)}' % (row - 1), wbf['total_float'])


        workbook.close()
        result = base64.encodestring(fp.getvalue())
        date_string = self.get_default_date_model().strftime("%Y-%m-%d")
        filename = '%s %s'%(report_name, date_string)
        filename += '%2Exlsx'
        self.write({'file_data':result})
        url = "web/content/?model="+self._name+"&id="+str(self.id)+"&field=file_data&download=true&filename="+filename
        return {
            'name': 'Stock Summary',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    @api.multi
    def action_print_batch(self):
        summary_id = self.env[self._context['active_model']].browse(self._context['active_id'])
        if self.type == 'detail' :
            report_name = 'Details Stock Summary %s'%summary_id.location_id.display_name
        else:
            if self.history == 'in':
                history_type = 'IN'
            elif self.history == 'out':
                history_type = 'OUT'
            elif self.history == 'return_in':
                history_type = 'Return IN'
            elif self.history == 'return_out':
                history_type = 'Return OUT'
            else:
                history_type = 'ALL'
            report_name = 'History Stock Summary %s (%s)'%(summary_id.location_id.display_name, history_type)
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = self.add_workbook_format(workbook)
        worksheet = workbook.add_worksheet(summary_id.location_id.display_name)

        if self.type == 'detail':
            worksheet.set_column('A1:A1', 40)
            worksheet.set_column('B1:P1', 30)
            row = 1
            worksheet.merge_range('A%s:B%s' % (row,row), 'Product', wbf['header'])
            worksheet.merge_range('C%s:D%s' % (row,row), 'Begining Balance', wbf['header'])
            worksheet.merge_range('E%s:F%s' % (row,row), 'Receive', wbf['header'])
            worksheet.merge_range('G%s:H%s' % (row,row), 'Return In', wbf['header'])
            worksheet.merge_range('I%s:J%s' % (row,row), 'Release', wbf['header'])
            worksheet.merge_range('K%s:L%s' % (row,row), 'Return Out', wbf['header'])
            worksheet.merge_range('M%s:N%s' % (row,row), 'Adjustmenr', wbf['header'])
            worksheet.merge_range('O%s:P%s' % (row,row), 'Ending Balance', wbf['header'])
            row += 1
            worksheet.write('A%s' % (row), 'Product Name', wbf['header'])
            worksheet.write('B%s' % (row), 'No Batch', wbf['header'])
            worksheet.write('C%s' % (row), 'Qty', wbf['header'])
            worksheet.write('D%s' % (row), 'Other', wbf['header'])
            worksheet.write('E%s' % (row), 'Qty', wbf['header'])
            worksheet.write('F%s' % (row), 'Other', wbf['header'])
            worksheet.write('G%s' % (row), 'Qty', wbf['header'])
            worksheet.write('H%s' % (row), 'Other', wbf['header'])
            worksheet.write('I%s' % (row), 'Qty', wbf['header'])
            worksheet.write('J%s' % (row), 'Other', wbf['header'])
            worksheet.write('K%s' % (row), 'Qty', wbf['header'])
            worksheet.write('L%s' % (row), 'Other', wbf['header'])
            worksheet.write('M%s' % (row), 'Qty', wbf['header'])
            worksheet.write('N%s' % (row), 'Other', wbf['header'])
            worksheet.write('O%s' % (row), 'Qty', wbf['header'])
            worksheet.write('P%s' % (row), 'Other', wbf['header'])
            row += 1
            start_row = row
            for line in summary_id.stock_summary_line_2:
                worksheet.write('A%s' % row, line.product_id.name, wbf['content'])
                worksheet.write('B%s' % row, line.no_batch, wbf['content'])
                worksheet.write('C%s' % row, line.saldo_awal_qty, wbf['content_float'])
                worksheet.write('D%s' % row, line.saldo_awal_pcs, wbf['content_float'])
                worksheet.write('E%s' % row, line.terima_qty, wbf['content_float'])
                worksheet.write('F%s' % row, line.terima_pcs, wbf['content_float'])
                worksheet.write('G%s' % row, line.retur_terima_qty, wbf['content_float'])
                worksheet.write('H%s' % row, line.retur_terima_pcs, wbf['content_float'])
                worksheet.write('I%s' % row, line.keluar_qty, wbf['content_float'])
                worksheet.write('J%s' % row, line.keluar_pcs, wbf['content_float'])
                worksheet.write('K%s' % row, line.retur_keluar_qty, wbf['content_float'])
                worksheet.write('L%s' % row, line.retur_keluar_pcs, wbf['content_float'])
                worksheet.write('M%s' % row, line.adj_qty, wbf['content_float'])
                worksheet.write('N%s' % row, line.adj_pcs, wbf['content_float'])
                worksheet.write('O%s' % row, line.balance_qty, wbf['content_float'])
                worksheet.write('P%s' % row, line.balance_pcs, wbf['content_float'])
                row += 1
        else :
            worksheet.set_column('A1:A1', 40)
            worksheet.set_column('B1:B1', 20)
            worksheet.set_column('C1:G1', 40)
            worksheet.set_column('H1:H1', 20)
            worksheet.set_column('I1:I1', 20)
            worksheet.set_column('J1:J1', 20)
            worksheet.set_column('K1:K1', 20)

            worksheet.write('A1', 'No Transaksi', wbf['header'])
            worksheet.write('B1', 'Tanggal', wbf['header'])
            worksheet.write('C1', 'Partner', wbf['header'])
            worksheet.write('D1', 'Source Location', wbf['header'])
            worksheet.write('E1', 'Destination Location', wbf['header'])
            worksheet.write('F1', 'Picking Type', wbf['header'])
            worksheet.write('G1', 'Product', wbf['header'])
            worksheet.write('H1', 'No Batch', wbf['header'])
            worksheet.write('I1', 'Lot', wbf['header'])
            worksheet.write('J1', 'Qty', wbf['header'])
            worksheet.write('K1', 'Pcs', wbf['header'])
            row = 2
            domain = [('order_in_id','=',summary_id.id)]

            if self.history == 'in' :
                domain.append(('picking_type_id','=',13))
            elif self.history == 'out' :
                domain.append(('picking_type_id','=',16))
            elif self.history == 'return_in' :
                domain.append(('picking_type_id','=',135))
            elif self.history == 'return_out' :
                domain.append(('picking_type_id','=',136))
            elif self.history in ['revision_in','revision_out']:
                raise ValidationError("Tidak ada report untuk Revision")

            history_ids = self.env['tj.summary.batch.line.history'].search(domain)

            for history in history_ids :
                worksheet.write('A%s'%row, history.picking_id.name, wbf['content'])
                worksheet.write('B%s'%row, history.min_date, wbf['content'])
                worksheet.write('C%s'%row, history.partner_id.display_name, wbf['content'])
                worksheet.write('D%s'%row, history.location_id.display_name, wbf['content'])
                worksheet.write('E%s'%row, history.location_dest_id.display_name, wbf['content'])
                worksheet.write('F%s'%row, history.picking_type_id.display_name, wbf['content'])
                worksheet.write('G%s'%row, history.product_id.display_name, wbf['content'])
                worksheet.write('H%s'%row, history.no_batch, wbf['content'])
                worksheet.write('I%s'%row, history.lot_id.display_name, wbf['content'])
                worksheet.write('J%s'%row, history.qty, wbf['content_float'])
                worksheet.write('K%s'%row, history.pcs, wbf['content_float'])
                row += 1

        workbook.close()
        result = base64.encodestring(fp.getvalue())
        date_string = self.get_default_date_model().strftime("%Y-%m-%d")
        filename = '%s %s'%(report_name, date_string)
        filename += '%2Exlsx'
        self.write({'file_data':result})
        url = "web/content/?model="+self._name+"&id="+str(self.id)+"&field=file_data&download=true&filename="+filename
        return {
            'name': 'Stock Summary',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }