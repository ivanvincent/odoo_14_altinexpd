from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    mrp_request_id  = fields.Many2one('mrp.request', string='Mrp Request')
    po_cust         = fields.Char(string='Po Customer')
    no_sample       = fields.Char(string='No Sample')
    up_kpd          = fields.Char(string='Up. Pengiriman')
    note_so         = fields.Char(string='Note')
    no_dqc          = fields.Boolean(related='partner_id.no_dqc', string='Status DQC')
    # payment_term_id = fields.Many2one(related='quotation_id.payment_term_id', string='Payment Term')
    # demantional_quality_control

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if not self.mrp_request_id:
            self.action_create_mor()
        return res

    def action_create_mor(self):
        line = []
        for l in self.order_line:
            line.append((0, 0, {
                'product_id'    : l.product_id.id,
                'qty_produce'   : l.quantity_remaining,
                'sale_line_id'  : l.id,
                'kd_bahan'      : l.kd_bahan,
                'lapisan'       : l.lapisan,
                # 'payment_term_id'       : l.payment_term_id,
            }))
        mrp_request = self.env['mrp.request'].create({
            'request_date': fields.Date.today(),
            'sale_id': self.id,
            'line_ids': line
        })
        # self.mrp_request_id = mrp_request.id
        # print("action_create_mor")