from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    
    parent_coa_id    = fields.Many2one('account.account', string='COA Parent Id',context={'show_parent_account':True})
    need_approve_knd = fields.Boolean(string='Need Approve KND ?')
    staff_knd_id     = fields.Many2one('hr.employee', string='Staff KND')