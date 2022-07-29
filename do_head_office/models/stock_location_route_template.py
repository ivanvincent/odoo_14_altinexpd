from odoo import models, fields, api, _
from odoo.exceptions import UserError

_PROCURE_METHOD = [
    ("make_to_stock", "Take From Stock"),
    ("make_to_order", "Trigger Another Rule"),
    ("mts_else_mto", "Take From Stock, if unavailable, Trigger Another Rule"),
]

class StockLocationRouteTemplate(models.Model):
    _name = 'stock.location.route.template'

    name             = fields.Char(string='Route Template')
    action_type      = fields.Selection([("pull","Pull From"),("push","Push To")], string='Action',default="pull",required=True,)
    src_location_id  = fields.Many2one('stock.location', string='Source Location')
    dest_location_id = fields.Many2one('stock.location', string='Dest Location')
    picking_type_id  = fields.Many2one('stock.picking.type', string='Operation Type')
    procure_method   = fields.Selection(selection=_PROCURE_METHOD, string='Supply Method', default='make_to_stock', required=True,index=True)
    auto             = fields.Selection([("manual","Manual Operation"),("transparent","Automatic No Step Added")], string='Automatic Move', default='manual', index=True, required=True,)
    active           = fields.Boolean(string='Active ?',default=True)