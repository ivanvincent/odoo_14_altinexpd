from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging 

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    # @api.model
    # def name_get(self):
    #     context = self.env.context
        
    #     if not context.get('name_product_without_code'):
    #         return super(ProductProduct,self).name_get()
        
    #     res = []
    #     picking_id = context.get('default_picking_id')
    #     picking_id = self.env['stock.picking'].browse([picking_id]) if picking_id else False
        
    #     if context.get('name_product_without_code') \
    #         and (picking_id and picking_id.picking_type_id.warehouse_id.code  == 'GDGK') \
    #         or self.env.user.id == 2 \
    #         or (self.env.user.default_warehouse_ids and 'GDGK' in self.env.user.default_warehouse_ids.mapped('code')):
    #         for record in self:
    #             displayName = '%s'%(record.name)
    #             res.append((record.id,displayName))
        
        
            
    #     return res
    
    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     res_search = False
    #     res = self.search(['|','|',('name',operator,name),('default_code', operator, name),('product_template_attribute_value_ids.name', operator, name)] + args, limit=limit)
    #     res_search = res.name_get()
    #     return res_search