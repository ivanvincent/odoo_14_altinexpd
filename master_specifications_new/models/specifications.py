<<<<<<< HEAD
from odoo import models, fields, api

class Specifications(models.Model):
    _name = 'specifications.new'
    _rec_name = 'desc'

    name = fields.Char(string='Kode Master')
    jenis_id = fields.Many2one('master.jenis.new', string='Jenis')
    spec_id = fields.Many2one('master.require.new', string='Spec',
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
=======
from odoo import models, fields, api

class Specifications(models.Model):
    _name = 'specifications.new'
    _rec_name = 'desc'

    name = fields.Char(string='Kode Master')
    jenis_id = fields.Many2one('master.jenis.new', string='Jenis')
    spec_id = fields.Many2one('master.require.new', string='Spec',
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
>>>>>>> 42cdb9030f851b5fe403eed06a6fc058da9468d8
    unit = fields.Many2one('master.qty.new', string = 'Unit')