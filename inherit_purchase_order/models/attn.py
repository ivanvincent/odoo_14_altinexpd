from odoo import models, fields, api

class Attn(models.Model):
    _name = 'attn'

    name    = fields.Char(string='Name')
    alamat  = fields.Text(string='Alamat')
    kota    = fields.Char(string='Kota')
    phone   = fields.Char(string='Phone')
    mobile  = fields.Char(string='Mobile')
    fax     = fields.Char(string='Fax')
    email   = fields.Char(string='Email')
    active  = fields.Boolean("Active", default=True)
    partner_id = fields.Many2one('res.partner', string='Partner')