# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
import odoo.addons.decimal_precision as dp

class MakloonOrder(models.Model):
    _inherit = 'makloon.order'

    @api.depends('production_pick_ids','result_pick_ids')
    # @api.multi
    def _get_makloon_progress(self):
        for me_id in self :
            progress_in = 0
            progress_out = 0
            pickings_in = me_id.mapped('result_pick_ids')
            pickings_out = me_id.mapped('production_pick_ids')
            move_in_done = 0
            move_in_prog = 0
            move_out_done = 0
            move_out_prog = 0
            for picking_in in pickings_in :
                for move in picking_in.move_lines :
                    if move.state == 'cancel':
                        continue
                    elif move.state == 'done':
                        move_in_done += move.product_uom_qty
                    else :
                        move_in_prog += move.product_uom_qty
            for picking_out in pickings_out :
                for move in picking_out.move_lines :
                    if move.state == 'cancel':
                        continue
                    elif move.state == 'done':
                        move_out_done += move.product_uom_qty
                    else :
                        move_out_prog += move.product_uom_qty
            if move_in_done or move_in_prog :
                progress_in = 100/(move_in_done + move_in_prog)*move_in_done
            if move_out_done or move_out_prog :
                progress_out = 100 / (move_out_done + move_out_prog) * move_out_done
            me_id.result_progress = progress_in
            me_id.material_progress = progress_out

    barcode_ids = fields.One2many('stock.picking', 'makloon_order_id', "Barcode List", domain=[('picking_type_id.code','=','incoming')])
    stage_name = fields.Char(
        string='Stage Name')
    material_progress = fields.Float('Material Progress', compute="_get_makloon_progress", copy=False)
    result_progress = fields.Float('Result Progress', compute="_get_makloon_progress", copy=False)
    order_body_kg = fields.Float(string='Body Roll', default=25)
    order_kerah_kg = fields.Float(string='Kerah Roll', )
    order_rib_kg = fields.Float(string='Rib Roll', )
    order_manset_kg = fields.Float(string='Manset Roll', )
    order_body_persen = fields.Float(string='Body Persen %', )
    order_kerah_persen = fields.Float(string='Kerah Persen %', )
    order_rib_persen = fields.Float(string='Rib Persen %', )
    order_manset_persen = fields.Float(string='Manset Persen %', )

    source_po = fields.Char(string='Source PO', )

    # @api.model
    # def create(self, vals):
    #     res = super(MakloonOrder, self).create(vals)
    #     print vals['order_body_persen'], vals['order_kerah_persen'], vals['order_rib_persen'], vals['order_manset_persen']
    #     ptotal = vals['order_body_persen']+vals['order_kerah_persen']+vals['order_rib_persen']+vals['order_manset_persen']
    #     if (ptotal < 100) or (ptotal == 0):
    #         raise UserError(_('Material Harus 100%'))
    #     elif (ptotal > 100):
    #         raise UserError(_('Material Lebih Dari 100%'))
    #     return res
    #
    # # @api.multi
    # def write(self, vals):
    #     res = super(MakloonOrder, self).write(vals)
    #     for rec in self:
    #         ptotal = rec.order_body_persen + rec.order_kerah_persen + rec.order_rib_persen + rec.order_manset_persen
    #         if (ptotal < 100):
    #             raise UserError(_('Material Harus 100%'))
    #         elif (ptotal > 100):
    #             raise UserError(_('Material Lebih Dari 100%'))
    #     return res
    #
    # @api.onchange('order_id','material_ids','result_ids',
    #               'order_body_kg','order_kerah_kg','order_rib_kg','order_manset_kg',
    #               'order_body_persen','order_kerah_persen','order_rib_persen','order_manset_persen')
    # def onchange_order(self):
    #     for rec in self:
    #         mat_total = 0
    #         pbody = 0
    #         pkerah = 0
    #         prib = 0
    #         pmanset = 0
    #
    #         for mat in rec.material_ids:
    #             if mat:
    #                 mat_total = mat.product_kg
    #                 print "mat_total=>",mat_total
    #         for res in rec.result_ids:
    #             if rec.order_body_persen and rec.order_body_kg and rec.order_body_persen<>0 and rec.order_body_kg<>0:
    #                 pbody = (mat_total * (rec.order_body_persen/100))/rec.order_body_kg
    #             if rec.order_kerah_persen and rec.order_kerah_kg and rec.order_kerah_persen <> 0 and rec.order_kerah_kg <> 0:
    #                 pkerah = (mat_total * (rec.order_kerah_persen / 100)) / rec.order_kerah_kg
    #             if rec.order_rib_persen and rec.order_rib_kg and rec.order_rib_persen <> 0 and rec.order_rib_kg <> 0:
    #                 prib = (mat_total * (rec.order_rib_persen / 100)) / rec.order_rib_kg
    #             if rec.order_manset_persen and rec.order_manset_kg and rec.order_manset_persen <> 0 and rec.order_manset_kg <> 0:
    #                 pmanset = (mat_total * (rec.order_manset_persen / 100)) / rec.order_manset_kg
    #                 # print 'persen=>',(mat_total * (rec.order_body_persen/100))
    #                 # print 'body=>', rec.order_body_kg
    #                 # print "if hasil pbody=>",float(int(pbody))
    #             res.product_body = int(pbody)
    #             res.product_kerah = int(pkerah)
    #             res.product_rib = int(prib)
    #             res.product_manset = int(pmanset)
    #             # print 'persen=>', (mat_total * (rec.order_body_persen / 100))
    #             # print 'body=>', rec.order_body_kg
    #             # print "pbody=>",pbody,"bulat=>",int(pbody)

        # if rec.order_id.order_body_persen and rec.order_id.order_body_kg:
            #     pbody = (mat_total * (rec.order_id.order_body_persen/100))/rec.order_id.order_body_kg
            # rec.product_body = pbody
            # print "pbody=>", pbody
            # if rec.order_id.order_kerah_persen and rec.order_id.order_kerah_kg:
            #     pkerah = (mat_total * (rec.order_id.order_kerah_persen/100))/rec.order_id.order_kerah_kg
            # rec.product_kerah = pkerah
            # print "pkerah=>", pkerah
            # if rec.order_id.order_rib_persen and rec.order_id.order_rib_kg:
            #     prib = (mat_total * (rec.order_id.order_rib_persen/100))/rec.order_id.order_rib_kg
            # rec.product_rib = prib
            # print "prib=>", prib
            # if rec.order_id.order_manset_persen and rec.order_id.order_manset_kg:
            #     pmanset = (mat_total * (rec.order_id.order_manset_persen/100))/rec.order_id.order_manset_kg
            # rec.product_manset = pmanset
            # print "pmanset=>", pmanset


    # @api.depends('result_pick_ids')
    # def _get_makloon_progress(self):
    #     sp_obj = self.env['stock.picking'].search([('origin', '=', self.name)])
    #     for spobj in sp_obj:
    #         spo_obj = self.env['stock.pack.operation'].search([('picking_id', '=', spobj.id)])
    #         for rec in self:
    #             rec.progress = 0.0
    #             print spo_obj.ids
    #             if spo_obj.ids:
    #                 total = 0.0
    #                 for record in spo_obj.ids:
    #                     if total != 0.0:
    #                         total += (record.qty_done / record.product_qty) * 100
    #                 rec.progress = total
    #                 print rec.progress

    @api.onchange('result_ids', 'stage_id')
    def onchange_name(self):
        if self.stage_id :
            self.stage_name = self.stage_id.operation_id.name

    # # @api.multi
    # def _create_picking_in(self):
    #     StockPicking = self.env['stock.picking']
    #     for order in self:
    #         if order.type == "out":
    #             if any([ptype in ['product', 'consu'] for ptype in order.result_ids.mapped('product_id.type')]):
    #                 # pickings = StockPicking.search([('makloon_order_id', '=', order.id)])
    #                 # if not pickings:
    #                 res = order._prepare_picking_in()
    #                 picking = StockPicking.create(res)
    #                 # else:
    #                 #     picking = pickings[0]
    #                 moves = order.result_ids._create_stock_moves_in(picking)
    #                 moves = moves.filtered(lambda x: x.state not in ('done', 'cancel')).action_confirm()
    #                 moves.force_assign()
    #                 print moves
    #                 for line in moves:
    #                     sp = self.env['stock.pack.operation'].search([('picking_id', '=', picking.id),
    #                                                                   ('product_id', '=', line.product_id.id)])
    #                     # print 'sp=>', sp,'picking=>',picking,'pickingid=>',picking.id
    #                     if sp:
    #                         for line2 in sp:
    #                             product_merk_id = line.product_merk_id.id
    #                             product_setting_id = line.product_setting_id.id
    #                             product_gramasi_id = line.product_gramasi_id.id
    #                             product_corak_id = line.product_corak_id.id
    #                             product_warna_id = line.product_warna_id.id
    #                             product_resep_warna_id = line.product_resep_warna_id.id
    #                             product_category_warna_id = line.product_category_warna_id.id

    #                             line2.product_merk_id = product_merk_id
    #                             line2.product_setting_id = product_setting_id
    #                             line2.product_gramasi_id = product_gramasi_id
    #                             line2.product_corak_id = product_corak_id
    #                             line2.product_warna_id = product_warna_id
    #                             line2.product_resep_warna_id = product_resep_warna_id
    #                             line2.product_category_warna_id = product_category_warna_id
    #                             # print 'looping sp =>', product_merk_id, product_setting_id, product_gramasi_id, product_corak_id, product_warna_id, product_resep_warna_id, product_category_warna_id
    #                 picking.message_post_with_view('mail.message_origin_link',
    #                                                values={'self': picking, 'origin': order},
    #                                                subtype_id=self.env.ref('mail.mt_note').id)

    # @api.multi
    def _create_po(self):
        po_obj = self.env['purchase.order']
        po_line_obj = self.env['purchase.order.line']
        for me in self:
            type_id = me.stage_id.operation_id.name.lower()
            if me.result_ids:
                po_data = {
                    'origin': me.name,
                    'partner_id': me.partner_id.id,
                    'makloon_id': me.id,
                    'type_id': type_id
                    # 'order_line': []
                }
                po_id = po_obj.create(po_data)
                for rs in me.result_ids:
                    line = {
                        'name': rs.product_id.name,
                        'order_id': po_id.id,
                        'product_id': rs.service_product_id.id,
                        'price_unit': rs.service_product_id.standard_price,
                        'product_uom': rs.service_product_id.uom_id.id,
                        'product_qty': rs.product_uom_qty,
                        'date_planned': me.date_order,
                        'product_merk_id': rs.product_merk_id.id,
                        'product_setting_id': rs.product_setting_id.id,
                        'product_gramasi_id': rs.product_gramasi_id.id,
                        'product_corak_id': rs.product_corak_id.id,
                        'product_warna_id': rs.product_warna_id.id,
                        'product_resep_warna_id': rs.product_resep_warna_id.id,
                        'product_category_warna_id': rs.product_category_warna_id.id,
                        'roll_kg_id': rs.roll_kg_id.id,                        
                    }
                    po_line_obj.create(line)

                return True

        return False

