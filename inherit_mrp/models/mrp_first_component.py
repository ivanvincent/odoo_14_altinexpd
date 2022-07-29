from odoo import models, fields, api

class MrpFirstComponent(models.Model):
    _name = 'mrp.first.component'

    name = fields.Char(string='Label dari Field')
    product_id = fields.Many2one('product.product', string='Component', required=True, )
    quantity = fields.Float(string='Quantity', digits=(12,5), required=True, )
    quantity_finish = fields.Float(string='Quantity Finish', digits=(12,5), required=False, )
    product_uom_id = fields.Many2one('uom.uom', string='Uom', required=True, )
    bom_id = fields.Many2one('mrp.bom', string='Bom')
    location_id = fields.Many2one('stock.location', string='Location')
    kategori_obat = fields.Selection([("aux","Auxilarie"),("dye","Dye stuff")], string='Kategori Obat')
    kategori_id = fields.Many2one('mrp.workcenter', string='Kategori')
    type = fields.Selection([("opc","Opc"),("finish","Finish")], string='Type')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        print('_onchange_product_id')
        for rec in self:
            if rec.product_id.id:
                rec.product_uom_id = rec.product_id.uom_id.id
    