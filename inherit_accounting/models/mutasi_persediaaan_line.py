from odoo import models, fields, api

class MutasiPersediaanLine(models.Model):
    _name = 'mutasi.persediaan.line'

    account_id = fields.Many2one('account.account', string='Account')
    account = fields.Char(string='Location')
    location_id = fields.Many2one('stock.location', string='Location')
    product_id = fields.Many2one('product.product', string='Product')
    categ_id = fields.Many2one('product.category', string="Product Category" , related='product_id.categ_id')
    lok = fields.Char(string='Lok')
    saldo_awal = fields.Float(string='Saldo Awal')
    penerimaan = fields.Float(string='Penerimaan')
    pengeluaran = fields.Float(string='Pengeluaran')
    saldo_akhir = fields.Float(string='Saldo Akhir')
    qty_start = fields.Float(string='Qty Start')
    qty_in = fields.Float(string='Qty In')
    qty_out = fields.Float(string='Qty Out')
    qty_balance = fields.Float(string='Qty Balance')
    mutasi_persediaan_id = fields.Many2one('mutasi.persediaan', 'Mutasi Persediaan')