class MakloonOrderMaterial(models.Model):
    _inherit = 'makloon.order.material'

    no_sj = fields.Many2one('stock.picking', 'No SJ')
    no_po = fields.Many2one('purchase.order', 'No PO')
    product_kg = fields.Float(string='KG', )
    product_body = fields.Float(string='Body(%)', )
    product_kerah = fields.Float(string='Kerah(%)', )
    product_rib = fields.Float(string='Rib(%)', )
    product_manset = fields.Float(string='Manset(%)', )

    # @api.onchange('order_id', 'order_id.stage_id', 'product_id', 'product_uom_qty', 'product_uom')
    # @api.depends('order_id', 'order_id.stage_id', 'product_id', 'product_uom_qty', 'product_uom')
    # def onchange_name_and_kg(self):
    #     # categ_obj = self.env['makloon.operation.line']
    #     for rec in self:

    #         if rec.product_uom_qty and rec.product_uom:
    #             if (rec.product_uom.name.lower() in ('bale','ball')):
    #                 rec.product_kg = rec.product_uom_qty * 181.44
    #             else:
    #                 rec.product_kg = rec.product_uom_qty

    #         if rec.order_id:
    #             rec.operation_name = rec.order_id.stage_id.operation_id.name
    #         if rec.order_id.stage_id.operation_id:
    #             ids = []
    #             for child_id in rec.order_id.stage_id.operation_id.order_line:
    #                 if child_id.product_material_id:
    #                     ids.append(child_id.product_material_id.id)
    #                     # print child_id
    #                     # print ids
    #             domain = {'product_id': [('categ_id', 'in', ids)]}
    #         else:
    #             domain = {'product_id': [('categ_id', 'in', [])]}
    #         # print domain
    #         return {'domain': domain}


