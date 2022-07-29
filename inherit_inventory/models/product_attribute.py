from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    @api.constrains('name')
    def _constrains_name(self):
        me_obj = self.search([('name', '=', self.name), ('id','!=',self.id)])
        if me_obj:
            raise UserError("Mohon maaf nama attribute harus uniq!")