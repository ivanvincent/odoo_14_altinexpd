from odoo import fields, models, api, _
from odoo.exceptions import UserError

# class AddWorkBookFormat():

def add_workbook_format(workbook):
    colors = {
        'white_orange': '#FFFFDB',
        'orange': '#FF  C300',
        'red': '#FF0000',
        'yellow': '#F6FA03',
        'white': '#FFFFFF'
    }

    wbf = {}

    wbf['header'] = workbook.add_format(
        {'bold': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#FFFFFF', 'font_color': '#000000'})
    wbf['header'].set_border()
    
    wbf['format_judul'] = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'fg_color': 'white'})
    wbf['format_judul'].set_font_size(18)

    wbf['content_left'] = workbook.add_format({'border': 1, 'align': 'left'})

    wbf['content_center'] = workbook.add_format({'border': 1, 'align': 'center'})

    wbf['content_float'] = workbook.add_format({'border': 1, 'align': 'right', 'num_format': '#,##0.00'})

    wbf['merge_format'] = workbook.add_format({'bold': 1,   'border': 0, 'align': 'center', 'valign': 'vcenter', 'fg_color': 'white'})
    wbf['merge_format'].set_font_size(16)

    wbf['merge_format_2'] = workbook.add_format({'bold': 1,   'border': 0, 'align': 'center', 'valign': 'vcenter', 'fg_color': 'white'})
    wbf['merge_format_2'].set_font_size(11)

    return wbf, workbook
