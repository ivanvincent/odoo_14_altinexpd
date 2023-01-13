from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    sequence_code_po = fields.Char(string='Sequence Purchase', required=True, help="For sequence PO")
    # group_reporting = fields.Selection([("stock","Stock"),("benang","Benang"),("greige","Greige")], string='Group Reporting')