from odoo import fields, api, models
from odoo.exceptions import Warning
from datetime import datetime

class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking','barcodes.barcode_events_mixin']

    list_product = fields.Char(string='Product', compute='compute_list_product')

    # @api.multi
    def action_generate_serial(self):
        no = 1
        tot_gulungan = sum(self.mapped('move_ids_without_package.roll'))
        for me_id in self :
            if me_id.state != 'assigned' or me_id.picking_type_code != 'incoming' or me_id.location_id.usage not in ('production','supplier','inventory'):
                return False
            for pack in me_id.move_ids_without_package:
                if pack.product_id.tracking != 'lot' :
                    raise Warning("Tracking product %s harus diset By Lots."%pack.product_id.name_get()[0][1])
                elif not pack.roll :
                    raise Warning("Silahkan input jumlah roll.")
                tot_qty = 0
                if not pack.move_line_nosuggest_ids:
                    data = []
                    for x in range(int(pack.roll)):
                        lot = self.env['stock.production.lot'].sudo().create({
                            # 'operation_id': pack.id,
                            'name': self.env['ir.sequence'].next_by_code('stock.production.lot') or ('/'),
                            'product_qty': 25,
                            'product_id' : pack.product_id.id,
                            'company_id' : me_id.company_id.id,
                            'gulungan_ke' : no, 
                            'total_gulungan': tot_gulungan,
                            'picking_in_id' : me_id.id
                        })
                        no += 1
                        tot_qty += 25
                        data.append((0, 0, {
                            'lot_id': lot.id,
                            'product_uom_id': pack.product_id.uom_id.id,
                            'location_id': pack.location_id.id,
                            'location_dest_id': pack.location_dest_id.id,
                            'product_id': pack.product_id.id,
                            'state': 'assigned',
                            'picking_id': self.id,
                        }))
                    pack.move_line_nosuggest_ids = data
                # pack.quantity_done = tot_qty

    def _create_lots_for_picking(self):
        Lot = self.env['stock.production.lot']
        for pack_op_lot in self.mapped('pack_operation_ids').mapped('pack_lot_ids'):
            if not pack_op_lot.lot_id:
                picking_id = pack_op_lot.operation_id.picking_id
                
                # CUSTOM CODE TO ADD PURCHASE ORDER REFERENCE
                purchase_id = False
                if picking_id and picking_id.purchase_id:
                    purchase_id = picking_id.purchase_id.id
                elif picking_id and picking_id.makloon_order_id.po_ids[:1]:
                    purchase_id = picking_id.makloon_order_id.po_ids[:1].id
                # END OF CUSTOM CODE

                lot = Lot.create({
                    'name': pack_op_lot.lot_name, 
                    'product_id': pack_op_lot.operation_id.product_id.id,
                    'picking_in_id': picking_id.id,
                    # CUSTOM CODE
                    'purchase_id': purchase_id,

                    # ORIGINAL CODE
                    # 'purchase_id': picking_id.makloon_order_id.po_ids[:1] and picking_id.makloon_order_id.po_ids[:1].id or False,
                    'product_bruto': pack_op_lot.qty,
                    'product_saldo': pack_op_lot.qty,
                    'product_merk_id': pack_op_lot.operation_id.product_merk_id.id,
                    'product_setting_id': pack_op_lot.operation_id.product_setting_id.id,
                    'product_merk_id': pack_op_lot.operation_id.product_merk_id.id,
                    'product_gramasi_id': pack_op_lot.operation_id.product_gramasi_id.id,
                    'product_corak_id': pack_op_lot.operation_id.product_corak_id.id,
                    'product_warna_id': pack_op_lot.operation_id.product_warna_id.id,
                    'product_resep_warna_id': pack_op_lot.operation_id.product_resep_warna_id.id,
                    'product_category_warna_id': pack_op_lot.operation_id.product_category_warna_id.id,
                    'no_urut': pack_op_lot.no_urut,
                    'no_lot': pack_op_lot.no_lot,
                })
                pack_op_lot.write({'lot_id': lot.id})
        # TDE FIXME: this should not be done here
        self.mapped('pack_operation_ids').mapped('pack_lot_ids').filtered(lambda op_lot: op_lot.qty == 0.0).unlink()
    create_lots_for_picking = _create_lots_for_picking
    
    def on_barcode_scanned(self, barcode):
        if self.picking_type_id.code not in ('outgoing','internal'):
            raise Warning("Scan barcode hanya untuk barang keluar atau internal transfer")
        if self.state not in ('draft','waiting','confirmed'):
            raise Warning("Scan barcode bisa dilakukan ketika status draft, waiting dan partially available.")
        if barcode in self.move_lines.mapped('restrict_lot_id').mapped('name'):
            raise Warning("Barcode sudah discan sebelumnya.")
        lot_id = self.env['stock.production.lot'].search([
            ('name','=',barcode),
            ('product_saldo','>',0)
        ], limit=1)
        if not lot_id :
            raise Warning("Barcode tidak ditemukan atau saldo akhirnya 0.")
        self.move_lines += self.env['stock.move'].new({
            'product_id': lot_id.product_id.id,
            'restrict_lot_id': lot_id.id,
            'name': lot_id.product_id.name_get()[0][1],
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'picking_type_id': self.picking_type_id.id,
            # 'date_expected': self.min_date or datetime.now(),
            'state': 'draft',
            'product_uom': lot_id.product_uom_id.id,
            'product_uom_qty': lot_id.product_saldo,
            'product_merk_id': lot_id.product_merk_id.id,
            'product_setting_id': lot_id.product_setting_id.id,
            'product_gramasi_id': lot_id.product_gramasi_id.id,
            'product_corak_id': lot_id.product_corak_id.id,
            'product_warna_id': lot_id.product_warna_id.id,
            'product_resep_warna_id': lot_id.product_resep_warna_id.id,
            'product_category_warna_id': lot_id.product_category_warna_id.id,
        })

    @api.model
    def barcode_scan(self,barcode,active_id):
        self = self.browse([active_id])
        if self:
            lot_id = self.env['stock.production.lot']\
            .search([('name','=',barcode),],limit=1)
            if not lot_id:
                return {
                    "error":True,
                    "message":"Barcode %s \nnot found !!!"%(barcode),
                    "count":len(lot_id)}
            elif self.move_line_ids_without_package and lot_id.id in [ lot.id for lot in self.move_line_ids_without_package.mapped('lot_id')]:
                return {
                    "error":True,
                    "message":"Barcode %s \nwas Added !!!"%(barcode),
                    "count":len(lot_id)
                    }
            self.move_line_ids_without_package = [(0,0,{
                    'lot_id'        : lot_id.id,
                    'product_id'    : lot_id.product_id.id,
                    'qty_done'      : lot_id.product_qty,
                    'picking_id'    : self.id,
                    'product_uom_id': lot_id.product_id.uom_id.id,
                    'location_id'   : self.location_id.id,
                    'location_dest_id'   : self.location_dest_id.id,
            })]
            return {
                    "error":False,
                    "message":"Barcode %s \n Added !!!"%(barcode),
                    "count":len(lot_id)
                    }

    def compute_list_product(self):
        for rec in self:
            rec.list_product = ', '.join(list(set(rec.mapped('move_ids_without_package.product_id.name'))))
    
    @api.model
    def create(self, vals):
        picking_type_id = self.env['stock.picking.type'].browse(vals['picking_type_id'])
        wh_code = picking_type_id.warehouse_id.code or 'WHS'
        if picking_type_id.code == 'incoming' :
            ptype = 'IN'
        elif picking_type_id.code == 'outgoing' :
            ptype = 'OUT'
        else :
            ptype = 'INT'
        pref = '%s/%s/NEW/'%(wh_code,ptype)
        sequence_id = self.env['ir.sequence'].search([
            ('code', '=', 'stock.picking'),
            ('prefix', '=', pref)
        ], limit=1)
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': 'Picking New %s'%(ptype),
                'code': 'stock.picking',
                'implementation': 'no_gap',
                'prefix': pref,
                'padding': 5,
            })
        vals['name'] = sequence_id.next_by_id()
        return super(StockPicking, self).create(vals)

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        no_picking = self.name
        self.name = no_picking.replace("/NEW", "")
        return res