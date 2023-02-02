from odoo import models, fields, api

class Machine(models.Model):
    _name = 'machine'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')