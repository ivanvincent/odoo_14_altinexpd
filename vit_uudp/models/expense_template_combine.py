from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ExpenseTemplateCombine(models.Model):
    _name = 'expense.template.combine'

    name          = fields.Char(string='Template Kombinasi')
    warehouse_ids = fields.Many2many(comodel_name='stock.warehouse', string='Stock Point')
    jalur_ids     = fields.Many2many(comodel_name='res.partner.jalur', string='Jalur')
    user_id       = fields.Many2one('res.users', string='User',default=lambda self: self.env.user.id)
    line_ids      = fields.One2many('expense.template.combine.line', 'template_id', 'Details')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'nama template harus unik !')
    ]

class ExpenseTemplateCombineLine(models.Model):
    _name = 'expense.template.combine.line'

    
    template_id = fields.Many2one('expense.template.combine', string='Template')
    product_id  = fields.Many2one('product.product', string='Product')
    account_id  = fields.Many2one('account.account', string='Account')
    nominal     = fields.Float(string='Nominal')
    