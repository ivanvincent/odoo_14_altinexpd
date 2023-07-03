from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    faktur_supplier      = fields.Char(string='Faktur Supplier')
    surat_jalan_supplier = fields.Char(string='Surat Jalan Supplier')
    is_invoiced          = fields.Boolean(string='Invoiced ?', default=False) #untuk filter image to vendorbills
    purchase_id_2        = fields.Many2one('purchase.order', string='Purchase') #untuk kebutuhan release lewat po
    account_move_ids     = fields.One2many('account.move', 'picking_id', string='Journal Entries', required=False)
    just_flag            = fields.Boolean(string='Just Flag ?', store=False,) #untuk kebutuhan domain
    warehouse_id         = fields.Many2one('stock.warehouse', string='Warehouse', related="picking_type_id.warehouse_id") #Kebutuhan android
    lot_id               = fields.Many2one('stock.production.lot', string='Lot/Serial Number', related="move_line_ids_without_package.lot_id")

    def action_cancel(self):
        res = super(StockPicking, self).action_cancel()
        # ---- BEGIN PENGHAPUSAN JURNAL
        if(self.account_move_ids):
            for recMove in self.account_move_ids:
                recMove.button_cancel()
                recMove.unlink()
        # ---- END PENGHAPUSAN JURNAL
        return res

    #Create customer invoice from surat jalan
    # ORIGINAL CODE 1 JULI 2023
    # def action_create_invoice(self):
    #     move_line = []
    #     type = self.picking_type_id.code
    #     type_journal = 'purchase' if type == 'incoming' else 'sale'
    #     move_type = ''
    #     if type == 'incoming':
    #         move_type = 'in_invoice'
    #     elif type == 'outgoing' and self.picking_type_id.return_type == 'return_out':
    #         move_type = 'out_refund'
    #     else:
    #         move_type = 'out_invoice'
    #     journal_id = self.env['account.journal'].search([('type', '=', type_journal), ('active', '=', True)], limit=1).id

    #     po_obj = self.env['purchase.order'].search([('name', '=', self.origin)])
    #     price_list = {}
    #     for a in po_obj.order_line:
    #         price_list[a.product_id.id] = a.price_unit

    #     for picking in self:
    #         for line in picking.move_ids_without_package:
    #             account_id = line.product_id.categ_id.property_stock_account_input_categ_id.id if type == 'incoming' else line.product_id.categ_id.property_stock_account_output_categ_id.id
    #             move_line.append((0, 0, {
    #                 'product_id': line.product_id.id,
    #                 'name': line.product_id.name,
    #                 'account_id': account_id,
    #                 'quantity': line.quantity_done,
    #                 'product_uom_id': line.product_uom.id,
    #                 'purchase_line_id': line.purchase_line_id.id,
    #                 'price_unit': price_list.get(line.product_id.id, 0) if po_obj else line.product_id.standard_price,
    #                 # 'grade_id': line.grade_id.id, 
    #                 'tax_ids': [(6, 0, line.purchase_line_id.taxes_id.ids)],
                    
    #             }))

    #         picking.write({'is_invoiced': True})
            
    #         move = self.env['account.move'].create({
    #             'picking_id': picking.id,
    #             'partner_id': picking.partner_id.id,
    #             'move_type': move_type,
    #             'sj_supplier': self.no_sj if type_journal == 'purchase' else False,
    #             'payment_reference': picking.name,
    #             'invoice_date': fields.Date.today(),
    #             'journal_id': journal_id,
    #             'invoice_line_ids': move_line
    #         })

    #         view = self.env.ref('account.view_move_form')
    #         action = {
    #                     'name': 'Customer Invoice' if move.move_type == 'out_invoice' else 'Vendor Bills',
    #                     'type': 'ir.actions.act_window',
    #                     'view_mode': 'form',
    #                     'res_model': 'account.move',
    #                     'res_id': move.id,
    #                     'view_id': view.id,
    #                 }
    #         return action

    def action_create_invoice(self):
        print('::::::::::::::::::::::::::::::::::::::::::::::::')
        move_line = []
        type = self.picking_type_id.code
        type_journal = 'purchase' if type == 'incoming' else 'sale'
        move_type = ''
        if type == 'incoming':
            move_type = 'in_invoice'
        elif type == 'outgoing' and self.picking_type_id.return_type == 'return_out':
            move_type = 'out_refund'
        else:
            move_type = 'out_invoice'
        journal_id = self.env['account.journal'].search([('type', '=', type_journal), ('active', '=', True)], limit=1).id

        po_obj = self.env['purchase.order'].search([('name', '=', self.origin)])
        price_list = {}
        for a in po_obj.order_line:
            price_list[a.product_id.id] = a.price_unit

        for picking in self:
            for line in picking.move_ids_without_package:
                account_id = line.product_id.categ_id.property_stock_account_input_categ_id.id if type == 'incoming' else line.product_id.categ_id.property_stock_account_output_categ_id.id
                
                purchase_line = self.env['purchase.order.line'].search([('id', '=', line.purchase_line_id.id)])
                move_line.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'account_id': account_id,
                    # 'quantity': line.quantity_done,
                    'quantity': line.quantity_done / purchase_line.conversion,
                    'product_uom_id': line.product_uom.id,
                    'purchase_line_id': line.purchase_line_id.id,
                    'price_unit': price_list.get(line.product_id.id, 0) if po_obj else line.product_id.standard_price,
                    # 'grade_id': line.grade_id.id, 
                    'tax_ids': [(6, 0, line.purchase_line_id.taxes_id.ids)],
                    
                }))

            picking.write({'is_invoiced': True})
            
            move = self.env['account.move'].create({
                'picking_id': picking.id,
                'partner_id': picking.partner_id.id,
                'move_type': move_type,
                'sj_supplier': self.no_sj if type_journal == 'purchase' else False,
                'payment_reference': picking.name,
                'invoice_date': fields.Date.today(),
                'journal_id': journal_id,
                'invoice_line_ids': move_line
            })

            view = self.env.ref('account.view_move_form')
            action = {
                        'name': 'Customer Invoice' if move.move_type == 'out_invoice' else 'Vendor Bills',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'account.move',
                        'res_id': move.id,
                        'view_id': view.id,
                    }
            return action

    def action_view_invoices(self):
        move = self.env['account.move'].search([('picking_id', '=', self.id)])
        view = self.env.ref('account.view_move_form')
        action = {
                    'name': 'Customer Invoice' if move.move_type == 'out_invoice' else 'Vendor Bills',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree,form',
                    'res_model': 'account.move',
                    'domain': [('id', '=', move.ids)],
                    # 'res_id': move.ids,
                    # 'view_id': view.id,
                }
        return action
    
    def action_show_image(self):
        return

    @api.onchange('just_flag')
    def onchange_just_flag(self):
        self.just_flag = True
        """ User id = 2 adalah administrator"""
        
        user = self.env.user
        if user.id != 2:
            res = {}
            res['domain'] = {'location_dest_id': [('id', 'in', user.stock_location_dest_ids.ids)]}
            return res