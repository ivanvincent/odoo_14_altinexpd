from odoo import models, fields, api

class Attn(models.Model):
    _name = 'attn'

    name = fields.Char(string='Name')