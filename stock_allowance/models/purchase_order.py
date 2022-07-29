from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # def _prepare_invoice(self):
    #     res = super(PurchaseOrder, self)._prepare_invoice()
    #     date_done_ids = self.mapped('picking_ids.date_done')
    #     filtered = filter(lambda x: x != False, date_done_ids)
    #     date_max = max(filtered)
    #     res['date_datang_barang'] = date_max ## set datang barang
    #     return res