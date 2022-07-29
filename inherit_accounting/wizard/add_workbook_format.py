from odoo import fields, models, api, _
from odoo.exceptions import UserError

# class AddWorkBookFormat():

def add_workbook_format(workbook):
    colors = {
        'white_orange': '#FFFFDB',
        'orange': '#FFC300',
        'red': '#FF0000',
        'yellow': '#F6FA03',
        'white': '#FFFFFF'
    }

    wbf = {}
    wbf['header'] = workbook.add_format(
        {'bold': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#FFFFFF', 'font_color': '#000000'})
    wbf['header'].set_border()

    wbf['header_orange'] = workbook.add_format(
        {'bold': 1, 'align': 'center', 'bg_color': colors['orange'], 'font_color': '#000000'})
    wbf['header_orange'].set_border()

    wbf['header_yellow'] = workbook.add_format(
        {'bold': 1, 'align': 'center', 'bg_color': colors['yellow'], 'font_color': '#000000'})
    wbf['header_yellow'].set_border()

    wbf['header_no'] = workbook.add_format(
        {'bold': 1, 'align': 'center', 'bg_color': '#FFFFDB', 'font_color': '#000000'})
    wbf['header_no'].set_border()
    wbf['header_no'].set_align('vcenter')

    wbf['footer'] = workbook.add_format({'align': 'left'})

    wbf['content_datetime'] = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
    wbf['content_datetime'].set_left()
    wbf['content_datetime'].set_right()

    wbf['content_date'] = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    wbf['content_date'].set_left()
    wbf['content_date'].set_right()

    wbf['title_doc'] = workbook.add_format({'bold': 1, 'align': 'left'})
    wbf['title_doc'].set_font_size(12)

    wbf['company'] = workbook.add_format({'align': 'left'})
    wbf['company'].set_font_size(11)

    wbf['content'] = workbook.add_format()
    wbf['content'].set_left()
    wbf['content'].set_right()

    wbf['content_center'] = workbook.add_format({'align': 'center'})
    wbf['content_center'].set_left()
    wbf['content_center'].set_right()

    wbf['content_float'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00'})
    # wbf['content_float'].set_right()
    # wbf['content_float'].set_left()

    wbf['content_number'] = workbook.add_format({'align': 'right', 'num_format': '#,##0'})
    wbf['content_number'].set_right()
    wbf['content_number'].set_left()

    wbf['content_number_center'] = workbook.add_format({'align': 'center', 'num_format': '#,##0'})
    wbf['content_number_center'].set_right()
    wbf['content_number_center'].set_left()

    wbf['content_number_noborder'] = workbook.add_format({'align': 'left', 'num_format': '#,##0'})
    # wbf['content_number_noborder'].set_right()
    # wbf['content_number_noborder'].set_left()

    wbf['content_percent'] = workbook.add_format({'align': 'right', 'num_format': '0.00%'})
    wbf['content_percent'].set_right()
    wbf['content_percent'].set_left()

    wbf['total_float'] = workbook.add_format(
        {'bold': 1, 'bg_color': colors['white'], 'align': 'right', 'num_format': '#,##0.00'})
    wbf['total_float'].set_top()
    wbf['total_float'].set_bottom()
    wbf['total_float'].set_left()
    wbf['total_float'].set_right()

    wbf['total_number'] = workbook.add_format(
        {'align': 'left', 'bg_color': colors['white'], 'bold': 1, 'num_format': '#,##0'})
    wbf['total_number'].set_top()
    wbf['total_number'].set_bottom()
    wbf['total_number'].set_left()
    wbf['total_number'].set_right()

    wbf['total'] = workbook.add_format({'bold': 1, 'bg_color': colors['white_orange'], 'align': 'center'})
    wbf['total'].set_left()
    wbf['total'].set_right()
    wbf['total'].set_top()
    wbf['total'].set_bottom()

    wbf['total_float_yellow'] = workbook.add_format(
        {'bold': 1, 'bg_color': colors['yellow'], 'align': 'right', 'num_format': '#,##0.00'})
    wbf['total_float_yellow'].set_top()
    wbf['total_float_yellow'].set_bottom()
    wbf['total_float_yellow'].set_left()
    wbf['total_float_yellow'].set_right()

    wbf['total_number_yellow'] = workbook.add_format(
        {'align': 'right', 'bg_color': colors['yellow'], 'bold': 1, 'num_format': '#,##0'})
    wbf['total_number_yellow'].set_top()
    wbf['total_number_yellow'].set_bottom()
    wbf['total_number_yellow'].set_left()
    wbf['total_number_yellow'].set_right()

    wbf['total_yellow'] = workbook.add_format({'bold': 1, 'bg_color': colors['yellow'], 'align': 'center'})
    wbf['total_yellow'].set_left()
    wbf['total_yellow'].set_right()
    wbf['total_yellow'].set_top()
    wbf['total_yellow'].set_bottom()

    wbf['total_float_orange'] = workbook.add_format(
        {'bold': 1, 'bg_color': colors['orange'], 'align': 'right', 'num_format': '#,##0.00'})
    wbf['total_float_orange'].set_top()
    wbf['total_float_orange'].set_bottom()
    wbf['total_float_orange'].set_left()
    wbf['total_float_orange'].set_right()

    wbf['total_number_orange'] = workbook.add_format(
        {'align': 'right', 'bg_color': colors['orange'], 'bold': 1, 'num_format': '#,##0'})
    wbf['total_number_orange'].set_top()
    wbf['total_number_orange'].set_bottom()
    wbf['total_number_orange'].set_left()
    wbf['total_number_orange'].set_right()

    wbf['total_orange'] = workbook.add_format({'bold': 1, 'bg_color': colors['orange'], 'align': 'center'})
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


    wbf['merge_format'] = workbook.add_format({'bold': 1,   'border': 0, 'align': 'center', 'valign': 'vcenter', 'fg_color': 'white'})
    wbf['merge_format'].set_font_size(16)

    wbf['merge_format_2'] = workbook.add_format({'bold': 1,   'border': 0, 'align': 'center', 'valign': 'vcenter', 'fg_color': 'white'})
    wbf['merge_format_2'].set_font_size(11)

    wbf['merge_format_3'] = workbook.add_format({'bold': 1,   'border': 0, 'align': 'left', 'fg_color': 'white'})
    wbf['merge_format_3'].set_font_size(13)

    wbf['merge_format_border'] = workbook.add_format({'bold': 1,   'border': 0, 'align': 'center', 'valign': 'vcenter', 'fg_color': 'white'})
    wbf['merge_format_border'].set_font_size(12)
    wbf['merge_format_border'].set_border()

    return wbf, workbook
