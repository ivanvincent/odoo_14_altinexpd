from odoo import models, fields, api

class Size(models.Model):
    _name = 'size'

    name = fields.Char(string='Size')