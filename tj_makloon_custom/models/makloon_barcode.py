# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, Warning
from datetime import datetime

class MakloonBarcode(models.Model):
    _name = 'makloon.barcode'

    name = fields.Char('Description', )
    source_document = fields.Many2one('stock.picking', 'Source document')
    source_po = fields.Many2one('purchase.order', 'PO')
    source_sj = fields.Char('NO SJ')
    no_sj = fields.Char('NO SJ')
    order_line = fields.One2many('makloon.barcode.line', 'order_id', string='Makloon Operation Lines', copy=True,
                                 track_visibility='onchange',)

    # @api.multi
    def ProductAge(self):
        cr = self.env.cr
        cr.execute("update makloon_barcode_line SET product_age = current_date - product_date , product_saldo = product_bruto-product_sold")

class MakloonBarcodeLine(models.Model):
    _name = 'makloon.barcode.line'

    order_id = fields.Many2one('makloon.barcode', string='Makloon Barcode', required=False, ondelete='cascade',
                               index=True, copy=False)
    source_document = fields.Many2one('stock.picking', 'Source document')
    source_po = fields.Many2one('purchase.order', 'PO')
    source_sj = fields.Char('NO SJ')
    product_lot = fields.Char('Product Lot')
    name = fields.Char('Barcode', copy=False)
    product_kode = fields.Char('Kode', )
    warehouse_id = fields.Many2one('stock.warehouse', string= 'Warehouse' , default=1)
    product_id = fields.Many2one('product.product', 'Product')
    product_date = fields.Date('Date', )
    product_age = fields.Integer('Age', )
    product_bruto = fields.Float('Bruto')
    product_netto = fields.Float('Netto')
    product_sold = fields.Float('Sold')
    product_residue = fields.Float('Residue')
    product_saldo = fields.Float('Saldo Akhir')
    product_uom_id = fields.Many2one('uom.uom', 'Uom')
    product_merk_id = fields.Many2one('makloon.merk', 'Merk')
    product_setting_id = fields.Many2one('makloon.setting', 'Setting')
    product_gramasi_id = fields.Many2one('makloon.gramasi', 'Gramasi')
    product_corak_id = fields.Many2one('makloon.corak', 'Corak')
    product_warna_id = fields.Many2one('makloon.warna', 'Warna')
    product_resep_warna_id = fields.Many2one('makloon.resep.warna', 'Resep Warna')
    product_category_warna_id = fields.Many2one('makloon.category.warna', 'Category Warna')
    product_lot_id = fields.Many2one('makloon.lot', 'Lot No')
    state = fields.Selection([('available', 'Available'),('broken', 'Broken'), ('sold', 'Sold'),('eceran', 'Eceran'), ],
                             string="Status", default='available')
    available_for_pos = fields.Boolean(string="Can Be POS", default=True,)
    no_urut = fields.Char('NO Urut')

    # @api.multi
    def ProductAge(self):
        cr = self.env.cr
        cr.execute("update makloon_barcode_line SET product_age = current_date - product_date , product_saldo = product_bruto-product_sold")

    @api.model
    def create(self, vals):
        if 'name' not in vals :
            vals['name'] = self.env['ir.sequence'].next_by_code('makloon.barcode.line')
        elif not vals.get('name', False):
            vals['name'] = self.env['ir.sequence'].next_by_code('makloon.barcode.line')
        return super(MakloonBarcodeLine, self).create(vals)

    def update_saldo(self, barcode, qty):
        if not barcode or not qty :
            return False
        barcode_id = self.search([
            ('name','=',barcode)
        ], limit=1)
        if barcode_id :
            new_sold = barcode_id.product_sold - qty
            new_saldo = barcode_id.product_bruto - new_sold
            barcode_id.write({
                'product_sold': new_sold,
                'product_saldo': new_saldo,
            })

    @api.onchange('product_bruto')
    def bruto_change(self):
        if self.product_bruto :
            self.product_saldo = self.product_bruto

