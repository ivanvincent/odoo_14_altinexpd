from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    
    
    # production_id        = fields.Many2one('mrp.production', string='Production')
    # production_type_id   = fields.Many2one('mrp.type', related='production_id.type_id' ,string='Production Type')
    # gramasi_finish       = fields.Float(string='Gramasi',related="production_id.gramasi_kain_finish")
    # lebar_finish         = fields.Float(string='Lebar',related="production_id.lebar_kain_finish")
    qty                  = fields.Float(string='Qty', related='product_qty', store=True,)
    # color_id             = fields.Many2one(related='product_id.color_id', string='Color')
    # design_id            = fields.Many2one(related='product_id.design_id', string='Design')
    
    
    # sale_id              = fields.Many2one(related='production_id.sale_id', string='Sake Order')
    # beam_id              = fields.Many2one('mrp.production.beam', string='Beam')
    # beam_type_id         = fields.Many2one(related='beam_id.type_id', string='Beam Type')    
    location_id          = fields.Many2one('stock.location', string='Location')
    product_category     = fields.Many2one('product.category', string='Product Category', related='product_id.categ_id', store=True,)
    picking_ids          = fields.Many2many(
        comodel_name='stock.picking', 
        relation='stock_production_picking_history_rel',
        string='Transfer History'
        )
    
    
    shift                = fields.Char(string='Shift')
    # quantity_kanji       = fields.Float(string='Quantity Kanji')
    # quantity_murni       = fields.Float(string='Quantity Murni')
    # quantity_brutto      = fields.Float(string='Quantity Brutto')
    # quantity_tarra       = fields.Float(string='Quantity Tarra')
    # panjang_awal         = fields.Float(string='Panjang Awal')
    # panjang_sisa         = fields.Float(string='Panjang Sisa')
    # sisa_actual_beam     = fields.Float(string='Sisa Actual Beam')
    # tanggal_beam         = fields.Date(string='Tanggal Beam')
    state                = fields.Selection([("available","Available"),("sold","Sold"),("released","Released"),("return","Returned")], string='Status')
   
    #todo fixme
    harga                = fields.Float(string='Harga')
    no_warna             = fields.Char(string='Warna')
    pic                  = fields.Float(string='Pic')
    lebar                = fields.Float(string='Lebar')
    grade_id             = fields.Many2one('makloon.grade', string='Grade')
    tanggal_produksi     = fields.Date(string='Tanggal Masuk')
    rack_id              = fields.Many2one('master.rack', string='Rack')
    no_om                = fields.Char(string='No Om')
    kelompok             = fields.Char(string='Kelompok')
    cone                 = fields.Char(string='Cone')
    
    
    # move_line_ids        = fields.One2many('stock.move.line.before', 'lot_id', string='History')
    # move_line_ids         = fields.Many2many('stock.move.line.before', 'moveline_rel','lot_prepare_id',string='History' )

    product_age          = fields.Integer('Age', compute='ProductAgeLot', store=True, readonly=True)
    category_age         = fields.Char('Category Age', compute='_get_category_age', store=True, readonly=True)

    def ProductAgeLot(self):
        self.env.cr.execute("""update stock_production_lot set product_age = current_date - tanggal_produksi""")
        
    @api.depends('product_age')
    def _get_category_age(self):
        for rec in self:
            if rec.product_age >= 0 and rec.product_age <= 90:
                rec.category_age = 'HIJAU'
            elif rec.product_age >= 90 and rec.product_age <= 180:
                rec.category_age = 'ORANGE'
            elif rec.product_age >= 180 and rec.product_age <= 365:
                rec.category_age = 'MERAH'
            elif rec.product_age > 365:
                rec.category_age = 'HITAM'
    
    
    
    
    def open_split_barcode_wizard_form(self):
        warehouse_id = self.env['stock.warehouse'].sudo().search([('lot_stock_id','=',self.location_id.id)],limit=1).id  if self.location_id else False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Split Barcode',
            'res_model': 'split.barcode.wizard',
            'view_mode': 'form',
            'context': {'default_lot_id':self.id,"default_quantity":self.product_qty,"default_location_id":self.location_id.id,"default_warehouse_id":warehouse_id,"model":self._name},
            'target': 'new',
        }
    
    
    def _create_moveline(self,lots =[]):
        moveline_ids = []
        move_ids = []
        #note
        warehouse_id = self.env.user.default_warehouse_ids
        if warehouse_id:
            for lot in lots:
                moveline_template = {
                        'product_id': lot.product_id.id,
                        'lot_id': lot.id,
                        'lot_name': lot.name,
                        'product_uom_id': lot.product_id.uom_id.id,
                        'qty_done': lot.product_qty,
                        'company_id':self.env.company.id,
                        'location_id': warehouse_id[0].out_type_id.default_location_src_id.id,
                        'location_dest_id': warehouse_id[0].out_type_id.default_location_dest_id.id,
                }
                
                moveline_ids.append((0,0,moveline_template))
                
                move_template = {
                        'name': lot.product_id.name,
                        'date':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'product_id': lot.product_id.id,
                        'product_uom': lot.product_id.uom_id.id,
                        'product_uom_qty': lot.product_qty,
                        'company_id': self.env.company.id,
                        'location_id': warehouse_id[0].out_type_id.default_location_src_id.id,
                        'location_dest_id': warehouse_id[0].out_type_id.default_location_dest_id.id,
                    }
                move_ids.append((0,0,move_template))
                
            
            
            
            picking_template = {
                'picking_type_id': warehouse_id[0].out_type_id.id or False,
                'date': fields.Date.today(),
                'scheduled_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'location_id': lot.location_id.id,
                'location_dest_id': 5,
                'immediate_transfer': False,
                'move_line_nosuggest_ids': moveline_ids,
                'move_lines':move_ids,
                
            }
            
            picking = self.env['stock.picking'].create(picking_template)
            return picking
        else:
            raise UserError("You Don't Have Default Warehouse")
            
    
    
    def _create_picking(self):
        active_ids = self.browse(self._context.get('active_ids'))
        picking = self._create_moveline(active_ids)
        picking.action_confirm()
        picking.action_assign()
        
        return {
            'name': 'Delivery Orders',
            'view_mode': "form",
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': picking.id,
        }

    @api.model
    def create(self, vals):
        ctx = self.env.context
        vals['company_id'] = ctx.get('allowed_company_ids', [1])[0]
        res = super(StockProductionLot, self).create(vals)

        return res

# class Stock(models.Model):
#     _inherit = 'mrp.production'
    
    
#     lot_id          = fields.Many2one('stock.production.lot', string='Kartu Beam')
#     beam_id         = fields.Many2one('mrp.production.beam', related='lot_id.beam_id',string='No Beam')
#     beam_type_id    = fields.Many2one('mrp.production.beam.type', string='Beam Type', related='beam_id.type_id')

    
    
    
    


    