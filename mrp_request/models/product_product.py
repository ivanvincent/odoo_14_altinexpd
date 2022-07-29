from odoo import models, fields, api, _
from odoo.exceptions import UserError




class SatuanProduksi(models.Model):
    _name = 'satuan.produksi'

    name        = fields.Char(string='Satuan Produksi')
    description = fields.Text(string='Description')
    
    
class Product(models.Model):
    _inherit = 'product.product'
    
    
    satuan_id   = fields.Many2one('satuan.produksi', string='Satuan Produksi')
    konversi_butir  = fields.Float(string='Butir')
    konversi_bungkus  = fields.Float(string='Bungkus')