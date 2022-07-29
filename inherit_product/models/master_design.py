from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class MasterDesign(models.Model):
    _name = 'master.design'

    name                = fields.Char(string='Design')
    date                = fields.Date(string='Date', default=fields.Date.today())
    user_id             = fields.Many2one('res.users', string='User',default=lambda self: self.env.user)
    greige_id           = fields.Many2one('product.product', string='Greige',required=False,domain=[('categ_id.name', '=', 'GREY')])
    product_id          = fields.Many2one('product.template', string='Product',required=False,domain=[('categ_id.name', '=', 'KAIN')])
    note                = fields.Text(string='Note')
    line_ids            = fields.One2many('master.design.line', 'design_id', string='Design')
    create_variant      = fields.Selection([
        ('always', 'Instantly'),
        ('dynamic', 'Dynamically'),
        ('no_variant', 'Never')],
        default='always',
        string="Variants Creation Mode",
        help="""- Instantly: All possible variants are created as soon as the attribute and its values are added to a product.
        - Dynamically: Each variant is created only when its corresponding attributes and values are added to a sales order.
        - Never: Variants are never created for the attribute.
        Note: the variants creation mode cannot be changed once the attribute is used on at least one product.""",
        required=True)
    labdip_id           = fields.Many2one('labdip', string='Labdip')
    
    


    # @api.model
    # def create(self,vals):
    #     roman_dict = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'}
    #     roman = roman_dict[int(datetime.now().strftime("%m"))]
    #     next_number = self.env['ir.sequence'].next_by_code('labdip.new')
    #     # next_number = self.env['ir.sequence'].next_by_code('master.design.code')
    #     # next_number = self.env['ir.sequence'].next_by_code('master.design.code')
    #     years = datetime.now().strftime('%Y')
    #     design_code = '%s/%s/%s-%s' % (next_number, 'LAB', roman, years)
    #     vals['name'] = design_code if vals.get('name') == 'new' else vals.get('name')
        
        
    #     res = super(MasterDesign, self).create(vals)
    #     return res
    
    
        
        
    
class MasterDesignLine(models.Model):
    _name = 'master.design.line'

    name                = fields.Char(string='Color',related='color_id.name')
    variant_id          = fields.Many2one('product.product', string='Variant')
    greige_id           = fields.Many2one('product.product', string='Greige',domain=[('categ_id.name', '=', 'GREY')])
    design_id           = fields.Many2one('master.design', string='Design')
    color_id            = fields.Many2one('product.attribute.value',string='Color', domain=[('attribute_id.name', '=', 'WARNA')])
    
    
    
    
    
    def create_variant(self):
        color_attr = self.env['product.template.attribute.line'].sudo().search([('product_tmpl_id','=',self.design_id.product_id.id),('attribute_id.name','=','WARNA')],limit=1)
        if color_attr:
            color_attr.sudo().write({
                "value_ids":[(4,self.color_id.id)],
            })
            
        product_ids = self.env['product.product'].sudo().search([('product_tmpl_id','=',self.design_id.product_id.id)])
        variant_id = None
        for variant in product_ids:
            for value in variant.product_template_attribute_value_ids.filtered(lambda x:x.product_attribute_value_id.id in (self.color_id.id,self.design_id.id)):
                variant_id = variant.id
        self.variant_id = variant_id
                
            
        
    


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'
    
    
    design_id   = fields.Many2one('master.design', string='Design')
    color_code  = fields.Char(string='Color Code')
        


    
    


    
