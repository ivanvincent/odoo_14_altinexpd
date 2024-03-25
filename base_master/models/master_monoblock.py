from odoo import models, fields, api

class TipType(models.Model):
    _name = 'tip.type'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Description')
    price = fields.Float(string='Price')