from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _name = 'sale.order'

    mrp_requests_ids = fields.One2many('mrp.request', 'sale_id', 'Mrp Request')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    quantity_remaining = fields.Float(string='Qty Remaining', compute='_compute_quantity_remaining')


    @api.depends('product_uom_qty')
    def _compute_quantity_remaining(self):
        for rec in self:
            mrl_obj = self.env['mrp.request.line'].search([('request_id.sale_id', '=', rec.id), ('request_id.state', '=', 'done')])
            rec.quantity_remaining = rec.product_uom_qty - sum(mrl_obj.mapped('qty_produce'))