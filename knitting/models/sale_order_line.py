from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging 
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    
    def _get_mrp_production(self):
        for line in self:
            mrp_ids = self.env['mrp.production'].sudo().search([('sale_id','=',line.order_id.id),('sale_line_id','=',line.id),('product_id','=',line.product_id.id)])
            if len(mrp_ids) > 0:
                for production in mrp_ids:
                    line.mrp_ids += mrp_ids
            else:
                line.mrp_ids = False
                
    @api.depends('mrp_ids')
    def _get_mrp_production_qty(self):
        for line in self:
            mrp_ids = self.env['mrp.production'].sudo().search([('sale_id','=',line.order_id.id),('sale_line_id','=',line.id),('product_id','=',line.product_id.id)])
            mrp_qty_shrinkageless = self.env['mrp.production'].sudo().search([('sale_id','=',line.order_id.id),('sale_line_id','=',line.id),('product_id','=',line.product_id.id),('mrp_request_id','!=',False)])
            line.mrp_quantity = sum(mrp_ids.mapped('product_qty'))
            line.mrp_produced_qty = sum(mrp_ids.mapped('qty_produced'))
            line.remaining_qty = line.product_uom_qty - sum(mrp_qty_shrinkageless.mapped('product_qty'))
            
            
    
    mrp_request_id        = fields.Many2one('mrp.request', string='Mrp Request')
    mrp_ids               = fields.Many2many('mrp.production',string='Manufacturing',compute="_get_mrp_production")
    mrp_quantity          = fields.Float(string='Manufacturing Qty',compute="_get_mrp_production_qty")
    mrp_produced_qty      = fields.Float(string='Produced Qty',compute="_get_mrp_production_qty")
    remaining_qty         = fields.Float(string='Remaining Qty',compute="_get_mrp_production_qty")
    html_color            = fields.Char(related='product_id.html_color', string='Color Visualitation')
    product_code          = fields.Char(string='Product Code', related='product_id.default_code')
    greige_id             = fields.Many2one('product.template', string='Greige',related="order_id.greige_id",store=True,)
    greige_availability   = fields.Boolean(string='Grege Availability')
    greige_stock_quantity = fields.Float(string='Greige Quantity',compute='_compute_quantities')
    reserved_quantity     = fields.Float(compute='_compute_quantities', string='Reserved', store=False)
    
    def _compute_quantities(self):
        Quant = self.env['stock.quant'].with_context(active_test=False)
        source_location = 1297 #GDDK
        qty = []
        for line in self:
            for stock in line.greige_id.product_variant_ids:
                domain_quant = [('product_id', '=',stock.id),('location_id','=',source_location)]
                quants_res = dict((item['product_id'][0], (item['quantity'], item['reserved_quantity'])) for item in Quant.read_group(domain_quant, ['product_id', 'quantity', 'reserved_quantity'], ['product_id'], orderby='id'))
                qty += [{
                    "reserved":  quants_res.get(stock.id, [False, 0.0])[1],
                    "onhand": quants_res.get(stock.id, [False, 0.0])[0],
                }]
              
           
            line.greige_stock_quantity = sum([stock.get('onhand') for stock in qty])
            line.reserved_quantity = sum([stock.get('reserved') for stock in qty])
            
    
    
    
    
    
    

    