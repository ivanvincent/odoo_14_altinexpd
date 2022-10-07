# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

import odoo.addons.decimal_precision as dp



class ProductTemplate(models.Model):
    _inherit = "product.template"

    construct_ids = fields.One2many('mrp.textile.construction', 'product_tmpl_id', 'Bill of Materials')
    textile_product = fields.Boolean("Textile Product", default=False)
    yarn = fields.Boolean("Yarn", default=False)
    size = fields.Float("Size")




class MrpTextileConstruction(models.Model):
    """ Defines bills of material for a product or a product template """
    _name = 'mrp.textile.construction'
    _description = 'Textile Construction'

    _rec_name = 'product_tmpl_id'

    name = fields.Char("Name")
    product_tmpl_id = fields.Many2one('product.template', 'Product', domain="[('textile_product', '=', True)]", required=True)
    product_id = fields.Many2one('product.product', "Yarn", domain="[('product_tmpl_id.yarn', '=', True)]")
    size = fields.Float('Size', related="product_id.size", store=True)
    struct_persentage = fields.Float("Structure Percentage")



    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.name=''
        if self.product_id:
            self.name = self.product_id.name


