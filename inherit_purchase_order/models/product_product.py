from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    total_vendor = fields.Integer(string='Total Vendor', compute="_compute_total_vendor")

    def _compute_total_vendor(self):
        partner_obj = self.env['purchase.order.line'].search([('product_id', '=', self.id)]).mapped('partner_id.id')
        self.total_vendor = len(set(partner_obj)) if partner_obj else 0
    
    def action_view_vendor(self):
        partner_obj = self.env['purchase.order.line'].search([('product_id', '=', self.id)]).mapped('partner_id.id')
        action = self.env.ref('account.res_partner_action_supplier').read()[0]
        action['domain'] = [('id', 'in', list(set(partner_obj)))]
        return action