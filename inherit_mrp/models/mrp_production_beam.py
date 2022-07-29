from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpProductionBeam(models.Model):
    _name = 'mrp.production.beam'

    name         = fields.Char(string='Beam')
    default_code = fields.Char(string='Code')
    type_id      = fields.Many2one('mrp.production.beam.type', string='Beam Type')
    
    
class MrpProductionBeam(models.Model):
    _name = 'mrp.production.beam.type'

    name            = fields.Char(string='Beam Type')
    description     = fields.Char(string='Description')