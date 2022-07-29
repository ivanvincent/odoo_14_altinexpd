from odoo import fields, models, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class SplitWizard(models.TransientModel):

    _name = 'split.barcode.wizard'
    
    # out_type_id
    
    
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
    # split_count      = fields.Integer(string='Splitting Count')
    # line_ids         = fields.One2many('split.barcode.line.wizard', 'wizard_id', string='Details')
    # move_line_id     = fields.Many2one('stock.move.line', string='Stock Move Line')
    # is_over_qty      = fields.Boolean(string='Over QUantity',compute="_get_total_quantity")
    
    
    
    
    
    # def _get_total_quantity(self):
    #     for lot in self:
    #         lot.is_over_qty = sum(lot.line_ids.mapped('new_quantity')) > lot.quantity
        
    
    
    # def generate_barcode(self):
    #     if self.split_count > 0:
    #         if self.location_id.location_id.name == 'GDGK':
    #             line_ids = []
    #             for line in range(self.split_count):
    #                 lot_name = self.env['ir.sequence'].next_by_code('stock.production.lot.greige')
    #                 line_ids.append((0,0,{"lot_name":lot_name ,"product_id":self.product_id.id}))
    #             self.line_ids = line_ids
                
    #         return {
    #         'name': _('Split Barcode'),
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'split.barcode.wizard',
    #         'res_id': self.id,
    #         'target': 'new',
    #      }   
    
    
    

    def action_split(self):
        active_model = self._context.get('model')
        move_line_ids = []
        if self.new_quantity > self.quantity:
            raise UserError('New Quantity more than Parent Quantity !!!')
                
        elif active_model == 'stock.production.lot' and self.warehouse_id:
            #    if self.location_id.location_id.name == 'GDGK':
            lot_name = self.lot_name if self.lot_name else False
            if self.location_id.location_id.name == 'GDGK' and not lot_name:
                lot_name = self.env['ir.sequence'].next_by_code('stock.production.lot.greige')
            if self.location_id.location_id.name == 'GDJU' and not lot_name:
                lot_name = self.env['ir.sequence'].next_by_code('stock.production.lot.gdj')
            
            move_in_line_ids = []
            move_out_line_ids = []
            lot_ids = []
            lot = self.env['stock.production.lot'].sudo().create({
            "name":lot_name,
            "product_id":self.product_id.id,
            "product_category":self.product_id.categ_id.id,
            "location_id":self.location_id.id,
            "product_uom_id":self.product_id.uom_id.id,
            "tanggal_produksi":self.lot_id.tanggal_produksi,
            "rack_id": self.lot_id.rack_id.id,
            "company_id":self.env.company.id,
            # "picking_ids": [(6,0,self.lot_id.picking_ids)] if self.lot_id.picking_ids else False,
            "grade_id": self.lot_id.grade_id.id ,
            "lebar": self.lot_id.lebar  or False,
            "pic": self.lot_id.pic  or False,
            "move_line_ids": [(0,0,{
                "name":self.lot_id.product_id.name,
                "product_id":self.lot_id.product_id.id,
                "lot_parent_name": self.lot_id.name,
                "location_id":self.location_id.id,
                "quantity":self.lot_id.product_qty,
                "state":"split",
                "grade_id": self.lot_id.grade_id.id ,
            })]
        
            })
            
            
            
            
            lot_ids.append(lot.id)
            lot_ids.append(self.lot_id.id)
                
            
            
                
            move_out_line_ids.append((0,0,{
                
                'product_id': self.product_id.id,
                'lot_id': self.lot_id.id,
                'grade_id': self.lot_id.grade_id.id,
                'lot_name': self.lot_id.name,
                'product_uom_id': self.product_id.uom_id.id,
                'location_id': self.location_id.id,
                'qty_done': self.new_quantity,
                'rack_id': self.lot_id.rack_id.id,
                # 'product_uom_qty':uom_quantity,
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
                # 'product_uom_qty':uom_quantity,
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
                stock_picking_in.action_assign()
                stock_picking_in.button_validate()
                
                stock_picking_out.action_confirm()
                stock_picking_out.action_assign()
                stock_picking_out.button_validate()
                
                if stock_picking_in.state == 'done' and stock_picking_out.state == 'done':
                    action = self.env.ref('stock.action_production_lot_form').read()[0]
                    action['domain'] = [('id', 'in', lot_ids)]
                    action['context'] = {'search_default_group_by_product': 1, 'display_complete': True, 'default_company_id': self.env.company.id}
                    return action
                    
                    



# class SplitWizardLine(models.TransientModel):

#     _name = 'split.barcode.line.wizard'
    
#     wizard_id       = fields.Many2one('split.barcode.wizard', string='Wizard')
#     lot_name        = fields.Char(string='New Barcode')
#     lot_id          = fields.Many2one('stock.production.lot', string='Barcode')
#     product_id      = fields.Many2one('product.product', string='Product')
#     new_quantity    = fields.Float(string='Quantity')
#     product_uom_id  = fields.Many2one('uom.uom',related="product_id.uom_id" ,string='Uom')