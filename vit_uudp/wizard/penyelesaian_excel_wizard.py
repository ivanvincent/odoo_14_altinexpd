from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import xlsxwriter
from io import BytesIO
import base64
import pandas as pd
from ...reporting.wizard import add_workbook_format as awf

class PenyelesaianExcelWizard(models.TransientModel):
    _name = 'penyelesaian.excel.wizard'

    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')
    data = fields.Binary(string='Data')

    def action_export(self):
        fp                = BytesIO()
        date_string       = datetime.now().strftime("%Y-%m-%d")
        workbook          = xlsxwriter.Workbook(fp)
        wbf, workbook     = awf.add_workbook_format(workbook)

        # WKS 1
        report_name       = 'LAPORAN REALISASI KASBON';
        writer            = pd.ExcelWriter(fp,engine='xlsxwriter')
        columns_by_drop   = ['TANGGAL KASBON', 'TANGGAL KEMBALI', 'NO BUKTI', 'KASBON', 'NAMA SALES', 'NAMA SOPIR', 'NAMA KENEK', 'STOCK POINT', 'JALUR', 'NO MOBIL', 'JENIS MOBIL', 'NO BKB', 'KM AWAL', 'KM AKHIR', 'SISA KASBON', 'BBM CASH', 'TOL', 'UANG MAKAN', 'PARKIR', 'TPR OGAH', 'KEAMANAN']
        columns_by_global = ['TANGGAL KASBON', 'TANGGAL KEMBALI', 'NO BUKTI', 'KASBON', 'NAMA SALES', 'NAMA SOPIR', 'NAMA KENEK', 'STOCK POINT', 'JALUR', 'NO MOBIL', 'JENIS MOBIL', 'NO BKB', 'KM AWAL', 'KM AKHIR', 'SISA KASBON', 'BBM CASH', 'TOL', 'UANG MAKAN', 'PARKIR', 'TPR OGAH', 'KEAMANAN']
        columns_by_gt     = ['TANGGAL KASBON', 'TANGGAL KEMBALI', 'NO BUKTI', 'KASBON', 'NAMA SALES', 'NAMA SOPIR', 'NAMA KENEK', 'STOCK POINT', 'JALUR', 'NO MOBIL', 'JENIS MOBIL', 'NO BKB', 'KM AWAL', 'KM AKHIR', 'SISA KASBON', 'BBM CASH', 'TOL', 'UANG MAKAN', 'PARKIR', 'TPR OGAH', 'KEAMANAN']
        columns_by_mt     = ['TANGGAL KASBON', 'TANGGAL KEMBALI', 'NO BUKTI', 'KASBON', 'NAMA SALES', 'NAMA SOPIR', 'NAMA KENEK', 'STOCK POINT', 'JALUR', 'NO MOBIL', 'JENIS MOBIL', 'NO BKB', 'KM AWAL', 'KM AKHIR', 'SISA KASBON', 'BBM CASH', 'TOL', 'UANG MAKAN', 'PARKIR', 'TPR OGAH', 'KEAMANAN']
        sheet_by_drop     = "DROP"
        sheet_by_global   = "KOMBINASI"
        sheet_by_mt       = "MT"
        sheet_by_gt       = "GT"
        formatted         = [{column: '' for column in columns_by_gt}]
        data_drop         = self.get_report_drop()
        data_mt           = self.get_report_mt()
        data_gt           = self.get_report_gt()
        data_global       = self.get_report_global()
        import logging;
        _logger = logging.getLogger(__name__)
        # df_by_gt          = pd.DataFrame(data_gt) if len(data_gt) > 0 else pd.DataFrame.from_dict(formatted)
        # df_by_mt          = pd.DataFrame(data_mt) if len(data_mt) > 0 else pd.DataFrame.from_dict(formatted)
        # df_by_drop        = pd.DataFrame(data_drop) if len(data_drop) > 0 else pd.DataFrame.from_dict(formatted)
        # df_by_global      = pd.DataFrame(data_global) if len(data_global) > 0 else pd.DataFrame.from_dict(formatted)
        df_by_gt          = pd.DataFrame(data_gt) if data_gt else pd.DataFrame(formatted)
        df_by_mt          = pd.DataFrame(data_mt) if data_mt else pd.DataFrame(formatted)
        df_by_drop        = pd.DataFrame(data_drop) if data_drop else pd.DataFrame(formatted)
        df_by_global      = pd.DataFrame(data_global) if data_drop else pd.DataFrame(formatted)
        # df_by_gt          = pd.DataFrame(data_gt)
        # df_by_mt          = pd.DataFrame(data_mt)
        # df_by_drop        = pd.DataFrame(data_drop)
        # df_by_global      = pd.DataFrame(data_global)
        start_row         = 4

        df_by_drop.to_excel(writer, sheet_name=sheet_by_drop,
                    index=False,header=False,
                    startrow=start_row,columns=columns_by_drop,
                    float_format='%.2f',
                    merge_cells=True)
        worksheet_by_drop = writer.sheets[sheet_by_drop]


        df_by_gt.to_excel(writer, sheet_name=sheet_by_gt,
                    index=False,header=False,
                    startrow=start_row,columns=columns_by_gt,
                    float_format='%.2f',
                    merge_cells=True)
        worksheet_by_gt = writer.sheets[sheet_by_gt]


        df_by_mt.to_excel(writer, sheet_name=sheet_by_mt,
                    index=False,header=False,
                    startrow=start_row,columns=columns_by_mt,
                    float_format='%.2f',
                    merge_cells=True)
        worksheet_by_mt = writer.sheets[sheet_by_mt]

        df_by_global.to_excel(writer, sheet_name=sheet_by_global,
                    index=False,header=False,
                    startrow=start_row,columns=columns_by_global,
                    float_format='%.2f',
                    merge_cells=True)
        worksheet_by_global = writer.sheets[sheet_by_global]


        worksheet_by_drop.merge_range('A1:U2','LAPORAN DROP ' + '(' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['format_judul'])
        worksheet_by_global.merge_range('A1:U2','LAPORAN KOMBINASI ' + '(' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['format_judul'])
        worksheet_by_gt.merge_range('A1:U2','LAPORAN GT ' + '(' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['format_judul'])
        worksheet_by_mt.merge_range('A1:U2','LAPORAN MT ' + '(' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['format_judul'])
        # merge = workbook.add_format({'border': 0, 'valign': 'vcenter','align': 'center',  'fg_color': 'white'})



        workbook = writer.book
        wbf, workbook = awf.add_workbook_format(workbook)

        for col_num, value in enumerate(columns_by_drop):
            worksheet_by_drop.write(3, col_num, value, wbf['header'])
            column_len = df_by_drop[value].astype(str).str.len().max()
            column_len = max(column_len, len(value)) + 3
            worksheet_by_drop.set_column(col_num, col_num, column_len)

        for col_num, value in enumerate(columns_by_global):
            worksheet_by_global.write(3, col_num, value, wbf['header'])
            column_len = df_by_global[value].astype(str).str.len().max()
            column_len = max(column_len, len(value)) + 3
            worksheet_by_global.set_column(col_num, col_num, column_len)

        for col_num, value in enumerate(columns_by_mt):
            worksheet_by_mt.write(3, col_num, value, wbf['header'])
            column_len = df_by_mt[value].astype(str).str.len().max()
            column_len = max(column_len, len(value)) + 3
            worksheet_by_mt.set_column(col_num, col_num, column_len)


        for col_num, value in enumerate(columns_by_gt):
            worksheet_by_gt.write(3, col_num, value, wbf['header'])
            column_len = df_by_gt[value].astype(str).str.len().max()
            column_len = max(column_len, len(value)) + 3
            worksheet_by_gt.set_column(col_num, col_num, column_len)


        border_fmt = workbook.add_format({'bold':True,'bottom':1, 'top':1, 'left':1, 'right':1})
        worksheet_by_drop.conditional_format(xlsxwriter.utility.xl_range(3, 0, len(df_by_drop) +3, start_row + 16), {'type': 'no_errors', 'format': border_fmt})
        worksheet_by_global.conditional_format(xlsxwriter.utility.xl_range(3, 0, len(df_by_global) +3, start_row + 16), {'type': 'no_errors', 'format': border_fmt})
        worksheet_by_gt.conditional_format(xlsxwriter.utility.xl_range(3, 0, len(df_by_gt) +3, start_row + 16), {'type': 'no_errors', 'format': border_fmt})
        worksheet_by_mt.conditional_format(xlsxwriter.utility.xl_range(3, 0, len(df_by_mt) +3, start_row + 16), {'type': 'no_errors', 'format': border_fmt})

        writer.save()
        writer.close()

        filename = '%s %s%s' % (report_name, date_string, '.xlsx')
        workbook.close()
        out = base64.encodestring(fp.getvalue())
        # self.write({'data': out})
        fp.close()

        self.write({'data': out})
        url = "web/content/?model=" + self._name + "&id=" + str(self.id) + "&field=data&download=true&filename=" + filename
        result = {
            'name'      : 'Report XLSX',
            'type'      : 'ir.actions.act_url',
            'url'       : url,
            'target'    : 'download',
        }
        return result



    def get_report_gt(self):
        query = """
            SELECT
                tgl_kasbon as "TANGGAL KASBON",
                tgl_kembali as "TANGGAL KEMBALI",
                no_bukti as "NO BUKTI",
                kasbon as "KASBON",
                nama_sales as "NAMA SALES",
                sopir as "NAMA SOPIR",
                nama_kenek as "NAMA KENEK",
                stock_point as "STOCK POINT",
                jalur as "JALUR",
                no_mobil as "NO MOBIL",
                jenis_mobil as "JENIS MOBIL",
                no_bkb as "NO BKB",
                km_awal as "KM AWAL",
                km_akhir as "KM AKHIR",
                sisa_kasbon as "SISA KASBON",
                sum(bbm_cash) as "BBM CASH",
                sum(tol) as "TOL",
                sum(uang_makan) as "UANG MAKAN",
                sum(parkir) as "PARKIR",
                sum(tpr_ogah) as "TPR OGAH",
                sum(keamanan) as "KEAMANAN"
                FROM (
            SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                k.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
				left JOIN res_partner_jalur k on r.res_partner_jalur_id = k.id
                left JOIN customer_type c ON k.customer_type = c.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'customer'
                and c.id = 13
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                k.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                l.sub_total as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
				left JOIN res_partner_jalur k on r.res_partner_jalur_id = k.id
                left JOIN customer_type c ON k.customer_type = c.id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'customer'
                AND l.exp_id = 14 --BBM
                and c.id = 13 
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                k.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_Akhir,
                0 as bbm_cash,
                l.sub_total as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
				left JOIN res_partner_jalur k on r.res_partner_jalur_id = k.id
                left JOIN customer_type c ON k.customer_type = c.id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'customer'
                AND l.exp_id = 25 --TOL
                and c.id = 13 
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                k.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                l.sub_total as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
				left JOIN res_partner_jalur k on r.res_partner_jalur_id = k.id
                left JOIN customer_type c ON k.customer_type = c.id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'customer'
                AND l.exp_id = 26 --UANGMAKAN
                and c.id = 13 
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                k.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                l.sub_total as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
				left JOIN res_partner_jalur k on r.res_partner_jalur_id = k.id
                left JOIN customer_type c ON k.customer_type = c.id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'customer'
                AND l.exp_id = 22 --PARKIR
                and c.id = 13 
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                k.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                l.sub_total as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
				left JOIN res_partner_jalur k on r.res_partner_jalur_id = k.id
                left JOIN customer_type c ON k.customer_type = c.id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'customer'
                AND l.exp_id = 21 --OGAH
                and c.id = 13 
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                k.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                l.sub_total as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
				left JOIN res_partner_jalur k on r.res_partner_jalur_id = k.id
                left JOIN customer_type c ON k.customer_type = c.id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'customer'
                AND l.exp_id = 18
                and c.id = 13 
                ) as k GROUP BY tgl_kasbon,
                tgl_kembali,
                no_bukti,
                kasbon,
                nama_sales,
                sopir,
                nama_kenek,
                stock_point,
                jalur,
                no_mobil,
                jenis_mobil,
                no_bkb,
                km_awal,
                km_akhir,
                sisa_kasbon
        """ % (self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end)

        self._cr.execute(query)
        result = self._cr.dictfetchall()
        return result


    def get_report_mt(self):
        query = """
            SELECT
                tgl_kasbon as "TANGGAL KASBON",
                tgl_kembali as "TANGGAL KEMBALI",
                no_bukti as "NO BUKTI",
                kasbon as "KASBON",
                nama_sales as "NAMA SALES",
                sopir as "NAMA SOPIR",
                nama_kenek as "NAMA KENEK",
                stock_point as "STOCK POINT",
                jalur as "JALUR",
                no_mobil as "NO MOBIL",
                jenis_mobil as "JENIS MOBIL",
                no_bkb as "NO BKB",
                km_awal as "KM AWAL",
                km_akhir as "KM AKHIR",
                sisa_kasbon as "SISA KASBON",
                sum(bbm_cash) as "BBM CASH",
                sum(tol) as "TOL",
                sum(uang_makan) as "UANG MAKAN",
                sum(parkir) as "PARKIR",
                sum(tpr_ogah) as "TPR OGAH",
                sum(keamanan) as "KEAMANAN"
                FROM (
            SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                k.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
				left JOIN res_partner_jalur k on r.res_partner_jalur_id = k.id
                left JOIN customer_type c ON k.customer_type = c.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'customer'
                and c.id = 12
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                k.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                l.sub_total as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
				left JOIN res_partner_jalur k on r.res_partner_jalur_id = k.id
                left JOIN customer_type c ON k.customer_type = c.id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'customer'
                AND l.exp_id = 14 --BBM
                and c.id = 12
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                k.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_Akhir,
                0 as bbm_cash,
                l.sub_total as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
				left JOIN res_partner_jalur k on r.res_partner_jalur_id = k.id
                left JOIN customer_type c ON k.customer_type = c.id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'customer'
                AND l.exp_id = 25 --TOL
                and c.id = 12
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                k.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                l.sub_total as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
				left JOIN res_partner_jalur k on r.res_partner_jalur_id = k.id
                left JOIN customer_type c ON k.customer_type = c.id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'customer'
                AND l.exp_id = 26 --UANGMAKAN
                and c.id = 12 
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                k.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                l.sub_total as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
				left JOIN res_partner_jalur k on r.res_partner_jalur_id = k.id
                left JOIN customer_type c ON k.customer_type = c.id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'customer'
                AND l.exp_id = 22 --PARKIR
                and c.id = 12 
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                k.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                l.sub_total as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
				left JOIN res_partner_jalur k on r.res_partner_jalur_id = k.id
                left JOIN customer_type c ON k.customer_type = c.id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'customer'
                AND l.exp_id = 21 --OGAH
                and c.id = 12 
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                k.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                l.sub_total as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
				left JOIN res_partner_jalur k on r.res_partner_jalur_id = k.id
                left JOIN customer_type c ON k.customer_type = c.id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'customer'
                AND l.exp_id = 18
                and c.id = 12 
                ) as k GROUP BY tgl_kasbon,
                tgl_kembali,
                no_bukti,
                kasbon,
                nama_sales,
                sopir,
                nama_kenek,
                stock_point,
                jalur,
                no_mobil,
                jenis_mobil,
                no_bkb,
                km_awal,
                km_akhir,
                sisa_kasbon
        """ % (self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end)

        self._cr.execute(query)
        result = self._cr.dictfetchall()

        return result





    def get_report_global(self):
        query = """
                SELECT
                tgl_kasbon as "TANGGAL KASBON",
                tgl_kembali as "TANGGAL KEMBALI",
                no_bukti as "NO BUKTI",
                kasbon as "KASBON",
                nama_sales as "NAMA SALES",
                sopir as "NAMA SOPIR",
                nama_kenek as "NAMA KENEK",
                stock_point as "STOCK POINT",
                jalur as "JALUR",
                no_mobil as "NO MOBIL",
                jenis_mobil as "JENIS MOBIL",
                no_bkb as "NO BKB",
                km_awal as "KM AWAL",
                km_akhir as "KM AKHIR",
                sisa_kasbon as "SISA KASBON",
                sum(bbm_cash) as "BBM CASH",
                sum(tol) as "TOL",
                sum(uang_makan) as "UANG MAKAN",
                sum(parkir) as "PARKIR",
                sum(tpr_ogah) as "TPR OGAH",
                sum(keamanan) as "KEAMANAN"
                FROM (SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                c.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
                left JOIN res_partner_jalur c ON c.id = r.res_partner_jalur_id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                --and p.bop_type = 'drop'
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                c.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                l.sub_total as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
                left JOIN res_partner_jalur c ON c.id = r.res_partner_jalur_id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                --and p.bop_type = 'drop'
                AND l.exp_id = 14 --BBM
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                c.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_Akhir,
                0 as bbm_cash,
                l.sub_total as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
                left JOIN res_partner_jalur c ON c.id = r.res_partner_jalur_id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <='%s'
                and a.state = 'done'
                and p.state = 'done'
                --and p.bop_type = 'drop'
                AND l.exp_id = 25 --TOL
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                c.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                l.sub_total as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
                left JOIN res_partner_jalur c ON c.id = r.res_partner_jalur_id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                --and p.bop_type = 'drop'
                AND l.exp_id = 26 --UANGMAKAN
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                c.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                l.sub_total as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
                left JOIN res_partner_jalur c ON c.id = r.res_partner_jalur_id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                --and p.bop_type = 'drop'
                AND l.exp_id = 22 --PARKIR
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                c.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                l.sub_total as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
                left JOIN res_partner_jalur c ON c.id = r.res_partner_jalur_id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                --and p.bop_type = 'drop'
                AND l.exp_id = 21 --OGAH
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                c.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                l.sub_total as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
                left JOIN res_partner_jalur c ON c.id = r.res_partner_jalur_id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                --and p.bop_type = 'drop'
                AND l.exp_id = 18 ) as k GROUP BY tgl_kasbon,
                tgl_kembali,
                no_bukti,
                kasbon,
                nama_sales,
                sopir,
                nama_kenek,
                stock_point,
                jalur,
                no_mobil,
                jenis_mobil,
                no_bkb,
                km_awal,
                km_akhir,
                sisa_kasbon
            """ % (self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end)
        self._cr.execute(query)
        return self._cr.dictfetchall()

    def get_report_drop(self):
        query = """
            SELECT
                tgl_kasbon as "TANGGAL KASBON",
                tgl_kembali as "TANGGAL KEMBALI",
                no_bukti as "NO BUKTI",
                kasbon as "KASBON",
                nama_sales as "NAMA SALES",
                sopir as "NAMA SOPIR",
                nama_kenek as "NAMA KENEK",
                stock_point as "STOCK POINT",
                jalur as "JALUR",
                no_mobil as "NO MOBIL",
                jenis_mobil as "JENIS MOBIL",
                no_bkb as "NO BKB",
                km_awal as "KM AWAL",
                km_akhir as "KM AKHIR",
                sisa_kasbon as "SISA KASBON",
                sum(bbm_cash) as "BBM CASH",
                sum(tol) as "TOL",
                sum(uang_makan) as "UANG MAKAN",
                sum(parkir) as "PARKIR",
                sum(tpr_ogah) as "TPR OGAH",
                sum(keamanan) as "KEAMANAN"
                FROM (SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                c.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
                left JOIN res_partner_jalur c ON c.id = r.res_partner_jalur_id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'drop'
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                c.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                l.sub_total as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
                left JOIN res_partner_jalur c ON c.id = r.res_partner_jalur_id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'drop'
                AND l.exp_id = 14 --BBM
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                c.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_Akhir,
                0 as bbm_cash,
                l.sub_total as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
                left JOIN res_partner_jalur c ON c.id = r.res_partner_jalur_id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <='%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'drop'
                AND l.exp_id = 25 --TOL
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                c.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                l.sub_total as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
                left JOIN res_partner_jalur c ON c.id = r.res_partner_jalur_id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'drop'
                AND l.exp_id = 26 --UANGMAKAN
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                c.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                l.sub_total as parkir,
                0 as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
                left JOIN res_partner_jalur c ON c.id = r.res_partner_jalur_id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'drop'
                AND l.exp_id = 22 --PARKIR
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                c.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                l.sub_total as tpr_ogah,
                0 as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
                left JOIN res_partner_jalur c ON c.id = r.res_partner_jalur_id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'drop'
                AND l.exp_id = 21 --OGAH
                UNION
                SELECT
                to_char(p.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kasbon,
                to_char(a.date + interval '7 hours', 'YYYY-MM-DD HH24:MI:SS') as tgl_kembali,
                p.name as no_bukti,
                p.total_pencairan as kasbon,
                sel.name as nama_sales,
                hed.name as sopir,
                help.name as nama_kenek,
                b.name as stock_point,
                c.name as jalur,
                fel.license_plate as no_mobil,
                fel.name as jenis_mobil,
                a.name as no_bkb,
                a.km_awal as km_awal,
                a.km_akhir as km_akhir,
                0 as bbm_cash,
                0 as tol,
                0 as uang_makan,
                0 as parkir,
                0 as tpr_ogah,
                l.sub_total as keamanan,
                a.sisa_penyelesaian as sisa_kasbon
                FROM
                uudp a
                left JOIN uudp_stock_warehouse_ids_res d ON a.id = d.uudp_id
                left JOIN stock_warehouse b ON b.id = d.stock_warehouse_id
                left JOIN uudp_res_partner_jalur_ids_rel r ON a.id = r.uudp_id
                left JOIN res_partner_jalur c ON c.id = r.res_partner_jalur_id
                left JOIN uudp_detail l ON l.uudp_id = a.id
                left JOIN hr_employee hed ON hed.id = a.driver_id
                left JOIN hr_employee sel ON sel.id = a.sales_id
                left JOIN hr_employee help ON help.id = a.helper_id
                left JOIN fleet_vehicle fel ON fel.id = a.vehicle_id
				INNER JOIN uudp p ON a.ajuan_id = p.id AND p.type = 'pengajuan'
                where
                a.type = 'penyelesaian'
                and p.tgl_penyelesaian >= '%s'
                and p.tgl_penyelesaian <= '%s'
                and a.state = 'done'
                and p.state = 'done'
                and p.bop_type = 'drop'
                AND l.exp_id = 18 ) as k GROUP BY tgl_kasbon,
                tgl_kembali,
                no_bukti,
                kasbon,
                nama_sales,
                sopir,
                nama_kenek,
                stock_point,
                jalur,
                no_mobil,
                jenis_mobil,
                no_bkb,
                km_awal,
                km_akhir,
                sisa_kasbon
            """ % (self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end,
                   self.date_start, self.date_end)
        self._cr.execute(query)
        return self._cr.dictfetchall()


    def action_preview(self):
        result = self.get_report_date()

        data = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'data' : result,
            }
        # import logging;
        # _logger = logging.getLogger(__name__)
        # _logger.warning('='*40)
        # _logger.warning('MESSAGE')
        # _logger.warning(data['form']['data'])
        # _logger.warning('='*40)
        return self.env.ref('vit_uudp.laporan_penyelesaian_print').with_context(landscape=True).report_action(self, data=data)



    def action_generate_excel(self):
        # print("action_generate_excel")
        # result = self.get_report_drop()
        # fp = BytesIO()
        # date_string = datetime.now().strftime("%Y-%m-%d")
        # workbook = xlsxwriter.Workbook(fp)
        # wbf, workbook = awf.add_workbook_format(workbook)

        #Laporan Produksi Dyeing Perhari
        report_name = 'LAPORAN PENYELESAIAN'
        return self.action_export()
        # return self.get_report_drop()
        # worksheet = workbook.add_worksheet(report_name)
        # # report_name = obj.name

        # worksheet.set_column('A6:A6', 20) #TANGGAL KELUAR
        # worksheet.set_column('B6:B6', 10) #TANGGAL KEMBALI
        # worksheet.set_column('C6:C6', 10) #NO BUKTI
        # worksheet.set_column('D6:D6', 10) #KASBOON
        # worksheet.set_column('E6:E6', 20) #NAMA SALES
        # worksheet.set_column('F6:F6', 20) #NAMA SOPIR
        # worksheet.set_column('G6:G6', 15) #NAMA KENEK
        # worksheet.set_column('H6:H6', 25) #STOCK POINT
        # worksheet.set_column('I6:I6', 15) #JALUR
        # worksheet.set_column('J6:J6', 15) #NO MOBIL
        # worksheet.set_column('K6:K6', 15) #JENIS MOBIL
        # worksheet.set_column('L6:L6', 30) #NO BKB
        # worksheet.set_column('M6:M6', 30) #KM AWAL
        # worksheet.set_column('N6:N6', 30) #KM AKHIR
        # # worksheet.set_column('O6:O6', 35) #OMZET
        # worksheet.set_column('O6:O6', 20) #BBM CASH
        # worksheet.set_column('P6:P6', 15) #TOL
        # worksheet.set_column('Q6:Q6', 10) #UANG MAKAN
        # worksheet.set_column('R6:R6', 10) #PARKIR
        # worksheet.set_column('S6:S6', 15) #TPR/OGAH
        # worksheet.set_column('T6:T6', 10) #KEAMANAN
        # worksheet.set_column('U6:U6', 10) #SISA KASBON
        # # worksheet.set_column('W6:WQ', 10) #TOTAL PENGELUARAN

        # worksheet.merge_range('A2:U2', report_name , wbf['merge_format'])
        # worksheet.merge_range('A3:U3', 'PERIODE (' + str(self.date_start) + ' - ' + str(self.date_end) + ')' , wbf['merge_format'])
        # worksheet.merge_range('A4:U4', '' , wbf['merge_format'])
        # worksheet.merge_range('A1:U1', '' , wbf['merge_format'])
        # worksheet.merge_range('A5:U5', '' , wbf['merge_format'])

        # row = 6
        # worksheet.write('A%s' % (row), 'TANGGAL KELUAR', wbf['header'])
        # worksheet.write('B%s' % (row), 'TANGGAL KEMBALI', wbf['header'])
        # worksheet.write('C%s' % (row), 'NO BUKTI', wbf['header'])
        # worksheet.write('D%s' % (row), 'KASBOON', wbf['header'])
        # worksheet.write('E%s' % (row), 'NAMA SALES', wbf['header'])
        # worksheet.write('F%s' % (row), 'NAMA SOPIR', wbf['header'])
        # worksheet.write('G%s' % (row), 'NAMA KENEK', wbf['header'])
        # worksheet.write('H%s' % (row), 'STOCK POINT', wbf['header'])
        # worksheet.write('I%s' % (row), 'JALUR', wbf['header'])
        # worksheet.write('J%s' % (row), 'NO MOBIL', wbf['header'])
        # worksheet.write('K%s' % (row), 'JENIS MOBIL', wbf['header'])
        # worksheet.write('L%s' % (row), 'NO BKB', wbf['header'])
        # worksheet.write('M%s' % (row), 'KM AWAL', wbf['header'])
        # worksheet.write('N%s' % (row), 'KM AKHIR', wbf['header'])
        # # worksheet.write('O%s' % (row), 'OMZET', wbf['header'])
        # worksheet.write('O%s' % (row), 'BBM CASH', wbf['header'])
        # worksheet.write('P%s' % (row), 'TOL', wbf['header'])
        # worksheet.write('Q%s' % (row), 'UANG MAKAN', wbf['header'])
        # worksheet.write('R%s' % (row), 'PARKIR', wbf['header'])
        # worksheet.write('S%s' % (row), 'TPR/OGAH', wbf['header'])
        # worksheet.write('T%s' % (row), 'KEAMANAN', wbf['header'])
        # worksheet.write('U%s' % (row), 'SISA KASBON', wbf['header'])
        # # worksheet.write('V%s' % (row), 'TOTAL PENGELUARAN', wbf['header'])

        # row += 1
        # no = 1

        # for rec in result:
        #     worksheet.write('A%s' % (row), rec.get('tgl_kasbon', ''), wbf['content_center'])
        #     worksheet.write('B%s' % (row), rec.get('tgl_kembali', ''), wbf['content_center'])
        #     worksheet.write('C%s' % (row), rec.get('no_bukti', ''), wbf['content_center'])
        #     worksheet.write('D%s' % (row), rec.get('kasbon', ''), wbf['content_float'])
        #     worksheet.write('E%s' % (row), rec.get('nama_sales', ''), wbf['content_center'])
        #     worksheet.write('F%s' % (row), rec.get('sopir', ''), wbf['content_center'])
        #     worksheet.write('G%s' % (row), rec.get('nama_kenek', ''), wbf['content_center'])
        #     worksheet.write('H%s' % (row), rec.get('stock_point', ''), wbf['content_center'])
        #     worksheet.write('I%s' % (row), rec.get('jalur', ''), wbf['content_center'])
        #     worksheet.write('J%s' % (row), rec.get('no_mobil', ''), wbf['content_center'])
        #     worksheet.write('K%s' % (row), rec.get('jenis_mobil', ''), wbf['content_center'])
        #     worksheet.write('L%s' % (row), rec.get('no_bkb', ''), wbf['content_float'])
        #     worksheet.write('M%s' % (row), rec.get('km_awal', ''), wbf['content_float'])
        #     worksheet.write('N%s' % (row), rec.get('km_akhir', ''), wbf['content_float'])
        #     worksheet.write('O%s' % (row), rec.get('bbm_cash', ''), wbf['content_float'])
        #     worksheet.write('P%s' % (row), rec.get('tol', ''), wbf['content_float'])
        #     worksheet.write('Q%s' % (row), rec.get('uang_makan', ''), wbf['content_float'])
        #     worksheet.write('R%s' % (row), rec.get('parkir', ''), wbf['content_float'])
        #     worksheet.write('S%s' % (row), rec.get('tpr_ogah', ''), wbf['content_float'])
        #     worksheet.write('T%s' % (row), rec.get('keamanan', ''), wbf['content_float'])
        #     worksheet.write('U%s' % (row), rec.get('sisa_kasbon', ''), wbf['content_float'])

        #     no += 1
        #     row += 1

        #     # TOTAL
        # worksheet.merge_range('A%s:N%s' % (row, row), 'TOTAL', wbf['foot_merge_format'])
        # worksheet.write('O%s' % (row), '=SUM(O7:O%s)' % (row-1), wbf['total_float'])
        # worksheet.write('P%s' % (row), '=SUM(P7:P%s)' % (row-1), wbf['total_float'])
        # worksheet.write('Q%s' % (row), '=SUM(Q7:Q%s)' % (row-1), wbf['total_float'])
        # worksheet.write('R%s' % (row), '=SUM(R7:R%s)' % (row-1), wbf['total_float'])
        # worksheet.write('S%s' % (row), '=SUM(S7:S%s)' % (row-1), wbf['total_float'])
        # worksheet.write('T%s' % (row), '=SUM(T7:T%s)' % (row-1), wbf['total_float'])
        # worksheet.write('U%s' % (row), '=SUM(U7:U%s)' % (row-1), wbf['total_float'])

        # filename = '%s %s' % (report_name, '.xlsx')
        # workbook.close()
        # out = base64.encodestring(fp.getvalue())
        # self.write({'data': out})
        # fp.close()

        # self.write({'data': out})
        # url = "web/content/?model=" + self._name + "&id=" + str(self.id) + "&field=data&download=true&filename=" + filename
        # result = {
        #     'name': 'Laporan Penyelesaian XLSX',
        #     'type': 'ir.actions.act_url',
        #     'url': url,
        #     'target': 'download',
        # }
        # return result

    # def prepare_report_filters(self):
    #     """It is writing under second page"""
    #     self.row_pos_2 += 2
    #     if filter:
    #             # Compariosn Date from
    #             self.sheet_2.write_string(self.row_pos_2, 0, _('Tanggal keluar'),
    #                                       self.format_header)
    #             date = self.tgl_kasbon(
    #                 filter['form']['tgl_kasbon']['tgl_kasbon'] and filter['form']['tgl_kasbon']['date_from'].strftime('%Y-%m-%d'))
    #             if filter['form']['tgl_kasbon'].get('tgl_kasbon'):
    #                 self.sheet_2.write_datetime(self.row_pos_2, 1, date,
    #                                             self.content_header_date)
    #             self.row_pos_2 += 1

