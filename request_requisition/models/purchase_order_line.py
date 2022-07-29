from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    
    request_requisition_id  = fields.Many2one('request.requisition', string='Request Requisition', related='purchase_request_id.rr_id')
    qty_rr = fields.Float(string='Qty Request Requisition', compute="_compute_qty_rr")
    
    
    def _compute_qty_rr(self):
        for rec in self:
            request_requisition_line_obj = self.env['request.requisition.line'].search([('order_id', '=', rec.request_requisition_id.id)])
            rec.qty_rr = sum(request_requisition_line_obj.filtered(lambda a: a.product_id.id == rec.product_id.id).mapped('quantity')) or 0