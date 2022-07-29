from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    
    def _get_kg_conversion(self):
        for line in self:
            if line.product_uom.name == 'YARD' and line.raw_material_production_id:
                line.qty_conv_kg = (line.raw_material_production_id.gramasi_kain_finish / 1000 * line.raw_material_production_id.lebar_kain_finish / 100) * 0.9144 * line.product_uom_qty 
            else :
                line.qty_conv_kg = 0.0
                
                

    jenis_benang         = fields.Selection([("lusi","Lusi"),("pakan","Pakan")], string='Jenis Benang') #kebutuhan JO Sizing / Weaving
    kode_benang          = fields.Char(string='Kode Benang')
    is_extra             = fields.Boolean(string='Is Extra ?',default=False)
    kategori_id          = fields.Many2one('mrp.workcenter', string='Kategori')
    kategori_obat        = fields.Selection([("aux","Auxilarie"),("dye","Dye stuff")], string='Kategori Obat')
    qty_conv_kg          = fields.Float(string='Qty Kg',compute="_get_kg_conversion")
    chemical_conc        = fields.Float(string='Conc')
    
    
    

    #Start kebutuhan MO Twisting
    # lot = fields.Char(string='Lot')
    jml_creel   = fields.Float(string='Jml Creel/Cns', related='product_id.berat_per_cones')
    tm          = fields.Float(string='T/M', related='product_id.tm')
    tc_percent  = fields.Float(string='TC %', related='product_id.tc')
    da          = fields.Char(string='DA', compute='get_att_twisting',)
    keb_kg      = fields.Float(string='Keb. Kg', compute='get_att_twisting',)
    gramasi     = fields.Float(string='Gramasi')

    lot_id = fields.Many2one('stock.production.lot', string='Lot')
    twist = fields.Char(string='Twist')
    brt_cyi = fields.Float(string='Brt/Cyi')
    #End kebutuhan MO Twisting

    #Start kebutuhan MO Dyeing
    type        = fields.Selection([("opc","Opc"),("finish","Finish")], string='Type')
    #End kebutuhan MO Dyeing

    # Untuk filter Product Berdasarkan Mrp Type
    @api.onchange('company_id')
    def onchange_company_id(self):
        context = self.env.context
        if 'default_type_id' in context:
            res = {}
            type = self.env['mrp.type'].browse(context['default_type_id'])
            res['domain'] = {'product_id': [('categ_id', 'in', type.component_product_category_ids.ids)]}
            return res
            
    @api.depends('product_id')
    def get_att_twisting(self):
        for rec in self:
            rec.da = rec.product_id.td * (100 / (100 - rec.tc_percent))
            rec.keb_kg = rec.gramasi * rec.raw_material_production_id.order_penarikan_sw
    
        
        

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    is_extra = fields.Boolean(string='Is Extra ?',default=False)
    