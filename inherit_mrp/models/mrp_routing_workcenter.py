from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpRoutingWorkCenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    mesin_id               = fields.Many2one('mrp.machine', string='Machine')
    routing_paramter_ids   = fields.One2many('mrp.routing.parameter', 'routing_id', string='Routing')
    program_id             = fields.Many2one('mrp.program', string='Program')
    hours                  = fields.Float(string='Hours',related="program_id.hours")
    duration               = fields.Float(string='Duration',related="program_id.duration")
    
    
