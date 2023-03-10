from shutil import move
from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    location_id = fields.Many2one('stock.location', string='Location')

    @api.model
    def create(self, values):
        # print('====================create===================')
        # print('values_account_move_line', values)
        # move_obj = self.env['account.move'].browse(values.get('move_id'))
        # location_obj = self.env['stock.location']

        # print('location_src_id', location_obj.browse(move_obj.stock_move_id.location_id.id).id)
        # print('location_dest_id', location_obj.browse(move_obj.stock_move_id.location_dest_id.id).id)
        # print('values', values)
        result = super(AccountMoveLine, self).create(values)
        return result

    def write(self, values):
        print('writteee', values)
        res = super(AccountMoveLine, self).write(values)
        return res