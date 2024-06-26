from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    quotation_id = fields.Many2one('quotation', string='Quotation')
    delivery_date = fields.Date(string='Delivery Time')
    up_kpd = fields.Many2one('attn', string='Attn', related='quotation_id.up_kpd')
    product_order_id = fields.Many2one(string='Product Order', related='quotation_id.product_order_id')
    no_quotation_accurate = fields.Char(string='No Quotation Accurate')
    kode_mkt_id = fields.Many2one('kode.mkt', string='Kode Mkt', related='quotation_id.kode_mkt_id', store=True,)
    dqups_id = fields.Many2one('quotation.request.form', string='D-QUPS')

    @api.onchange('quotation_id')
    def onchange_quotation_id(self):
        print("onchange_quotation_id")
        qtn = self.quotation_id
        if qtn:
            self.partner_id     = qtn.partner_id
            self.design_id      = qtn.design_code_id.id
            self.payment_term_id =  qtn.payment_term_id.id
            self.order_line     = False
            self.delivery_date  = qtn.delivery_date
            self.no_sample      = qtn.no_sample
            # self.up_kpd         = qtn.up_kpd.id
            self.alamat      = qtn.up_kpd.alamat
            self.note_so         = qtn.note_so
            
            order_lines = []
            for line in qtn.line_ids:
                order_lines.append((0, 0, {
                        'product_id'        : line.product_id.id,
                        'product_uom_qty'   : line.quantity,
                        'price_unit'        : line.price_unit,
                        'name'              : line.product_id.name,
                        'product_uom'       : line.product_id.uom_id.id,
                        'state'             : 'draft',
                        'treatment_id'      : line.treatment_id.id,
                        'kd_bahan'          : line.kd_bahan,
                        'lapisan'           : line.lapisan,
                        'tax_id'            : line.tax_ids,
                        'embos'             : line.embos
                        # 'contract_line_id'  : line.id,
                    }))
            self.order_line = order_lines
            self.payment_term_id =  qtn.payment_term_id.id