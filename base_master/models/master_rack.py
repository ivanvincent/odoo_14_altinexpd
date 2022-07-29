from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MasterRack(models.Model):
    _name = 'master.rack'

    name         = fields.Char(string='Rack')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    location_id  = fields.Many2one('stock.location', string='Stock Location')
    