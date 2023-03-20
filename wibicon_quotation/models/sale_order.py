from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    quotation_id = fields.Many2one('quotation', string='Quotation')
    delivery_date = fields.Date(string='Delivery Time')
    kd_bahan = fields.Char(string='Kode Bahan')

    @api.onchange('quotation_id')
    def onchange_quotation_id(self):
        print("onchange_quotation_id")
        qtn = self.quotation_id
        if qtn:
            self.partner_id = qtn.partner_id
            self.design_id = qtn.design_code_id.id
            self.payment_term_id = qtn.payment_term_id.id
            self.order_line = False
            self.delivery_date = qtn.delivery_date
            self.kd_bahan = qtn.kd_bahan
            order_lines = []
            for line in qtn.line_ids:
                order_lines.append((0, 0, {
                        'product_id'        : line.product_id.id,
                        'product_uom_qty'   : line.quantity,
                        'price_unit'        : line.price_unit,
                        'name'              : line.product_id.name,
                        'product_uom'       : line.product_id.uom_id.id,
                        'state'             : 'draft',
                        'treatment_id'      : line.treatment_id.id
                        # 'contract_line_id'  : line.id,
                    }))
            self.order_line = order_lines