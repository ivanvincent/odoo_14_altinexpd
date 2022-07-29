from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    image_ids = fields.One2many('account.move.line.images', 'account_move_line_id', string='Images')
    location_src_id = fields.Many2one('stock.location', string='Source Location', store=True, related="move_id.stock_move_id.location_id")
    location_dest_id = fields.Many2one('stock.location', string='Destination Location', store=True, related="move_id.stock_move_id.location_dest_id")
    location_id = fields.Many2one('stock.location', string='Location')

    def action_show_image(self):
        action = self.env.ref('inherit_accounting.account_move_action').read()[0]
        action['res_id'] = self.id
        action['name'] = 'Image of %s' % (self.product_id.id)
        return action