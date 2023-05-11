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
    alamat          = fields.Text(string='Alamat')
    option_vip      = fields.Selection([("vip","VIP"),("high_gress","High Gress")], string='HighGress / VIP')
    # payment_term_id = fields.Many2one(related='quotation_id.payment_term_id', string='Payment Term')
    # payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')
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

    # super(SaleOrder, self).action_cancel()
    # def onchange_partner_id(self) :
    #     res = super(SaleOrder, self).onchange_partner_id()

    #     if not self.partner_id:
    #         self.update({
    #             'partner_invoice_id': False,
    #             'partner_shipping_id': False,
    #             'fiscal_position_id': False,
    #         })
    #         return

    #     self = self.with_company(self.company_id)

    #     addr = self.partner_id.address_get(['delivery', 'invoice'])
    #     partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
    #     values = {
    #         'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
    #         'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
    #         'partner_invoice_id': addr['invoice'],
    #         'partner_shipping_id': addr['delivery'],
    #     }
    #     user_id = partner_user.id
    #     if not self.env.context.get('not_self_saleperson'):
    #         user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
    #     if user_id and self.user_id.id != user_id:
    #         values['user_id'] = user_id

    #     if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms') and self.env.company.invoice_terms:
    #         values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
    #     if not self.env.context.get('not_self_saleperson') or not self.team_id:
    #         values['team_id'] = self.env['crm.team'].with_context(
    #             default_team_id=self.partner_id.team_id.id
    #         )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)], user_id=user_id)
    #     self.update(values)
    #     return res
    