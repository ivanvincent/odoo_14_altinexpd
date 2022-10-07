from odoo import api, fields, models, _

class MakloonHargaOutlet(models.Model):
    _name = 'makloon.harga.outlet'

    name = fields.Char("Name", )
    date = fields.Date("Date",)
    product_id = fields.Many2one('product.product', 'Product')
    product_category_id = fields.Many2one('makloon.category.warna', 'Category Warna')
    price_roll = fields.Float('Price roll',)
    set_kg = fields.Float('Set Kg', )
    price_down = fields.Float('Price down', )
    price_up = fields.Float('Price up', )
    product_gramasi_id = fields.Many2one('makloon.gramasi', 'Gramasi')
    product_lot_id = fields.Many2one('makloon.lot', 'Lot No')
    active = fields.Boolean('Active', default=True,)

class MakloonLot(models.Model):
    _name = 'makloon.lot'
    name = fields.Char("Name", )
    description = fields.Char("Description", )