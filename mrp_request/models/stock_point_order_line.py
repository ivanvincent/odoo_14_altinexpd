from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPointOrderLine(models.Model):
    _inherit = 'stock.point.order.line'

    
    mrp_request_line_id = fields.Many2one('mrp.request.line', string='Request Line')
    mrp_request_id      = fields.Many2one("mrp.request",string='Mrp Request')
    
    # mrp_request_state   = fields.Selection(
    #     compute="_compute_request_state",
    #     string="Request Status",
    #     selection=lambda self: self.env["mrp.request"]._fields["state"].selection,
    #     store=True,
    # )
    
    
    
    
    # @api.depends("order.state", "mrp_request_line_id.mrp_request_id.state")
    # def _compute_request_state(self):
    #     for rec in self:
    #         temp_request_state = False
    #         if rec.mrp_request_line_id:
    #             if any(po_line.state == "done" for po_line in rec.line_ids):
    #                 temp_request_state = "done"
    #             elif all(po_line.state == "cancel" for po_line in rec.purchase_lines):
    #                 temp_request_state = "cancel"
    #             elif any(po_line.state == "purchase" for po_line in rec.purchase_lines):
    #                 temp_request_state = "purchase"
    #             elif any(
    #                 po_line.state == "to approve" for po_line in rec.purchase_lines
    #             ):
    #                 temp_request_state = "to approve"
    #             elif any(po_line.state == "sent" for po_line in rec.purchase_lines):
    #                 temp_request_state = "sent"
    #             elif all(
    #                 po_line.state in ("draft", "cancel")
    #                 for po_line in rec.purchase_lines
    #             ):
    #                 temp_request_state = "draft"
    #         rec.mrp_request_state = temp_request_state

    