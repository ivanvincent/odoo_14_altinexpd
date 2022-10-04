from odoo import api, fields, models, _
from odoo.exceptions import Warning

class PickingList(models.Model):
    _name = 'makloon.picking.list'

    name = fields.Char('Name',related='picking_id.name', )
    picking_id = fields.Many2one('stock.picking', 'Stock Picking',)
    product_id = fields.Many2one('product.product', 'Product')
    picking_list = fields.One2many('makloon.picking.list.line', 'order_id', string='Picking List', copy=True,
                                 track_visibility='onchange',)
    state = fields.Selection(string='State', related='picking_id.state')

    # @api.multi
    def action_crud_picking(self):
        self.ensure_one()
        self.write({'picking_id': self.picking_id.id,
                   'product_id': self.product_id.id,})
        if self.picking_list:
            kg = 0
            bale = 0
            roll = 0
            for rec in self.picking_list:
                kg += rec.qty_kg
                bale += rec.qty_bale
                roll += rec.qty_roll

        # self.ensure_one()
        # picking = self.env['makloon.picking.list'].search(
        #     [('id', '=', self.id)])
        # picking.write({
        #     'picking_id': self.picking_id.id,
        #     'product_id': self.product_id.id,
        #     'name': self.name,
        #     'picking_list': self.picking_list.ids,
        # })
        # # picking.write(data)

        # print 'picking=>', data
        # picking_line =  self.env['makloon.picking.list.line'].search(
        #     [('id', 'in', self.picking_list.ids)])
        # if len(picking_line)>0:
        #     for rec in picking_line:
        #         data = {
        #             'qty_kg': rec.qty_kg,
        #             'qty_bale': rec.qty_bale,
        #             'qty_roll': rec.qty_roll,
        #             'packing': rec.packing,
        #             'lot': rec.lot,
        #         }
        #         print 'picking_line=>', data
        #         picking_line.write(data)


class PickingListline(models.Model):
    _name = 'makloon.picking.list.line'

    order_id = fields.Many2one('makloon.picking.list', string='Reference List', required=True, ondelete='cascade',
                               index=True, copy=False)
    name = fields.Char('Name', )
    no_urut = fields.Char('No', )
    qty_kg = fields.Float('KG', )
    qty_bale = fields.Float('Bale', )
    qty_roll = fields.Float('Roll', )
    packing = fields.Char('Packing', )
    lot = fields.Char('Lot', )
    barcode = fields.Char('Barcode')
    warna_id = fields.Many2one('makloon.warna', string='Warna', ondelete='restrict')

    @api.onchange('barcode')
    def barcode_change(self):
        if self.barcode :
            self.barcode = self.barcode.upper()
            self.barcode = self.barcode.replace(' ','')
            barcode_id = self.env['makloon.barcode.line'].search([
                ('name','=',self.barcode)
            ], limit=1)
            if not barcode_id :
                raise Warning("Barcode tidak ditemukan.")
            self.warna_id = barcode_id.product_warna_id.id
            self.qty_kg = barcode_id.product_bruto-barcode_id.product_sold
            #self.qty_kg = barcode_id.product_netto-barcode_id.product_sold
