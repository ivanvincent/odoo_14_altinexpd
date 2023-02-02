from odoo import fields, models, api, _
from odoo.exceptions import UserError

class PrintReportingStockLotWizard(models.TransientModel):
    _name = 'print.reporting_stock_lot.wizard'

    reporting_id    = fields.Many2one('reporting.stock.lot', string='Reporting', required=True,)
    type_print      = fields.Selection([("greige","Lot")], string='Type')
    template_greige = fields.Selection([
        ("laporan_mutasi_barang","Laporan Mutasi Barang"),
        # ("laporan_penerimaan_kain_greige","Laporan Penerimaan Kain Greige"),
        ("laporan_pengeluaran_kain","Laporan Pengeluaran"),
        # ("laporan_kain_lama","Laporan Kain Lama"),
        ("laporan_akurasi_data_stock_opname","Laporan Akurasi Data Stock Opname"),
        ("laporan_group_by_palet","Laporan Group By Palet"),
        ("laporan_barcode_perpalet","Laporan Barcode Perpalet"),
        ], string='Template Greige'
    )

    def action_print(self):
        if self.template_greige == 'laporan_mutasi_barang':
            return self.env.ref('reporting.action_laporan_mutasi_barang').report_action(self.reporting_id)
        # elif self.template_greige == 'laporan_penerimaan_kain_greige':
        #     return self.env.ref('reporting.action_laporan_penerimaan_kain_greige').report_action(self.reporting_id)

        elif self.template_greige == 'laporan_pengeluaran_kain':
            return self.env.ref('reporting.action_laporan_pengeluaran_kain').report_action(self.reporting_id)
        elif self.template_greige == 'laporan_kain_lama':
            return self.env.ref('reporting.action_laporan_kain_lama').report_action(self.reporting_id)

        elif self.template_greige == 'laporan_akurasi_data_stock_opname':
            return self.env.ref('reporting.action_laporan_akurasi_data_stock_opname').report_action(self.reporting_id)

        elif self.template_greige == 'laporan_group_by_palet':
            return self.env.ref('reporting.action_laporan_group_by_palet').report_action(self.reporting_id)

        elif self.template_greige == 'laporan_barcode_perpalet':
            return self.env.ref('reporting.action_laporan_barcode_perpalet').report_action(self.reporting_id)

        return True