from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FollowUpForcast(models.Model):
    _name = 'follow.up.forcast'
    _auto = False

    product_id = fields.Many2one('product.product', string='Product')
    default_code = fields.Char(string='Code')
    part_no = fields.Char(string='Part No')
    price_unit = fields.Float(string='Price Unit')
    qty_delivery = fields.Float(string='Qty Delivery')
    qty_need = fields.Float(string='Qty Need')
    qty_forcast = fields.Float(string='Qty Forcast')
    qty_sale_order = fields.Float(string='Qty Sale Order')
    qty_onhand = fields.Float(string='Qty OnHand')
    qty_minim = fields.Float(string='Qty Minimum Stock')
    qty_sisa = fields.Float(string='Qty Sisa')
    _sql = """ 
            CREATE OR REPLACE VIEW follow_up_forcast AS (
            SELECT row_number() OVER () as id,
            product_id,
            price_unit,
            qty as qty_forcast,
            qty_so,
            qty_do, 
            qty_inv,
            0 as qty_sale_order,  
            0 as qty_delivery,
            0 as qty_onhand,
            0 as qty_minim,
            0 as qty_mo,
            0 as qty_sisa,
            0 as qty_need, 
            default_code,
            part_no
            FROM sale_contract_line)
           """