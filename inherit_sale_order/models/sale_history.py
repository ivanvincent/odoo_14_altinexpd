from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
class SaleProductHistory(models.Model):
    _name = 'sale.product.history'
    
    
    partner_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one('product.product', string='Product')
    last_price = fields.Float(string='Last Price' ,compute='get_last_price',)
    line_ids   = fields.One2many('sale.product.history.line', 'history_id', string='Details')
    
    
    @api.depends('line_ids')
    def get_last_price(self):
        for history in self:
            history.last_price = history.line_ids[-1].sale_price
    

class SaleProductHistoryLine(models.Model):
    _name = 'sale.product.history.line'
    
    
    history_id     = fields.Many2one('sale.product.history', string='HIstory')
    sale_id        = fields.Many2one('sale.order', string='Sale Order')
    so_date        = fields.Date(string='Sale Order Date')
    partner_id     = fields.Many2one('res.partner', string='Customer',related="history_id.partner_id")
    product_id     = fields.Many2one('product.product', string='Product',related="history_id.product_id")
    sale_price     = fields.Float(string='Price')
    discount       = fields.Float(string='Discount')
    
