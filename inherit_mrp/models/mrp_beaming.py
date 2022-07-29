from odoo import models, fields, api

class MrpBeaming(models.Model):
    _name = 'mrp.beaming'

    kode_prod = fields.Char(string='Kode Prod')
    te_helai = fields.Char(string='TE (Helai)')
    qty_beam = fields.Float(string='Pjg/Beam')
    jml_beam = fields.Float(string='Jumlah beam')
    type_beam_id = fields.Many2one('type.beam', string='Type beam')
    lebar_beam = fields.Float(string='Lebar Beam')
    total_panjang = fields.Float(string='Total Panjang')
    unit_wv = fields.Char(string='Unit WV')
    date = fields.Date(string='Date')
    production_id = fields.Many2one('mrp.production', string='MO')