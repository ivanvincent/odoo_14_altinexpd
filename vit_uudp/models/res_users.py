from odoo import fields, api, models

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    
    allowed_category = fields.Many2many(comodel_name='uudp.category', relation='user_uudp_category_rel',string='Allowed Category',help="User uudp allowed category")
    
    

    # @api.multi
    # def name_get(self):
    #     res = []
    #     for x in self:
    #         name = '['+x.login+'] '+x.name
    #         res.append((x.id, name))
    #     return res

# ResUsers()