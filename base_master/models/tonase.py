from odoo import models, fields, api

class Tonase(models.Model):
    _name = 'tonase'

    name = fields.Char(string='Name')