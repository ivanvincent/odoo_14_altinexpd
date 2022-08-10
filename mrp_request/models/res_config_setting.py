from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    mor_sequence_id          = fields.Many2one('ir.sequence', string='MOR Sequence')
    mor_filter_product       = fields.Boolean(string='Filter Product',default=True)
    mor_product_category_ids = fields.Many2many(comodel_name='product.category', relation='mor_product_category_rel',string='Product Category')
    wo_sequence_id           = fields.Many2one('ir.sequence', string='WO Sequence')
    
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config                = self.env['ir.config_parameter'].sudo()
        mor_filter_product       = ir_config.get_param('mor_filter_product')
        mor_product_category_ids   = ir_config.get_param('mor_product_category_ids')
        mor_sequence_id  = ir_config.get_param('mor_sequence_id')
        wo_sequence_id  = ir_config.get_param('wo_sequence_id')
        
        res.update(
            mor_filter_product=mor_filter_product,
            mor_sequence_id=int(mor_sequence_id),
            wo_sequence_id=int(wo_sequence_id),
            mor_product_category_ids=[(6, 0, literal_eval(mor_product_category_ids))] if mor_product_category_ids else False,
        )
        
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("mor_filter_product", self.mor_filter_product or False)
        ir_config.set_param("mor_product_category_ids", self.mor_product_category_ids.ids)
        ir_config.set_param("mor_sequence_id", self.mor_sequence_id.id)
        ir_config.set_param("wo_sequence_id", self.wo_sequence_id.id)
        
        
        
        