from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpRoutingParameter(models.Model):
    _name = 'mrp.routing.parameter'

    name = fields.Char(string='Name')
    no_urut = fields.Integer(string='No Urut')
    plan = fields.Char(string='Plan')
    actual = fields.Char(string='Actual')
    uom_id = fields.Many2one('uom.uom', string='Uom')
    routing_id = fields.Many2one('mrp.routing.workcenter', string='Routing')
    parameter_id = fields.Many2one('master.parameter', string='Parameter')