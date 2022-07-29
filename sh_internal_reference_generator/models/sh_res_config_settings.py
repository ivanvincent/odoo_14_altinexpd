# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _


class ShResCompany(models.Model):
    _inherit = 'res.company'
    
    sh_product_int_ref_generator = fields.Boolean(string="Product Internal Reference Generator Feature")
    sh_product_name_config = fields.Boolean(string="Product Name Config")
    sh_product_name_digit = fields.Char(string="Product Name Digit", default="4")
    sh_product_name_separate = fields.Char(string="Product Name Separate")
    sh_product_attribute_config = fields.Boolean(string="Product Attribute Config")
    sh_product_attribute_name_digit = fields.Char(string="Product Attribute Name Digit", default="1")
    sh_product_attribute_name_separate = fields.Char(string="Product Attribute Name Separate")
    sh_product_cataegory_config = fields.Boolean(string="Product Category Config")
    sh_product_category_digit = fields.Char(string="Product Category Digit", default="3")
    sh_product_catagory_separate = fields.Char(string="Product Category Separate")
    sh_product_sequence_config = fields.Boolean(string="Product Sequence Config")
    sh_product_sequence = fields.Many2one('ir.sequence', string="Product Sequence")
    sh_product_sequence_separate = fields.Char(string="Product Sequence Separate")
    sh_new_product_int_ref_generator = fields.Boolean(string="Auto Generate Internal Reference For New Products")


class ShResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    sh_product_int_ref_generator = fields.Boolean(string="Product Internal Reference Generator Feature", related="company_id.sh_product_int_ref_generator", readonly=False)
    sh_product_name_config = fields.Boolean(string="Product Name Config", related="company_id.sh_product_name_config", readonly=False)
    sh_product_name_digit = fields.Char(string="Product Name Digit", default="4", related="company_id.sh_product_name_digit", readonly=False)
    sh_product_name_separate = fields.Char(string="Product Name Separate", related="company_id.sh_product_name_separate", readonly=False)
    sh_product_attribute_config = fields.Boolean(string="Product Attribute Config", related="company_id.sh_product_attribute_config", readonly=False)
    sh_product_attribute_name_digit = fields.Char(string="Product Attribute Name Digit", default="1", related="company_id.sh_product_attribute_name_digit", readonly=False)
    sh_product_attribute_name_separate = fields.Char(string="Product Attribute Name Separate", related="company_id.sh_product_attribute_name_separate", readonly=False)
    sh_product_cataegory_config = fields.Boolean(string="Product Category Config", related="company_id.sh_product_cataegory_config", readonly=False, default="4v")
    sh_product_category_digit = fields.Char(string="Product Category Digit", default="3", related="company_id.sh_product_category_digit", readonly=False)
    sh_product_catagory_separate = fields.Char(string="Product Category Separate", related="company_id.sh_product_catagory_separate", readonly=False)
    sh_product_sequence_config = fields.Boolean(string="Product Sequence Config", related="company_id.sh_product_sequence_config", readonly=False)
    sh_product_sequence = fields.Many2one('ir.sequence', string="Product Sequence", related="company_id.sh_product_sequence", readonly=False)
    sh_product_sequence_separate = fields.Char(string="Product Sequence Separate", related="company_id.sh_product_sequence_separate", readonly=False)
    sh_new_product_int_ref_generator = fields.Boolean(string="Auto Generate Internal Reference For New Products", related="company_id.sh_new_product_int_ref_generator", readonly=False)

    def action_generate_int_ref(self):
        return {
            'name':'Generate Internal Reference',
            'type':'ir.actions.act_window',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'internal.reference.wizard',
            'target':'new',
            }
