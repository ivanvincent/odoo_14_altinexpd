from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    workcenter_categ_id = fields.Many2one('mrp.workcenter.category', string='Category')
    machine_ids = fields.Many2many(comodel_name='mrp.machine', string='Machine Line')
    time_std    = fields.Float(string='Time Standard.')