from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_product   = fields.Integer(string='Total Product', compute="_compute_total_product")
    supplier_code   = fields.Char(string='Supplier Code')
    attn            = fields.Char(string='ATTN')
    fax             = fields.Char(string='Fax')

    def _compute_total_product(self):
        purchase_order_line_obj = self.env['purchase.order.line'].search([('partner_id', '=', self.id)]).mapped('product_id.id')
        self.total_product = len(list(set(purchase_order_line_obj))) if purchase_order_line_obj else 0

    def action_view_product(self):
        action = self.env.ref('inherit_purchase_order.purchase_order_line_action').read()[0]
        action['name'] = "Product from %s" % (self.name)
        action['domain'] = [('partner_id', '=', self.id)]
        return action

    # def _compute_total_product(self):
    #     product_obj = self.env['purchase.order.line'].search([('partner_id', '=', self.id)]).mapped('partner_id.id')
    #     print('')
    #     print(product_obj)
    #     self.total_product = len(list(set(product_obj))) if product_obj else 0

    # def action_view_product(self):
    #     product_obj = self.env['purchase.order.line'].search([('partner_id', '=', self.id)]).mapped('partner_id.id')
    #     action = self.env.ref('inherit_purchase_order.purchase_order_line_action').read()[0]
    #     action['domain'] = [('id', '=', len(list(set(product_obj))))]
    #     return action