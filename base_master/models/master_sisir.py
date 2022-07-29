from odoo import models, fields, api

class MasterSisir(models.Model):
    _name = 'master.sisir'

    name        = fields.Char(string='Nomor Sisir')
    lebar_sisir = fields.Float(string='Lebar Sisir')
    uom_id      = fields.Many2one('uom.uom', string='Uom')
    
    