class MakloonOrderResult(models.Model):
    _inherit = 'makloon.order.result'

    product_group_category = fields.Many2one('product.template.group.category', 'Product Category')
    product_merk_id = fields.Many2one('makloon.merk', 'Merk')
    product_setting_id = fields.Many2one('makloon.setting', 'Setting Jadi')
    product_gramasi_id = fields.Many2one('makloon.gramasi', 'Gramasi Matang')
    product_corak_id = fields.Many2one('makloon.corak', 'Corak')
    product_resep_warna_id = fields.Many2one('makloon.resep.warna', 'Resep Warna')
    product_warna_id = fields.Many2one('makloon.warna', 'Warna' , required=True)
    product_category_warna_id = fields.Many2one('makloon.category.warna', 'Category Warna')
    product_roll = fields.Integer(string='Roll', )
    roll_kg_id = fields.Many2one('makloon.roll', '@ Kg', required=True)
    # product_body = fields.Integer(string='Body Roll', )
    # product_kerah = fields.Integer(string='Kerah Roll', )
    # product_rib = fields.Integer(string='Rib Roll', )
    # product_manset = fields.Integer(string='Manset Roll', )
    price_unit = fields.Float(string='Harga Rp', required=True, digits=dp.get_precision('Product Price'))
    price_subtotal = fields.Float(string='Subtotal', store=True,
                                  digits=dp.get_precision('Product Subtotal'))
    # progress = fields.Float('Order Progress', compute="_get_makloon_progress")

    operation_name = fields.Char(
        string='Operation Name',
        compute='_onchange_name',
        store=True, )

    @api.onchange('product_id')
    def onchange_product(self):
        for rec in self:
            rec.product_group_category = rec.product_id.product_group_category.id
            # print rec.product_id.product_group_category.id

    # @api.depends('result_pick_ids')
    # def _get_makloon_progress(self):
    #     # sp_obj = self.env['stock.picking'].search([('origin', '=', self.name)])
    #     for rec in self:
    #         rec.progress = 0.0
    #         if rec.result_pick_ids:
    #             total = 0.0
    #             for record in rec.result_pick_ids:
    #                 if total != 0.0:
    #                     total += (record.qty_done / record.product_qty) * 100
    #             rec.progress = total
                        # rec.progress = (total / len(rec.stage_ids)) * 100

    @api.onchange('price_unit','product_uom_qty')
    def onchange_pricesubtotal(self):
        for rec in self:
            rec.price_subtotal = rec.product_uom_qty * rec.price_unit
            # print rec.product_uom_qty , rec.price_unit

    @api.onchange('product_resep_warna_id')
    def _onchange_resepwarna(self):
        for rec in self:
            if rec.product_resep_warna_id:
                if rec.product_resep_warna_id.warna_id:
                    rec.product_warna_id = rec.product_resep_warna_id.warna_id.id
                if rec.product_resep_warna_id.category_warna_id:
                    rec.product_category_warna_id = rec.product_resep_warna_id.category_warna_id.id
                # print rec.product_resep_warna_id.warna_id, rec.product_resep_warna_id.category_warna_id

    @api.onchange('order_id', 'order_id.stage_id', 'product_id')
    @api.depends('order_id', 'order_id.stage_id', 'product_id')
    def _onchange_name(self):
        # categ_obj = self.env['makloon.operation.line']
        for rec in self:
            if rec.order_id:
                rec.operation_name = rec.order_id.stage_id.operation_id.name
            if rec.order_id.stage_id.operation_id:
                ids = []
                for child_id in rec.order_id.stage_id.operation_id.order_line:
                    if child_id.product_category_id:
                        ids.append(child_id.product_category_id.id)
                        # print child_id
                        # print ids
                domain = {'product_id': [('categ_id', 'in', ids)]}
            else:
                domain = {'product_id': [('categ_id', 'in', [])]}
            # print domain
            return {'domain': domain}

    # @api.multi
    def _create_stock_moves_in(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            if line.product_id.type not in ['product', 'consu']:
                continue
            qty = 0.0
            price_unit = line._get_stock_move_price_unit()

            # print "LOCATION IN RESULT .., ", line.order_id.production_loc.id

            template = {
                'name': line.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.product_uom.id,
                'date': line.order_id.date_order,
                # 'date_expected': line.order_id.date_order,
                'location_id': picking.location_id.id,  # line.order_id.production_loc.id,  # self.production_loc.id
                'location_dest_id': line.order_id.warehouse_id.lot_stock_id.id,
                'picking_id': picking.id,
                'partner_id': line.order_id.partner_id.id,
                # 'move_dest_id': False,
                'state': 'draft',
                'company_id': line.order_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': line.order_id.warehouse_id.in_type_id.id,
                'group_id': False,
                # 'procurement_id': False,
                'origin': line.order_id.name,
                'warehouse_id': line.order_id.warehouse_id.id,
                'product_merk_id': line.product_merk_id.id,
                'product_setting_id': line.product_setting_id.id,
                'product_gramasi_id': line.product_gramasi_id.id,
                'product_corak_id': line.product_corak_id.id,
                'product_warna_id': line.product_warna_id.id,
                'product_resep_warna_id': line.product_resep_warna_id.id,
                'product_category_warna_id': line.product_category_warna_id.id,
            }
            # print "template=>>",template
            diff_quantity = line.product_uom_qty - qty
            if float_compare(diff_quantity, 0.0, precision_rounding=line.product_uom.rounding) > 0:
                template['product_uom_qty'] = diff_quantity
                done += moves.create(template)
        # print "template=>>", template
        return done