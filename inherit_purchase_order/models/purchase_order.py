from typing import Sequence
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_release        = fields.Integer(string='Release', 
    # compute='_compute_picking_release',
     default=0)
    purchase_category_id = fields.Many2one('purchase.order.category', string='Category')
    payment_term_id      = fields.Many2one('account.payment.term', string='Payment Term')
    street_delivery      = fields.Many2one('street.delivery', string='Street Delivery')
    date_datang_barang   = fields.Text(string='Dtg Barang', compute="_compute_date_datang_barang")
    lot_id               = fields.Many2one('stock.production.lot', string='Lot / serial number', related='order_line.lot_id')
    purchase_order_offer_line_ids = fields.One2many('purchase.order.offer', 'purchase_id', 'Line')
    state                 = fields.Selection(selection_add=[('draft', 'Draft'), ('approve', 'To be Approve'), ('purchase', 'Approved'), ("reject", "Rejected"),("done", "Done")])
    picking_count_makloon = fields.Integer(string='Picking Count Makloon', compute='compute_picking_count_makloon')
    is_surat_jalan        = fields.Boolean(string='Surat Jalan ?')
    is_bill               = fields.Boolean(string='Bill ?',)
    is_fp                 = fields.Boolean(string='Faktur Pajak ?', 
    # compute="_compute_document"
    )
    

    def action_approve(self):
        self.state = 'approve'

    def button_reject(self):
        for order in self:
                order.write({'state': 'reject'})
        return True
    
    
    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        date_done_ids = self.mapped('picking_ids.date_done')
        filtered = filter(lambda x: x != False, date_done_ids)
        date_max = max(filtered)
        res['date_datang_barang'] = date_max ## set datang barang
        return res

    def action_view_release(self):
        action = False
        product = [{'product_id': a.product_id.id, 'quantity' : a.qty_received} for a in self.order_line]
        move_ids = [(0, 0, {'product_id':a.product_id.id, 'product_uom_qty':(a.qty_received - a.qty_released), 'product_uom': a.product_uom.id, 'name': a.product_id.name}) for a in self.order_line.filtered(lambda x: x.qty_received > x.qty_released)]
        context = {
            'default_origin' : 'Release from %s' % (self.name),
            'default_purchase_id_2' : self.id,
            'product' : product,
            'default_move_ids_without_package' : move_ids,
            'release_from_po' : True
        }
        if self.total_release < 1:
            view_id = self.env.ref('stock.view_picking_form')
            action = {
                        'name': _('Inventory Release'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'stock.picking',
                        'view_mode': 'form',
                        'target': 'current',
                        'view_id': view_id.id,
                        'context': context,
                    }
        else:
            action = self.env.ref('stock.action_picking_tree_all').read()[0]
            action['domain'] = [('purchase_id_2', '=', self.id)]
            action['context'] = context
        return action

    def _compute_picking_release(self):
        picking_obj = self.env['stock.picking'].search([('purchase_id_2', '=', self.id)])
        for order in self:
            order.total_release = len(picking_obj)

    # Start Override from base odoo
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'approve']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()

                # BEGIN PERUBAHAN PRODUCT_UOM_QTY PADA STOCK_MOVE BERDASARKAN CONVERSION * PRODUCT_QTY
                for data_line in order.order_line:
                    data_stock_move = self.env['stock.move'].search([('purchase_line_id', '=', data_line.id)])
                    if data_stock_move:
                        data_stock_move.product_uom_qty = data_line.conversion * data_line.product_qty
                # END PERUBAHAN PRODUCT_UOM_QTY PADA STOCK_MOVE BERDASARKAN CONVERSION * PRODUCT_QTY


            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
            if self.makloon_id:
                self.env['stock.picking'].create({
                    'picking_type_id': self.picking_type_id.id,
                    'partner_id': self.partner_id.id,
                    'user_id': False,
                    'date': self.date_order,
                    'origin': self.name,
                    'location_dest_id': self._get_destination_location(),
                    'location_id': self.picking_type_id.default_location_src_id.id,
                    'company_id': self.company_id.id,
                    'move_ids_without_package': [(0, 0, {
                        'name': material.product_id.name,
                        'product_id': material.product_id.id,
                        'product_uom': material.product_uom.id,
                        'date': self.date_order,
                        'location_id': self.picking_type_id.default_location_src_id.id, #sself.warehouse_id.wh_output_stock_loc_id.id,
                        'location_dest_id': self._get_destination_location(),
                        'partner_id': self.partner_id.id,
                        'state': 'draft',
                        'company_id': self.company_id.id,
                        'price_unit': material.product_id.standard_price,
                        # 'picking_type_id': self.warehouse_id.out_type_id.id,
                        'group_id': False,
                        'origin': self.name,
                        'warehouse_id': self.picking_type_id.warehouse_id.id,
                    }) for material in self.makloon_id.result_ids]
                })
        return True
    # End Override from base odoo

    @api.model
    def create(self, vals):
        # roman_dict = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII',
        #             13: 'XIII', 14: 'XIV', 15: 'XV', 16: 'XVI', 17: 'XVII', 18: 'XVIII', 19: 'XIX', 20:'XX', 21: 'XXI', 22:'XXI', 23:'XXIII', 24:'XXIV',
        #             25:'XXV', 26:'XXVI', 27:'XXVII', 28:'XXVIII', 29:'XXIX',30:'XXX',31:'XXXI',}

        # roman = roman_dict[int(datetime.now().strftime("%m"))]
        # next_number = self.env['ir.sequence'].next_by_code('purchase.order.custom.code')
        # departement_code = self.env['stock.picking.type'].browse(vals.get('picking_type_id')).warehouse_id.sequence_code_po
        # categ_code = self.env['purchase.order.category'].browse(vals.get('purchase_category_id')).sequence_code_po
        # years = datetime.now().strftime('%Y')
        
        # if not categ_code:
        #     raise UserError("Silahkan isi kode sequence purchase order category")
        # po_number = '%s/%s/%s/%s' % (roman, next_number, categ_code, years)
        # vals['name'] = po_number # set po number
        if 'purchase_category_id' in vals:
            if vals['purchase_category_id']:
                # if  vals['purchase_category_id'] == 4:
                #     category = self.env['purchase.order.category'].browse([vals['purchase_category_id']])
                #     seq = category.sequence_id.next_by_id().split('/')
                #     seq[0] = roman_dict[int(seq[0])]
                #     seq[1] = roman_dict[int(seq[1])]
                #     vals['name'] = '/'.join(seq)
                # else:

                category = self.env['purchase.order.category'].browse([vals['purchase_category_id']])
                vals['name'] = category.sequence_id.next_by_id()
                
                # if category.name.lower() == 'umum':
                #     sequence = self.env['ir.sequence'].next_by_code('purchase.order.umum') 
                #     vals['name'] = sequence
                # elif category.name.lower() == 'obat':
                #     sequence = self.env['ir.sequence'].next_by_code('purchase.order.obat') 
                #     vals['name'] = sequence
                # elif category.name.lower() == 'pt bara':
                #     sequence = self.env['ir.sequence'].next_by_code('purchase.order.pbr') 
                #     vals['name'] = sequence
                
        res = super(PurchaseOrder, self).create(vals)
        return res

    def _compute_date_datang_barang(self):
        for rec in self:
            picking_ids = rec.picking_ids
            if picking_ids:
                rec.date_datang_barang = '\n '.join(d.strftime("%Y/%m/%d")for d in picking_ids.mapped('scheduled_date'))
            else:
                rec.date_datang_barang = False
                
                
    # def action_show_image(self):
    #     action = self.env.ref('inherit_purchase_order.purchase_order_action').read()[0]
    #     action['res_id'] = self.id
    #     action['name'] = "Images of %s" % (self.product_id.name)
    #     return action

    def action_view_picking_makloon(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action['domain'] = [('origin', '=', self.name)]
        # action['domain'] = [('origin', '=', self.name), ('makloon_order_id', '=', self.makloon_id.id)]
        return action

    def compute_picking_count_makloon(self):
        # picking = self.env['stock.picking'].search([('origin', '=', self.name), ('makloon_order_id', '=', self.makloon_id.id)])
        picking = self.env['stock.picking'].search([('origin', '=', self.name)])
        for rec in self:
            rec.picking_count_makloon = len(picking.ids)

    # def action_create_invoice(self):
    #     if self.picking_count > 1 and not self.is_surat_jalan and not self.is_bill and not self.is_fp:
    #         raise UserError('Mohon maaf silahkan lengkapi tanda terima dokumen terlebih dahulu')
    #     res = super(PurchaseOrder, self).action_create_invoice()
    #     return res

    # def _compute_document(self):
    #     for rec in self:
    #         if rec.surat_jalan_doc :
    #             rec.is_surat_jalan = True
    #         else:
    #             rec.is_surat_jalan = False

    #         for rec in self:
    #             if rec.bill_doc:
    #                 rec.is_bill = True
    #             else:
    #                 rec.is_bill = False

    #             for rec in self:
    #                 if rec.fp_doc :
    #                     rec.is_fp = True
    #                 else:
    #                     rec.is_fp = False