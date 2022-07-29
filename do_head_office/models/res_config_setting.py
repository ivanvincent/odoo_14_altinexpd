

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    do_filter_product             = fields.Boolean(string='Filter Product',default=False)
    do_filter_warehouse           = fields.Boolean(string='Filter Warehouse',default=False)
    restrict_warehouse             = fields.Boolean(string='Restrict Warehouse',default=False)
    do_product_category_ids       = fields.Many2many(comodel_name='product.category', relation='do_product_category_rel',string='Product Category')
    do_warehouse_src_ids          = fields.Many2many(comodel_name='stock.warehouse', relation='do_warehouse_config_rel',string='Source Warehouse')
    vehicle_picking_type_id       = fields.Many2one('stock.picking.type', string='Vehicle Transit Operation Type')
    vehicle_return_picking_type_id = fields.Many2one('stock.picking.type', string='Vehicle Return Operation Type')
    

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config                = self.env['ir.config_parameter'].sudo()
        do_filter_product        = ir_config.get_param('do_filter_product')
        do_filter_warehouse      = ir_config.get_param('do_filter_warehouse')
        do_product_category_ids  = ir_config.get_param('do_product_category_ids')
        do_warehouse_src_ids     = ir_config.get_param('do_warehouse_src_ids')
        vehicle_picking_type_id  = ir_config.get_param('vehicle_picking_type_id')
        vehicle_return_picking_type_id  = ir_config.get_param('vehicle_return_picking_type_id')
        res.update(
            do_filter_product=do_filter_product,
            do_filter_warehouse=do_filter_warehouse,
            vehicle_picking_type_id=int(vehicle_picking_type_id),
            vehicle_return_picking_type_id=int(vehicle_return_picking_type_id),
            do_product_category_ids=[(6, 0, literal_eval(do_product_category_ids))] if do_product_category_ids else False,
            do_warehouse_src_ids=[(6, 0, literal_eval(do_warehouse_src_ids))] if do_warehouse_src_ids else False
        )
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("do_filter_product", self.do_filter_product or False)
        ir_config.set_param("do_filter_warehouse", self.do_filter_warehouse or False)
        ir_config.set_param("do_product_category_ids", self.do_product_category_ids.ids)
        ir_config.set_param("do_warehouse_src_ids", self.do_warehouse_src_ids.ids)
        ir_config.set_param("vehicle_picking_type_id", self.vehicle_picking_type_id.id)
        ir_config.set_param("vehicle_return_picking_type_id", self.vehicle_return_picking_type_id.id)