from odoo import models, fields, api, _
from odoo.exceptions import UserError
from  datetime import timedelta 
import logging
_logger = logging.getLogger(__name__)


class MrpProgram(models.Model):
    _name = 'mrp.program'

    name     = fields.Char(string='Program')
    description     = fields.Char(string='Description')
    date     = fields.Date(string='Date', default=fields.Date.today())
    duration = fields.Float(string='Duration')
    hours    = fields.Float(string='Hours', compute='_compute_hours', store=False, readonly=True)
    line_ids = fields.One2many('mrp.program.line', 'program_id', string='Details', copy=True)
    
    @api.depends('duration')
    def _compute_hours(self):
        for program in self:
            program.hours = program.duration / 60.0
    
class MrpProgramLine(models.Model):
    _name = 'mrp.program.line'

    name       = fields.Char(string='Proses')
    program_id = fields.Many2one('mrp.program', string='Program')
    no_urut    = fields.Integer(string='No Urut')
    suhu       = fields.Float(string='Suhu')
    time       = fields.Float(string='Time')
    deviasi    = fields.Float(string='Deviasi')
    tso_1       = fields.Boolean(string='TSO 1')
    tso_2       = fields.Boolean(string='TSO 2')
    tso_3       = fields.Boolean(string='TSO 3')
    tso_4       = fields.Boolean(string='TSO 4')
    tso_5       = fields.Boolean(string='TSO 5')
    tso_6       = fields.Boolean(string='TSO 6')
    tso_7       = fields.Boolean(string='TSO 7')
    tso_8       = fields.Boolean(string='TSO 8')