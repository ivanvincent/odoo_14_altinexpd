from odoo import models, fields, api

class TypeBeam(models.Model):
    _name = 'type.beam'

    name = fields.Char(string='Name')