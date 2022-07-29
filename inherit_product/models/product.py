
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Product(models.Model):
    _inherit = 'product.product'
    
    mkt_categ_id        = fields.Many2one('marketing.category', string='Marketing Category')
    kd_product_mkt_id   = fields.Many2one('product.product', string='Kode Product Mkt')
    group_product_id    = fields.Many2one('group.product', string='Group Product')
    line_product_id     = fields.Many2one('line.product', string='Line Product')
    merk_product_id     = fields.Many2one('merk.product', string='Merk Product')
    lead_days           = fields.Integer(string='Lead')
    min_stock           = fields.Float(related="product_tmpl_id.min_stock",string='Mininum Stock')
    usage_daily         = fields.Float(string='Usage Daily',compute="_get_usage_daily")
    order_time          = fields.Float(string='Order Time',compute="_get_order_time")
    lead_time           = fields.Float(string='Lead Purchase',compute="_get_order_time")
    
    def _get_usage_daily(self):
        for line in self:
            today = fields.Datetime.now()
            week_ago = fields.Datetime.subtract(today,days=7)
            product_moves = self.env['stock.move.line'].search([('product_id','=',line.id),('picking_code','=','internal'),('date','>=',week_ago),('date','<=',today),('state','=','done')])
            line.usage_daily = sum(product_moves.mapped('qty_done')) / 7
    

    def _get_order_time(self):
        order_line = self.env['purchase.order.line']
        for line in self:
            line.order_time = 0
            order_line      = order_line.search([('product_id','=',line.id)]).sorted(lambda x: x.order_id,reverse = True)
            if order_line and order_line[0].purchase_request_lines and order_line[0].order_id.date_planned and order_line[0].order_id.date_approve:
                order_line      = order_line[0] if order_line else False
                date_pr         = order_line.purchase_request_lines.request_id.date_start 
                lead_receipt    = order_line.order_id.date_planned.date() - order_line.order_id.date_approve.date()
                lead_po         = (order_line.order_id.date_approve.date() - date_pr)
                line.order_time = lead_po.days
                lead_time       = lead_receipt
                line.lead_time  =  line.order_time + lead_time.days or 0
            else:
                line.order_time = 0
                lead_time       = 0
                line.lead_time  = 0

    
    
  
    def name_get(self):
        return [(rec.id, rec.name) for rec in self]
    
    
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    
    min_stock = fields.Float(string='Mininum Stock')
    

class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'
    
    usage_daily         = fields.Float(string='Usage Daily',compute="_get_usage_daily")
    order_time          = fields.Float(string='Order Time',compute="_get_order_time")
    min_stock           = fields.Float(string='Minimum Stock')
    
    
    def _get_usage_daily(self):
        for line in self:
            today = fields.Datetime.now()
            week_ago = fields.Datetime.subtract(today,days=7)
            product_id = line.product_tmpl_id.product_variant_id.id
            product_moves = self.env['stock.move.line'].search([('product_id','=',product_id),('picking_code','=','internal'),('date','>=',week_ago),('date','<=',today),('state','=','done')])
            line.usage_daily = sum(product_moves.mapped('qty_done')) / 7
            
    
    def _get_order_time(self):
        order_line = self.env['purchase.order.line']
        for line in self:
            line.order_time = 0
            product_id = line.product_tmpl_id.product_variant_id.id
            order_line = order_line.search([('product_id','=',product_id),('partner_id','=',line.name.id)])
            tes = set(order_line.purchase_request_lines)
            import logging;
            _logger = logging.getLogger(__name__)
            _logger.warning('='*40)
            _logger.warning('order time')
            _logger.warning(tes)
            _logger.warning(order_line.purchase_request_lines.filtered(lambda l: l.purchase_state == 'purchase').mapped('date_start'))
            _logger.warning('='*40)