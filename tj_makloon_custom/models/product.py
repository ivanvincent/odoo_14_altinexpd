from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_group_category = fields.Many2one('product.template.group.category','Group Category')

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        total = 0
        if self.textile_product==True and self.construct_ids:
            for rec in self.construct_ids:
                total += rec.struct_persentage
            if (total <100):
                raise UserError(_('Material Harus 100%'))
            elif (total > 100):
                raise UserError(_('Material Lebih Dari 100%'))
        return res

    # @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        total = 0
        if self.textile_product == True and self.construct_ids:
            for rec in self.construct_ids:
                total += rec.struct_persentage
            if (total < 100):
                raise UserError(_('Material Harus 100%'))
            elif (total > 100):
                raise UserError(_('Material Lebih Dari 100%'))
        return res

class ProductTemplateCategory(models.Model):
    _name = "product.template.group.category"
    name = fields.Char('Name', )