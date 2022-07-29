from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    bank_va_no = fields.Char(string='Virtual Account Bank')
    pay_6988 = fields.Boolean(string='Pay With 376 302 6988 ?')