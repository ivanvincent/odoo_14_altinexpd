from odoo import models, fields, api

class KodeMkt(models.Model):
    _name = 'kode.mkt'

    name = fields.Char(string='Name')