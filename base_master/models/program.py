from odoo import models, fields, api

class Program(models.Model):
    _name = 'program'

    name = fields.Char(string='Name')