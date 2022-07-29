from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RuteSaleConfig(models.Model):
    _name = 'rute.sale.config'

    name                       = fields.Char(string='Config Name',index=True,copy=False)
    warehouse_id               = fields.Many2one('stock.warehouse', string='Stock Point',domain=[('is_stock_point', '=', True)],required=True, )
    default_location_fg_id     = fields.Many2one('stock.location', string='Finish Good Location',required=True, )
    default_location_siba_id   = fields.Many2one('stock.location', string='SIBA Location',required=True, )
    default_location_return_id = fields.Many2one('stock.location', string='Return Location',required=True, )
    default_picking_type_id    = fields.Many2one('stock.picking.type', string='Picking Type',required=True, )
    product_category_ids       = fields.Many2many(comodel_name='product.category', relation='rute_sale_product_category_rel',string='Product Category',required=True, )
    rute_sale_expense_ids      = fields.Many2many(comodel_name='rute.sale.expense', relation='rute_sale_expense_rel',string='Expense',required=True, )
    
    _sql_constraints = [
        ('warehouse_id_uniq', 'unique(name,warehouse_id)', 'Stock Point Harus Unik')
    ]
    
    
    @api.onchange('warehouse_id')
    def get_price(self):
        picking_type_id = self.env['stock.picking.type'].search([('warehouse_id','=',self.warehouse_id.id),('code','=','internal'),('is_stock_point','=',True)],limit=1)
        self.default_picking_type_id = picking_type_id.id
        self.default_location_fg_id = picking_type_id.default_location_src_id.id
        self.default_location_siba_id = picking_type_id.default_location_siba_id.id
        
        
    @api.model
    def create(self,vals):
        if vals.get('warehouse_id'):
            warehouse_id = self.env['stock.warehouse'].browse(vals.get('warehouse_id'))
            if warehouse_id:
                vals['name'] = 'Config' + ' '+ warehouse_id.name
                
        return super(RuteSaleConfig, self).create(vals)
    
        
    