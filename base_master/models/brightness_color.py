from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BrightnessColor(models.Model):
    _name = 'brightness.color'

    name        = fields.Char(string='Brightness')
    number_code = fields.Integer(string='Number Of Code')
    code        = fields.Char(string='Code')
    start_range = fields.Float(string='Start Of Range')
    end_range   = fields.Float(string='End Of Range')
    


class ProcessChemicalType(models.Model):
    _name = 'process.chemical.type'

    name        = fields.Char(string='Process Chamical Type')
    date        = fields.Date(string='Date', default=fields.Date.today())
    
    
    