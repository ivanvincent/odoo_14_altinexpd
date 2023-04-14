from odoo import models, fields, api

class CupDepth(models.Model):
    _name = 'cup.depth'

    name = fields.Char(string='Name')