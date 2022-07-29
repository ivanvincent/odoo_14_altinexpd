from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    
    
    def _get_color_id(self):
        for product in self:
            product.html_color = False
            design_id = product.product_template_attribute_value_ids.filtered(lambda x:x.attribute_id.name == "Kode Design")
            color = product.product_template_attribute_value_ids.filtered(lambda x:x.attribute_id.name == "WARNA")
            if len(color) > 1:
                product.color_id = color[0].product_attribute_value_id.id
            elif len(color) == 1:
                product.color_id = color.product_attribute_value_id.id
            else:
                product.color_id = False
            if len(design_id) > 1:
                design_id = design_id[0]
            color_final = self.env['labdip.color.final'].search([('labdip_id.name','=',design_id.name),('color_id','=',product.color_id.id)],limit=1)
            product.html_color = color_final.html_color
    
    
    color_id    = fields.Many2one('product.attribute.value', string='Color',compute="_get_color_id")
    warna_id    = fields.Many2one('product.attribute.value', string='Warna', related='color_id', store=True,)
    
    html_color  = fields.Char(string='Color Visualisation',compute="_get_color_id")
    std_potong  = fields.Float(string='Standar Potong')

    

class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    
    mrp_type_id = fields.Many2one('mrp.type', string='Production Type')

    