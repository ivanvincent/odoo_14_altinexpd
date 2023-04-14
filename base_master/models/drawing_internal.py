from odoo import models, fields, api

class DrawingInternal(models.Model):
    _name = 'drawing.internal'

    name = fields.Char(string='Name')