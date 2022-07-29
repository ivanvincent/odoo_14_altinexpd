from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    supplier_id = fields.Many2one('res.partner', string='Supplier')
    just_flag = fields.Boolean(string='Flag ?', store=False,) #Flag For Change Domain Product

    @api.onchange('just_flag')
    def _onchange_just_flag(self):
        """
            User id 2 = Administrator
        """
        user = self.env.user.id
        if user != 2:
            res = {}
            categ_ids = [category.id  for warehouse in self.env.user.default_warehouse_ids for category in warehouse.product_category_ids] #settingan ada di user (res.users)
            res['domain'] = {'product_id': [('categ_id', 'in', categ_ids)]}
            return res