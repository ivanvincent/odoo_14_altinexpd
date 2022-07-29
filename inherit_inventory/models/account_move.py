from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    date_datang_barang = fields.Date(string='Datang barang')
    picking_id = fields.Many2one('stock.picking', string='No Picking')