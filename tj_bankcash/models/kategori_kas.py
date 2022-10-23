from odoo import models, fields, api

class KategoriKas(models.Model):
    _name = 'kategori.kas'

    name = fields.Char(string='Name')
    type = fields.Selection([("terima","Terima"),("keluar","Keluar")], string='Type')