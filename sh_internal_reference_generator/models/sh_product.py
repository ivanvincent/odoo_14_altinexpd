# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ShProductTemplate(models.Model):
    _inherit = 'product.template'

    # partner_id = fields.Many2one("res.partner", "Partner")
    # part_no = fields.Char(string="Part No")
    # sku_no = fields.Char(string="SKU No")

    @api.model
    def create(self, vals):
        res = super(ShProductTemplate, self).create(vals)
        company = self.env.user.company_id        
        if company and company.sh_product_int_ref_generator == True and company.sh_new_product_int_ref_generator == True:
            sequence = self.env['ir.sequence'].next_by_code(company.sh_product_sequence.code)
            product_template_sequence = ''
            if company.sh_product_name_config == True:
                product_name = str(res.name)
                if int(company.sh_product_name_digit) >= 1:
                    product_name = product_name[:int(company.sh_product_name_digit)]
                    if " " in product_name:
                        if company.sh_product_name_separate:
                            product_name = product_name.replace(" ", str(company.sh_product_name_separate))
                            if company.sh_product_sequence_separate:
                                product_template_sequence = product_template_sequence + product_name[:int(company.sh_product_name_digit)] + str(company.sh_product_sequence_separate)
                            else:
                                product_template_sequence = product_template_sequence + product_name[:int(company.sh_product_name_digit)]
                        else:
                            if company.sh_product_sequence_separate:
                                product_template_sequence = product_template_sequence + product_name[:int(company.sh_product_name_digit)] + str(company.sh_product_sequence_separate)
                            else:
                                product_template_sequence = product_template_sequence + product_name[:int(company.sh_product_name_digit)]
                    else:
                        if company.sh_product_sequence_separate:
                            product_template_sequence = product_template_sequence + product_name[:int(company.sh_product_name_digit)] + str(company.sh_product_sequence_separate)
                        else:
                            product_template_sequence = product_template_sequence + product_name[:int(company.sh_product_name_digit)]
             
            if company.sh_product_attribute_config == True:
                if int(company.sh_product_attribute_name_digit) >= 1:
                    if res.attribute_line_ids:
                        atrributes_name = []
                        for attribute in res.attribute_line_ids:
                            for value in attribute.value_ids:
                                atrributes_name.append(value.name)
                        for atrributes_value in atrributes_name:
                            value = atrributes_value
                            value = value[:int(company.sh_product_attribute_name_digit)]
                            if " " in value:
                                if company.sh_product_attribute_name_separate:
                                    value = value.replace(" ", str(company.sh_product_attribute_name_separate))
                                    if company.sh_product_sequence_separate:
                                        product_template_sequence += value[:int(company.sh_product_attribute_name_digit)] + str(company.sh_product_sequence_separate)
                                    else:
                                        product_template_sequence += value[:int(company.sh_product_attribute_name_digit)]
                                else:
                                    if company.sh_product_sequence_separate:
                                        product_template_sequence += value[:int(company.sh_product_attribute_name_digit)] + str(company.sh_product_sequence_separate)
                                    else:
                                        product_template_sequence += value[:int(company.sh_product_attribute_name_digit)]
                            else:
                                if company.sh_product_sequence_separate:
                                    product_template_sequence += value[:int(company.sh_product_attribute_name_digit)] + str(company.sh_product_sequence_separate)
                                else:
                                    product_template_sequence += value[:int(company.sh_product_attribute_name_digit)]
            if company.sh_product_cataegory_config == True:
                category_name = str(res.categ_id.name)
                if int(company.sh_product_category_digit) >= 1:
                    category_name = category_name[:int(company.sh_product_category_digit)]
                    if " " in category_name:
                        if company.sh_product_catagory_separate:
                            category_name = category_name.replace(" ", str(company.sh_product_catagory_separate))
                            if company.sh_product_sequence_separate:
                                product_template_sequence += category_name[:int(company.sh_product_category_digit)] + str(company.sh_product_sequence_separate)
                            else:
                                product_template_sequence += category_name[:int(company.sh_product_category_digit)]
                        else:
                            if company.sh_product_sequence_separate:
                                product_template_sequence += category_name[:int(company.sh_product_category_digit)] + str(company.sh_product_sequence_separate)
                            else:
                                product_template_sequence += category_name[:int(company.sh_product_category_digit)]
                    else:
                        if company.sh_product_sequence_separate:
                            product_template_sequence += category_name[:int(company.sh_product_category_digit)] + str(company.sh_product_sequence_separate)
                        else:
                            product_template_sequence += category_name[:int(company.sh_product_category_digit)]
            if company.sh_product_sequence_config == True and company.sh_product_sequence:
                product_template_sequence += str(sequence)
            if product_template_sequence.endswith(str(company.sh_product_sequence_separate)):
                product_template_sequence = product_template_sequence[:-1]
            if product_template_sequence != '':
                categ_benang = self.env['product.category'].browse(vals.get('categ_id'))
                name_bng = categ_benang.name
                if 'BENANG' in name_bng or 'Benang' in name_bng:
                    if not categ_benang.code:
                        raise UserError('Silahkan isi "code" terlebih dahulu pada master product category')
                
                    product = vals.get('name')[0:3]
                    categ = categ_benang.code
                    run_number = self.env['ir.sequence'].next_by_code('seq.product.benang')
                    res.default_code = '%s/%s/%s' % (product, categ, run_number)
                else:
                    res.default_code = product_template_sequence
        return res