class StockPicking(models.Model):
    _inherit = 'stock.picking'    

    # @api.multi
    def action_generate(self):
        # stock_pack_operation_obj = self.env['stock.pack.operation']
        self.ensure_one()
        makloon_barcode_obj = self.env['makloon.barcode']
        obj = makloon_barcode_obj.search([('source_document', '=', self.id)])
        if obj :
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'makloon.barcode',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': obj.id,
                'views': [(False, 'form')],
                'target': 'current',
            }
        else :
            data = {
                'source_document': self.id,
                'source_po': self.no_po.id,
                'source_sj': self.no_sj,
            }
            # print 'data=>', data
            result = makloon_barcode_obj.create(data)

        makloon_barcode_line_obj = self.env['makloon.barcode.line']
        res = []
        if self.pack_operation_product_ids:
            for rec in self.pack_operation_product_ids:
                # # print 'int(rec.roll)=>',int(rec.roll)
                # obj_line = makloon_barcode_line_obj.search([('source_document','=',rec.picking_id.id),
                #                                   ('product_id','=',rec.product_id.id)])
                # if len(obj_line) == int(rec.roll):
                #     raise ValidationError(_("Barcode %s available!!!")%(rec.picking_id.name))
                # qty_done = 0
                if not rec.roll :
                    raise Warning("Silahkan input roll.")
                for x in range(int(rec.roll)):
                    qty = 25
                    qty2 = 0
                    data = {
                            'order_id': result.id,
                            'source_document': rec.picking_id.id,
                            'product_id': rec.product_id.id,
                            'product_date': fields.datetime.now(),
                            'warehouse_id': self.warehouse_id.id,
                            'product_bruto': float(qty),
                            'product_netto': float(qty2),
                            'product_saldo': float(qty),
                            'product_sold': float(qty2),
                            'product_residue': float(qty2),
                            'product_uom_id': rec.product_uom_id.id,
                            'product_merk_id': rec.product_merk_id.id,
                            'product_setting_id': rec.product_setting_id.id,
                            'product_gramasi_id': rec.product_gramasi_id.id,
                            'product_corak_id': rec.product_corak_id.id,
                            'product_warna_id': rec.product_warna_id.id,
                            'product_resep_warna_id': rec.product_resep_warna_id.id,
                            'product_category_warna_id': rec.product_category_warna_id.id,
                        }
                    # # print 'data=>',data, 'ke=>',x
                    request = makloon_barcode_line_obj.create(data)
                    res.append(request.id)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'makloon.barcode',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': result.id,
                'views': [(False, 'form')],
                'target': 'current',
            }

    # @api.multi
    def action_calculate(self):
        for me_id in self :
            for pack in me_id.pack_operation_product_ids :
                picking_list_ids = self.env['makloon.picking.list'].search([
                    ('picking_id','=',me_id.id),
                    ('product_id', '=', pack.product_id.id),
                ])
                qty_kg = 0
                for picking_list_id in picking_list_ids : #harusnya ini cuma ada satu
                    qty_kg += sum([picklist_line.qty_kg for picklist_line in picking_list_id.picking_list])
                if qty_kg and qty_kg != pack.qty_done :
                    pack.write({'qty_done':qty_kg})

    # @api.multi
    def action_confirm(self):
        # self.action_calculate()
        return super(StockPicking, self).action_confirm()

    # # @api.multi
    # def action_view_barcode(self):
    #     action = self.env.ref('makloon.barcode').read()[0]
    #
    #     po_id = self.mapped('source_document')
    #     # print po_id
    #     if len(po_id) > 1:
    #         action['domain'] = [('id', 'in', po_id.ids)]
    #     elif po_id:
    #         action['views'] = [(self.env.ref('tj_makloon_custom_makloon_barcode_form').id, 'form')]
    #         action['res_id'] = po_id.id
    #     return action

    @api.model
    def _prepare_values_extra_move(self, op, product, remaining_qty):
        res = super(StockPicking, self)._prepare_values_extra_move(op, product, remaining_qty)
        other_move = self.env['stock.move'].search([
            ('product_id','=',product.id),
            ('picking_id','=',op.picking_id.id)
        ], limit=1)
        if other_move :
            res.update({
                'product_merk_id': other_move.product_merk_id.id,
                'product_setting_id': other_move.product_setting_id.id,
                'product_gramasi_id': other_move.product_gramasi_id.id,
                'product_corak_id': other_move.product_corak_id.id,
                'product_warna_id': other_move.product_warna_id.id,
                'product_resep_warna_id': other_move.product_resep_warna_id.id,
                'product_category_warna_id': other_move.product_category_warna_id.id,
            })
        return res

class StockPackOperation(models.Model):
    _inherit = 'stock.move'

    # barcode_id = fields.Many2one('makloon.barcode', 'Barcode Generate')
    roll = fields.Float('Roll', )
    product_merk_id = fields.Many2one('makloon.merk', 'Merk')
    product_setting_id = fields.Many2one('makloon.setting', 'Setting')
    product_gramasi_id = fields.Many2one('makloon.gramasi', 'Gramasi')
    product_corak_id = fields.Many2one('makloon.corak', 'Corak')
    product_warna_id = fields.Many2one('makloon.warna', 'Warna')
    product_resep_warna_id = fields.Many2one('makloon.resep.warna', 'Resep Warna')
    product_category_warna_id = fields.Many2one('makloon.category.warna', 'Category Warna')

class StockMove(models.Model):
    _inherit = 'stock.move'

    product_merk_id = fields.Many2one('makloon.merk', 'Merk')
    product_setting_id = fields.Many2one('makloon.setting', 'Setting')
    product_gramasi_id = fields.Many2one('makloon.gramasi', 'Gramasi')
    product_corak_id = fields.Many2one('makloon.corak', 'Corak')
    product_warna_id = fields.Many2one('makloon.warna', 'Warna')
    product_resep_warna_id = fields.Many2one('makloon.resep.warna', 'Resep Warna')
    product_category_warna_id = fields.Many2one('makloon.category.warna', 'Category Warna')

class StockMove(models.Model):
    _inherit = 'sale.order.line'

    product_merk_id = fields.Many2one('makloon.merk', 'Merk')
    product_setting_id = fields.Many2one('makloon.setting', 'Setting')
    product_gramasi_id = fields.Many2one('makloon.gramasi', 'Gramasi')
    product_corak_id = fields.Many2one('makloon.corak', 'Corak')
    product_warna_id = fields.Many2one('makloon.warna', 'Warna')
    product_resep_warna_id = fields.Many2one('makloon.resep.warna', 'Resep Warna')
    product_category_warna_id = fields.Many2one('makloon.category.warna', 'Category Warna')      