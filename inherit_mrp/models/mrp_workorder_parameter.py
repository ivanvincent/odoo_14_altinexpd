from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpWorkorderParamater(models.Model):
    _name = 'mrp.workorder.parameter'

    name = fields.Char(string='Name')
    no_urut = fields.Integer(string='No Urut')
    plan = fields.Char(string='Plan')
    actual = fields.Char(string='Actual')
    uom_id = fields.Many2one('uom.uom', string='Uom')
    workorder_id = fields.Many2one('mrp.workorder', string='Workorder')
    parameter_id = fields.Many2one('master.parameter', string='Parameter')