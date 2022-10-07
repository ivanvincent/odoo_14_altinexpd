from odoo import fields, api, models, _
from odoo.exceptions import Warning
from datetime import datetime

class AngkringDuplicateLot(models.TransientModel):
    _name = "angkring.duplicate.lot"

    name = fields.Char()
    new_qty = fields.Float(string='New Qty')

    # @api.multi
    def create_picking(self, lot_id):
        obj_picking = self.env['stock.picking']
        # loss_loc_id = self.env.ref('stock.location_inventory')
        loss_loc_id = self.env['stock.location'].search([('name','=', 'Inventory adjustment')])        
        location_id = lot_id.quant_ids.mapped('location_id').filtered(lambda loc: loc.usage == 'internal')
        # location_id = self.env['stock.location'].browse(8)
        # location_dest_id = lot_id.quant_ids.mapped('location_dest_id').filtered(lambda loc: loc.usage == 'internal')
        if not lot_id.warehouse_id :
            raise Warning("Silahkan input warehouse terlebih dahulu.")
        ptype_out_id = lot_id.warehouse_id.out_type_id
        ptype_in_id = lot_id.warehouse_id.in_type_id
        if len(location_id) > 1 :
            raise Warning("Serial number harus berada di satu lokasi yang bertipe internal")
        picking_out_id = obj_picking.create({
            'picking_type_id': ptype_out_id.id,
            'date': datetime.now(),
            'origin': lot_id.name,
            'location_id': location_id.id,
            'location_dest_id': loss_loc_id.id,
            'move_lines': [(0,0,{
                'name': lot_id.product_id.name_get()[0][1],
                'product_id': lot_id.product_id.id,
                'product_uom_qty': self.new_qty,
                'product_uom': lot_id.product_id.uom_id.id,
                'location_id': location_id.id,
                'location_dest_id': loss_loc_id.id,
                # 'restrict_lot_id': lot_id.id,
            })]
        })
        picking_out_id.action_confirm()
        picking_out_id.action_assign()
        if picking_out_id.state != 'assigned' :
            picking_out_id.force_assign()
            raise Warning("Stok tidak tersedia di lokasi %s"%picking_out_id.location_id.name_get()[0][1])
        for pack in picking_out_id.move_ids_without_package:
            pack.quantity_done = self.new_qty
            for pack_lot in pack.move_line_nosuggest_ids:
                pack_lot.write({
                    'lot_id': lot_id.id
                })
                pack_lot.qty_done = self.new_qty
        picking_out_id.button_validate()
        # picking_out_id.do_new_transfer()

        picking_in_id = obj_picking.create({
            'picking_type_id': ptype_in_id.id,
            'date': datetime.now(),
            'origin': lot_id.name,
            'location_id': loss_loc_id.id,
            'location_dest_id': location_id.id,
            'move_lines': [(0,0,{
                'name': lot_id.product_id.name_get()[0][1],
                'product_id': lot_id.product_id.id,
                'product_uom_qty': self.new_qty,
                'product_uom': lot_id.product_id.uom_id.id,
                'location_id': loss_loc_id.id,
                'location_dest_id': location_id.id,
            })]
        })
        picking_in_id.action_confirm()
        picking_in_id.action_assign()
        # picking_in_id.button_validate()
        new_lot_id = False
        if picking_in_id.state != 'assigned' :
            # picking_in_id.force_assign()
            raise Warning("Stok tidak tersedia di lokasi %s"%picking_in_id.location_id.name_get()[0][1])
        for pack in picking_in_id.move_ids_without_package:
            if pack.product_id.tracking != 'lot' :
                raise Warning("Tracking product %s harus diset By Lots."%pack.product_id.name_get()[0][1])
            # pack.write({
            #     'roll': 1,
            #     'quantity_done': self.new_qty,
            # })
            new_lot_id = self.env['stock.production.lot'].create({
                        # 'operation_id': pack.id,
                        'name': self.env['ir.sequence'].next_by_code('stock.production.lot') or ('/'),
                        'product_qty': self.new_qty,
                        'product_id': pack.product_id.id,
                        'company_id': self.env.user.company_id.id,
                        'lot_parent_name': lot_id.name,
                    })
            pack.write({
                'move_line_nosuggest_ids': [(0, 0, {
                    'lot_id': new_lot_id.id,
                    'qty_done': self.new_qty,
                    'product_uom_id': pack.product_id.uom_id.id,
                    'location_id': pack.location_id.id,
                    'location_dest_id': pack.location_dest_id.id,
                    'product_id': new_lot_id.product_id.id,
                    'picking_id': picking_in_id.id,
                })]
            })
            # if not pack.move_line_nosuggest_ids:
            #     for x in range(int(pack.roll)):
                    # new_lot_id = self.env['stock.production.lot'].create({
                    #     'operation_id': pack.id,
                    #     'lot_name': self.env['ir.sequence'].next_by_code('stock.production.lot') or ('/'),
                    #     'qty': self.new_qty,
                    # })
        # picking_in_id.do_new_transfer()
        picking_in_id.button_validate()
        return new_lot_id or False

    # @api.multi
    def action_generate(self):
        lot_id = self.env['stock.production.lot'].browse(self._context['active_id'])
        # if self.new_qty >= lot_id.product_saldo :
        #     raise Warning("New qty harus lebih kecil dari saldo akhir.")
        if not self.new_qty :
            raise Warning("New qty tidak boleh nol.")
        new_lot_id = self.create_picking(lot_id)
        if not new_lot_id :
            return False
        new_lot_id.write({
            'ref': lot_id.ref,
            'picking_in_id': lot_id.picking_in_id.id,
            'purchase_id': lot_id.purchase_id.id,
            # 'warehouse_id': lot_id.warehouse_id.id,
            'product_date': lot_id.product_date,
            'product_age': lot_id.product_age,
            'product_merk_id': lot_id.product_merk_id.id,
            'product_setting_id': lot_id.product_setting_id.id,
            'product_gramasi_id': lot_id.product_gramasi_id.id,
            'product_corak_id': lot_id.product_corak_id.id,
            'product_warna_id': lot_id.product_warna_id.id,
            'product_resep_warna_id': lot_id.product_resep_warna_id.id,
            'product_category_warna_id': lot_id.product_category_warna_id.id,
        })
        view_id = self.env.ref('stock.view_production_lot_form').id
        context = self._context.copy()
        return {
            'name':'New Serial Number',
            'view_type': 'form',
            'view_mode': 'tree',
            'views' : [(view_id,'form')],
            'res_model': 'stock.production.lot',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': new_lot_id.id,
            'target': 'current',
            'context': context,
        }
