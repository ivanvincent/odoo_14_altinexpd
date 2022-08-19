from odoo import models, fields, api

class Treatment(models.Model):
    _name = 'treatment'

    name = fields.Char(string='Name')