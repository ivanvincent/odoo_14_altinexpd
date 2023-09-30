from odoo import models, fields, api

class Specifications(models.Model):
    _name = 'specifications'
    _rec_name = 'spect_name'

    name = fields.Char(string='Kode Master')
    jenis_id = fields.Many2one('master.jenis', string='Jenis')
    spec_id = fields.Many2one('master.require', string='Spec',
    # domain="[('jenis_ids', 'in', jenis_id)]"
    )
    spect_name = fields.Char(string='Kode')
    desc = fields.Char(string='Nama Spefisikasi')
    desc_detail = fields.Text(string='Deskripsi Detail')
    harga = fields.Float(string='Harga')
    urutan = fields.Integer(string='Urutan', default=999)
    active = fields.Boolean(string='Active ?', default=True)
    state = fields.Selection(
        [("draft", "Draft"), ("confirm", "Confirm")], string='State', default='draft')
    deskripsi = fields.Char(string='Deskripsi')
    rumus_subtotal = fields.Char('Rumus Subtotal')
    rumus_total = fields.Char('Rumus Total')