from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    #todo fix me 
    om_id      = fields.Many2one('pull.cron.om', string='Order Marketing')
    sj_greige  = fields.Many2one('pull.cron.sj.greige', string='SJ GREIGE')
    
    
    
    
    
    @api.onchange('sj_greige')
    def on_change_sj_greige(self):
        if self.sj_greige:
            moveline_ids = []
            for line in self.sj_greige.line_ids:
                grade_id = self.env['makloon.grade'].sudo().search([('name','=',line.grade)],limit=1)
                line.product_id.sudo().write({
                        "tracking":'lot',
                        "pic":line.pic,
                        "lebar":line.lebar,
                        "categ_id":127,
                        "type":'product',
                        "gramasi_finish":line.gramasi_finish,
                        "default_code": line.kd_kain,
                        "gramasi_greige":line.gramasi_greige,
                        "kelompok":line.kelompok,
                        "std_potong":line.std_potong,
                    })
                
                lot = self.env['stock.production.lot'].sudo().create({
                        "name":line.barcode,
                        "product_id":line.product_id.id,
                        "product_category":line.product_id.categ_id.id,
                        "location_id":self.location_dest_id.id,
                        "product_uom_id":line.product_id.uom_id.id,
                        "tanggal_produksi":line.tanggal_prod,
                        "kelompok":line.kelompok,
                        # "rack_id":if,
                        "company_id":self.env.company.id,
                        "grade_id": grade_id.id ,
                        "lebar": line.lebar  or False,
                        "pic": line.pic  or False,
                    
                })
                
                moveline_template = {
                        'product_id': line.product_id.id,
                        'lot_id': lot.id,
                        'grade_id': grade_id.id,
                        'lot_name': lot.name,
                        'product_uom_id': line.product_id.uom_id.id,
                        'location_id': 15,
                        'qty_done': line.quantity,
                        'rack_id': self.rack_id.id,
                        # 'product_uom_qty':uom_quantity,
                        "location_dest_id":self.location_dest_id.id,
                        'company_id':self.env.company.id,
                        
                    }
                moveline_ids.append((0,0,moveline_template))
            self.move_line_ids_without_package = moveline_ids
        # else:
            # self.with_context(prefetch_fields=False).mapped('move_lines').unlink()
            
            # self.move_ids_without_package = False
            # self.move_lines = False
            # self.move_line_ids = False
            # self.move_line_ids_without_package = False
            # self.move_line_nosuggest_ids = False
    
    
    @api.onchange('om_id')
    def on_change_om(self):
        if self.om_id:
            lot_ids = self.env['stock.production.lot'].sudo().search([('no_om','=',self.om_id.name)])
            self.move_line_ids_without_package = False
            if not self.move_line_ids_without_package :
                self.move_line_ids_without_package = [(0,0,{ 'product_id': lot.product_id.id,
                'lot_id': lot.id,
                'lot_name': lot.name,
                'product_uom_id': lot.product_id.uom_id.id,
                'location_id': self.location_id.id,
                'qty_done': lot.product_qty,
                'product_uom_qty': lot.product_qty,
                'location_dest_id': self.location_dest_id.id,
                'company_id':self.env.company.id, }) for lot in lot_ids.filtered(lambda x :x.product_qty > 0)]