from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    grm_greige	= fields.Float('Gramasi Greige')
    lbr_greige	= fields.Float('Lebar Greige')