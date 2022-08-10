from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpParameter(models.Model):
    _name = 'mrp.parameter'

    name        = fields.Char(string='Parameter')
    uom_id      = fields.Many2one('uom.uom', string='Uom')
    description = fields.Text(string='Descriptions')