

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    filter_product       = fields.Boolean(string='Filter Product',default=False)
    approval             = fields.Boolean(string='Approval',default=False)
    product_category_ids = fields.Many2many(comodel_name='product.category', string='Product Category')
    restrict_warehouse   = fields.Boolean(string='Restrict Warehouse',default=True)
    

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config             = self.env['ir.config_parameter'].sudo()
        filter_product        = ir_config.get_param('filter_product')
        approval              = ir_config.get_param('approval')
        product_category_ids  = ir_config.get_param('product_category_ids')
        restrict_warehouse  = ir_config.get_param('restrict_warehouse')
        res.update(
            filter_product=filter_product,
            approval=approval,
            restrict_warehouse=restrict_warehouse,
            product_category_ids=[(6, 0, literal_eval(product_category_ids))] if product_category_ids else False
        )
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("filter_product", self.filter_product or '')
        ir_config.set_param("approval", self.approval or '')
        ir_config.set_param("restrict_warehouse", self.restrict_warehouse or '')
        ir_config.set_param("product_category_ids", self.product_category_ids.ids)