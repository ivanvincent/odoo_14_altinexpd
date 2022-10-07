from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

import logging
_logger = logging.getLogger(__name__)

class SplitWizard(models.TransientModel):

    _name = 'split.barcode.wizard'
    
    
    
    lot_id           = fields.Many2one('stock.production.lot', string='Barcode')
    lot_name         = fields.Char(string='New Barcode')
    location_id      = fields.Many2one('stock.location', string='Location')
    product_id       = fields.Many2one('product.product',related="lot_id.product_id",string='Product')
    product_uom_id   = fields.Many2one('uom.uom',related="product_id.uom_id" ,string='Uom')
    warehouse_id     = fields.Many2one('stock.warehouse', string='Warehouse')
    quantity         = fields.Float(string='Quantity')
    new_quantity     = fields.Float(string='New Quantity')
    picking_id       = fields.Many2one('stock.picking', string='Stock Picking')
    sj_pro_app       = fields.Char(string='SJ PRO APP')
    
    
    @api.onchange('lot_id')
    def get_quantity(self):
        self.quantity = self.lot_id.product_qty
    
    
    
    
    def _create_lot(self,lot_name):
        return self.env['stock.production.lot'].sudo().create({
            "name":lot_name,
            "product_id":self.product_id.id,
            # "product_category":self.product_id.categ_id.id,
            # "location_id":self.location_id.id,
            "product_uom_id":self.product_id.uom_id.id,
            # "tanggal_produksi":self.lot_id.tanggal_produksi,
            # "rack_id": self.lot_id.rack_id.id,
            "company_id":self.env.company.id,
            # "grade_id": self.lot_id.grade_id.id ,
            # "lebar": self.lot_id.lebar  or False,
            # "pic": self.lot_id.pic  or False,
            # "move_line_ids": [(0,0,{
            #     "name":self.lot_id.product_id.name,
            #     "product_id":self.lot_id.product_id.id,
            #     "lot_parent_name": self.lot_id.name,
            #     "location_id":self.location_id.id,
            #     "quantity":self.lot_id.product_qty,
                # "state":"split",
                # "grade_id": self.lot_id.grade_id.id ,
            # })]
        
            })
        
    def _prepare_split_vals(self,lot):
        move_in_line_ids = []
        move_out_line_ids = []
        move_out_line_ids.append((0,0,{
                'product_id': self.product_id.id,
                'lot_id': self.lot_id.id,
                # 'grade_id': self.lot_id.grade_id.id,
                'lot_name': self.lot_id.name,
                'product_uom_id': self.product_id.uom_id.id,
                # 'location_id': self.location_id.id,
                'qty_done': self.new_quantity,
                'rack_id': self.lot_id.rack_id.id,
                "location_dest_id":15,
                'company_id':self.env.company.id,
            }))
                
        move_in_line_ids.append((0,0,{
            
            'product_id': self.product_id.id,
            'lot_id': lot.id,
            'grade_id': lot.grade_id.id,
            'lot_name': lot.name,
            'product_uom_id': self.product_id.uom_id.id,
            'location_id': 15,
            'qty_done': self.new_quantity,
            'rack_id': self.lot_id.rack_id.id,
            "location_dest_id":self.location_id.id,
            'company_id':self.env.company.id,
        
            
        }))
                
        stock_picking_in = self.env['stock.picking'].sudo().create({
            "picking_type_id": self.warehouse_id.in_type_id.id,
            'location_id': 15,
            "origin": "SPLIT BARCODE ",
            "location_dest_id":self.location_id.id,
            'move_line_ids_without_package':move_in_line_ids,
        })
        
        stock_picking_out = self.env['stock.picking'].sudo().create({
            "picking_type_id": self.warehouse_id.int_type_id.id,
            'location_id': self.location_id.id,
            "origin": "SPLIT BARCODE ",
            "location_dest_id":15,
            'move_line_ids_without_package':move_out_line_ids,
        })
        
        if stock_picking_in and stock_picking_out:
            stock_picking_in.action_confirm()
            stock_picking_in.with_context(split_barcode=True).action_assign()
            stock_picking_in.button_validate()
            
            stock_picking_out.action_confirm()
            stock_picking_out.with_context(split_barcode=True).action_assign()
            stock_picking_out.button_validate()
            
        return (stock_picking_in,stock_picking_out)
    
    
    
    

    def action_split(self):
        active_model = self._context.get('model') or self._context.get('params').get('model') if  'params' in self._context else self._context.get('active_model')
        lot_ids = []
        if self.new_quantity > self.lot_id.product_qty:
            raise UserError(_('New quantity more than parent quantity !!!'))
        
        elif self.new_quantity == 0:
            raise UserError(_('New quantity is null !!!'))
                
        elif active_model == 'stock.production.lot' and self.warehouse_id:
            lot_name = self.lot_name if self.lot_name else False
            if self.location_id.location_id.name == 'GDGK' and not lot_name:
                lot_name = self.env['ir.sequence'].next_by_code('stock.production.lot.greige')
            if self.location_id.location_id.name == 'GDJU' and not lot_name:
                lot_name = self.env['ir.sequence'].next_by_code('stock.production.lot.gdj')
            
            lot = self._create_lot(lot_name)
            lot_ids.append(lot.id)
            lot_ids.append(self.lot_id.id)
            stock_picking_in , stock_picking_out =self._prepare_split_vals(lot)
            if stock_picking_in.state == 'done' and stock_picking_out.state == 'done':
                action = self.env.ref('stock.action_production_lot_form').read()[0]
                action['domain'] = [('id', 'in', lot_ids)]
                action['context'] = {'search_default_group_by_product': 1, 'display_complete': True, 'default_company_id': self.env.company.id}
                return action
            
        elif self._context.get('split_bacode_at_picking'):
            if not self.lot_id:
                raise UserError(_('New quantity is null !!!'))
            lot_name = self.lot_name if self.lot_name else False
            if self.location_id.location_id.name == 'GDGK' and not lot_name:
                lot_name = self.env['ir.sequence'].next_by_code('stock.production.lot.greige')
            if self.location_id.location_id.name == 'GDJU' and not lot_name:
                lot_name = self.env['ir.sequence'].next_by_code('stock.production.lot.gdj')
            lot = self._create_lot(lot_name)
            lot_ids.append(lot.id)
            lot_ids.append(self.lot_id.id)
            stock_picking_in , stock_picking_out =self._prepare_split_vals(lot)
            if stock_picking_in.state == 'done' and stock_picking_out.state == 'done':
                action = self.env.ref('stock.action_production_lot_form').read()[0]
                action['domain'] = [('id', 'in', lot_ids)]
                action['context'] = {'search_default_group_by_product': 1, 'display_complete': True, 'default_company_id': self.env.company.id}
                return action
            
            
        elif active_model == 'stock.picking' or active_model == 'stock.move.line' and self.warehouse_id:
            lot_name = self.lot_name if self.lot_name else False
            if self.location_id.location_id.name == 'GDGK' and not lot_name:
                lot_name = self.env['ir.sequence'].next_by_code('stock.production.lot.greige')
            if self.location_id.location_id.name == 'GDJU' and not lot_name:
                lot_name = self.env['ir.sequence'].next_by_code('stock.production.lot.gdj')
            
            lot = self._create_lot(lot_name)
            lot_ids.append(lot.id)
            lot_ids.append(self.lot_id.id)
            stock_picking_in , stock_picking_out =self._prepare_split_vals(lot)
            move_line_id = self.env['stock.move.line'].browse([self._context.get('default_move_line_id')])
            diff_quantity = self.lot_id.product_qty
            move_line_id.write({"lot_id":self.lot_id.id,"qty_done":self.lot_id.product_qty})
            if float_compare(diff_quantity, 0.0, precision_rounding=self.lot_id.product_id.uom_id.rounding) > 0:
                move_line_id.write({"lot_id":self.lot_id.id,"qty_done":diff_quantity})
            diff_quantity = self.new_quantity
            new_move_line_vals = {
                    "lot_id":lot.id,    
                    "qty_done":self.new_quantity,
                    "product_id":lot.product_id.id, 
                    "product_uom_id":lot.product_id.uom_id.id,
                    "location_id":self.picking_id.location_id.id,
                    "location_dest_id":self.picking_id.location_dest_id.id,
            }
            self.picking_id.write({"move_line_ids_without_package":[(0,0,new_move_line_vals)]})
