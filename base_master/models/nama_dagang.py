from odoo import models, fields, api

class NamaDagang(models.Model):
    _name = 'nama.dagang'

    name = fields.Char(string='Nama')