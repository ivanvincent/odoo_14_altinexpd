from odoo import fields, models, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class RRPurchaseRequestWizard(models.TransientModel):

    _name = 'rr.purchase.request.wizard'
    
    
    picking_type_id = fields.Many2one('stock.picking.type', string='Operation Type',required=True, )
    pr_id           = fields.Many2one('purchase.request', string='Purchase Request',domain=[('state', '=', 'draft')])
    request_id      = fields.Many2one('request.requisition', string='Request Requisition')
    request_by      = fields.Many2one('res.users', string='Request By',default= lambda self : self.env.user.id)
    line_ids        = fields.One2many('rr.purchase.request.line.wizard', 'wiz_id', string='Purchase Request Line')

    def create_purchase_request(self):
        if self.pr_id:
            self.pr_id.line_ids = [(0,0 ,{'request_id': self.request_id.id,'name': line.product_id.name,'product_id': line.product_id.id,'product_qty': line.product_qty,'product_uom_id': line.product_uom_id.id}) for line in self.line_ids]
            for line in self.request_id.order_ids:
                line.write({"is_request_pr": True})
            
            self.pr_id.sudo().write({'request_id': pr_id.id})
            
            
            self.request_id.create_picking_issue()
            
            # self.pr_id.button_to_approve()
        else:
                
            vals =  {
                    'origin'                : self.request_id.name,
                    'date_start'            : self.request_id.request_date,
                    'description'           : self.request_id.note,
                    'picking_type_id'       : self.picking_type_id.id,
                    'requested_by'          : self.env.user.id,
                    'rr_id'                 : self.request_id.id,
                    'line_ids'              : [(0,0,{'request_id': self.request_id.id,'name': line.product_id.name,'product_id': line.product_id.id,'product_qty': line.product_qty,'product_uom_id': line.product_uom_id.id}) for line in self.line_ids.filtered(lambda x : x.qty_on_hand < 1)]
                }
            
            request = self.env['purchase.request'].sudo().create(vals)
            
            self.request_id.sudo().write({'request_id': request.id})
            
            for line in self.request_id.order_ids:
                line.write({"is_request_pr": True})
            
            self.request_id.create_picking_issue()
            
            # request.button_to_approve()
        
        return
    
    @api.model
    def default_get(self,fields):
        res = super().default_get(fields)
        active_model = self.env.context.get("active_model", False)
        request_line_ids = []
        if active_model == "request.requisition.line":
            request_line_ids += self.env.context.get("active_ids", [])
        elif active_model == "request.requisition":
            request_ids = self.env.context.get("active_ids", False)
            request_line_ids += (
                self.env[active_model].browse(request_ids).mapped("order_ids.id")
            )
        if not request_line_ids:
            return res
        res["line_ids"] = self.get_items(request_line_ids)
        res["request_id"] = self.env.context.get('active_id')
        res['picking_type_id'] = self.env[active_model].browse([self.env.context.get("active_id")]).mapped('warehouse_id')[0].in_type_id.id
        return res
    
    @api.model
    def get_items(self, request_line_ids):
        request_line_obj = self.env["request.requisition.line"]
        items = []
        request_lines = request_line_obj.browse(request_line_ids)
        for line in request_lines.filtered(lambda x: x.qty_onhand <= 0):
            items.append([0, 0, self._prepare_item(line)])
        return items
    
    @api.model
    def _prepare_item(self, line):
        return {
            "line_id": line.id,
            "request_id": line.order_id.id,
            "product_id": line.product_id.id,
            "name": line.name or line.product_id.name,
            "product_qty": line.quantity,
            "product_uom_id": line.uom_id.id,
        }


class RRPurchaseRequestLineWizard(models.TransientModel):

    _name = 'rr.purchase.request.line.wizard'
    
    
    wiz_id         = fields.Many2one(comodel_name='rr.purchase.request.wizard', string='Wizard ')
    line_id        = fields.Many2one(comodel_name="request.requisition.line", string="RR Purchase Request Line")
    request_id     = fields.Many2one(comodel_name="request.requisition",related="line_id.order_id",string="Request Requisition", readonly=True,)
    name           = fields.Char(string='Description',required=True)
    product_id     = fields.Many2one('product.product', string='Product')
    product_qty    = fields.Float(string="Quantity to purchase", digits="Product Unit of Measure")
    product_uom_id = fields.Many2one(comodel_name="uom.uom", string="UoM", required=True)
    specification  = fields.Char(related="line_id.spesification",string='Specifications')
    no_komunikasi  = fields.Char(related="line_id.no_komunikasi",string='No Komunikasi')
    qty_on_hand  = fields.Float(related="line_id.qty_onhand",string='Qty On Hand')
    
    