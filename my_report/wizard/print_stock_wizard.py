from odoo import fields, models, api, _
from odoo.exceptions import UserError

class PrintStockWizard(models.TransientModel):
    _name = 'print.stock.wizard'

    picking_id      = fields.Many2one('stock.picking', string='Stock Picking', required=True,)
    type_print      = fields.Selection([("greige","Greige")], string='Type')
    template_greige = fields.Selection([
        ("pengeluaran_greige_a4","Pengeluaran Greige A4"),
        ("pengeluaran_greige_a5","Pengeluaran Greige A5"),
        ("bukti_penerimaan_kain_greige","Bukti Penerimaan Kain Greige"),
        ("bukti_pengeluaran_kain_greige","Bukti Pengeluaran Kain Greige"),
        ("packing_list_pengiriman_kain","Packing List Pengiriman Kain"),
        ], string='Template Greige'
    )

    def action_print(self):
        if self.template_greige == 'pengeluaran_greige_a4':
            return self.env.ref('my_report.action_pengeluaran_greige_a4').report_action(self.picking_id)
        elif self.template_greige == 'pengeluaran_greige_a5':
            return self.env.ref('my_report.action_pengeluaran_greige_a5').report_action(self.picking_id)

        elif self.template_greige == 'bukti_penerimaan_kain_greige':
            return self.env.ref('my_report.action_bukti_penerimaan_kain_greige').report_action(self.picking_id)
        elif self.template_greige == 'bukti_pengeluaran_kain_greige':
            return self.env.ref('my_report.action_bukti_pengeluaran_kain_greige').report_action(self.picking_id)

        elif self.template_greige == 'packing_list_pengiriman_kain':
            return self.env.ref('my_report.action_packing_list_pengiriman_kain').report_action(self.picking_id)

        return True