class ShProduct(models.Model):
    _inherit = 'product.product'    

    # partner_id = fields.Many2one("res.partner", "Partner")
    # part_no = fields.Char(string="Part No")
    # sku_no = fields.Char(string="SKU No")

    @api.model
    def create(self, vals):
        res = super(ShProduct, self).create(vals)
        company = self.env.user.company_id
        if company and company.sh_product_int_ref_generator == True and company.sh_new_product_int_ref_generator == True:
            sequence = self.env['ir.sequence'].next_by_code(company.sh_product_sequence.code)
            product_sequence = ''
            if company.sh_product_name_config == True:
                product_name = str(res.name)
                if int(company.sh_product_name_digit) >= 1:
                    product_name = product_name[:int(company.sh_product_name_digit)]
                    if " " in product_name:
                        if company.sh_product_name_separate:
                            product_name = product_name.replace(" ", str(company.sh_product_name_separate))
                            if company.sh_product_sequence_separate:
                                product_sequence = product_sequence + product_name[:int(company.sh_product_name_digit)] + str(company.sh_product_sequence_separate)
                            else:
                                product_sequence = product_sequence + product_name[:int(company.sh_product_name_digit)]
                        else:
                            if company.sh_product_sequence_separate:
                                product_sequence = product_sequence + product_name[:int(company.sh_product_name_digit)] + str(company.sh_product_sequence_separate)
                            else:
                                product_sequence = product_sequence + product_name[:int(company.sh_product_name_digit)]
                    else:
                        if company.sh_product_sequence_separate:
                            product_sequence = product_sequence + product_name[:int(company.sh_product_name_digit)] + str(company.sh_product_sequence_separate)
                        else:
                            product_sequence = product_sequence + product_name[:int(company.sh_product_name_digit)]
                     
            if company.sh_product_attribute_config == True:
                if int(company.sh_product_attribute_name_digit) >= 1:
                    if res.product_template_attribute_value_ids:
                        atrributes_name = []
                        for attribute in res.product_template_attribute_value_ids:
                            for value in attribute.product_attribute_value_id:
                                atrributes_name.append(value.name)
                        for atrributes_value in atrributes_name:
                            value = atrributes_value
                            value = value[:int(company.sh_product_attribute_name_digit)]
                            if " " in value:
                                if company.sh_product_attribute_name_separate:
                                    value = value.replace(" ", str(company.sh_product_attribute_name_separate))
                                    if company.sh_product_sequence_separate:
                                        product_sequence += value[:int(company.sh_product_attribute_name_digit)] + str(company.sh_product_sequence_separate)
                                    else:
                                        product_sequence += value[:int(company.sh_product_attribute_name_digit)]
                                else:
                                    if company.sh_product_sequence_separate:
                                        product_sequence += value[:int(company.sh_product_attribute_name_digit)] + str(company.sh_product_sequence_separate)
                                    else:
                                        product_sequence += value[:int(company.sh_product_attribute_name_digit)]
                            else:
                                if company.sh_product_sequence_separate:
                                    product_sequence += value[:int(company.sh_product_attribute_name_digit)] + str(company.sh_product_sequence_separate)
                                else:
                                    product_sequence += value[:int(company.sh_product_attribute_name_digit)]
            if company.sh_product_cataegory_config == True:
                category_name = str(res.categ_id.name)
                if int(company.sh_product_category_digit) >= 1:
                    category_name = category_name[:int(company.sh_product_category_digit)]
                    if " " in category_name:
                        if company.sh_product_catagory_separate:
                            category_name = category_name.replace(" ", str(company.sh_product_catagory_separate))
                            if company.sh_product_sequence_separate:
                                product_sequence += category_name[:int(company.sh_product_category_digit)] + str(company.sh_product_sequence_separate)
                            else:
                                product_sequence += category_name[:int(company.sh_product_category_digit)]
                        else:
                            if company.sh_product_sequence_separate:
                                product_sequence += category_name[:int(company.sh_product_category_digit)] + str(company.sh_product_sequence_separate)
                            else:
                                product_sequence += category_name[:int(company.sh_product_category_digit)]
                    else:
                        if company.sh_product_sequence_separate:
                            product_sequence += category_name[:int(company.sh_product_category_digit)] + str(company.sh_product_sequence_separate)
                        else:
                            product_sequence += category_name[:int(company.sh_product_category_digit)]
            if company.sh_product_sequence_config == True and company.sh_product_sequence:
                product_sequence += str(sequence)
            if product_sequence.endswith(str(company.sh_product_sequence_separate)):
                product_sequence = product_sequence[:-1]
            if product_sequence != '':
                if 'categ_id' in vals:
                    categ_benang = self.env['product.category'].browse(vals.get('categ_id'))
                    name_bng = categ_benang.name
                    if 'BENANG' in name_bng or 'Benang' in name_bng:
                        if not categ_benang.code:
                            raise UserError('Silahkan isi "code" terlebih dahulu pada master product category')
                    
                        product = vals.get('name')[0:3]
                        categ = categ_benang.code
                        run_number = self.env['ir.sequence'].next_by_code('seq.product.benang')
                        res.default_code = '%s/%s/%s' % (product, categ, run_number)
                    else:
                        res.default_code = product_sequence
                else:
                    res.default_code = product_sequence
        if 'generatorless' in self._context:
            res.default_code = vals.get('default_code')
        return res
