from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    standard_price = fields.Float('Std Price', compute='_compute_bom_cost')
    total_price = fields.Float('Total Raw Price', compute='_compute_bom_cost')
    kategori_id = fields.Many2one('mrp.workcenter', string='Kategori')
    kategori_obat = fields.Selection([("aux","Auxilarie"),("dye","Dye stuff")], string='Kategori Obat')
    lot_id = fields.Many2one('stock.production.lot', string='Lot')
    type = fields.Selection([("opc","Opc"),("finish","Finish")], string='Type')
    
    def _compute_bom_cost(self):
        for bom_line in self:
            bom_line.standard_price = bom_line.product_id.standard_price
            bom_line.total_price = bom_line.standard_price * bom_line.product_qty

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        for rec in self:
            rec.product_id = rec.lot_id.product_id.id
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        product_id = self.product_id.id
        if product_id:
            res = {}
            res['domain'] = {'lot_id': [('product_id', '=', self.product_id.id)]}
            return res