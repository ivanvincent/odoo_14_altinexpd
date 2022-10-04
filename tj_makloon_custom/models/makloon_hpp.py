from odoo import api, fields, models, _

class MakloonHpp(models.Model):
    _name = 'makloon.hpp'

    name = fields.Char("Description", related='jenis_bahan.name')
    jenis_bahan = fields.Many2one('product.product', 'Jenis Bahan')
    nama_bahan = fields.Many2one('product.product', 'Nama Bahan')
    jenis_benang = fields.Many2one('product.product', 'Jenis Benang')
    satuan = fields.Many2one('uom.uom', 'Satuan Benang')
    konvers_kg = fields.Float('Konvers Kg')
    konvers_hpp = fields.Float('Konvers Hpp')
    persentase = fields.Float('Persentase')
    setting = fields.Many2one('makloon.setting', 'Setting')
    gramasi = fields.Many2one('makloon.gramasi', 'Gramasi')
    corak = fields.Many2one('makloon.corak', 'Corak')
    daftar_harga = fields.Many2one('product.product', 'Daftar Harga')
    warna = fields.Many2one('makloon.warna', 'Warna')
    resep_warna = fields.Many2one('makloon.resep.warna', 'Resep Warna')
    category_warna = fields.Many2one('makloon.category.warna', 'Category Warna')
    makloon_celup = fields.Many2one('res.partner', 'Makloon Celup')
    makloon_rajut = fields.Many2one('res.partner', 'Makloon Rajut')

    @api.onchange('satuan')
    def onchange_satuan(self):
        for rec in self:
            if rec.satuan:
                if rec.satuan.name.lower() == 'kg':
                    rec.konvers_kg = 1
                    rec.konvers_hpp = 0.96
                elif rec.satuan.name.lower() in ('bal','bale'):
                    rec.konvers_kg = 181.44
                    rec.konvers_hpp = 176