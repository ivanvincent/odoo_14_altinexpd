from odoo import models, fields, api

class Specifications(models.Model):
    _name = 'specifications'

    jenis_id = fields.Many2one('master.jenis', string='Jenis')
    spec_id = fields.Many2one('master.require', string='Spec',domain="[('jenis_ids', 'in', jenis_id)]")
    spect_name = fields.Char(string='Nama Spefisikasi')
    desc = fields.Char(string='Desc')
    harga = fields.Float(string='Harga')
    active = fields.Boolean(string='Active ?', Default=True)