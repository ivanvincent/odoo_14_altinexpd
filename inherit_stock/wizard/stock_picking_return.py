from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging 
_logger = logging.getLogger(__name__)


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'
    
    
    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError(_("You may only return one picking at a time."))
        res = super(ReturnPicking, self).default_get(fields)
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'stock.picking':
            picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
            if picking.exists():
                res.update({'production_id': picking.production_id.id})
        return res
    
    
    production_id = fields.Many2one('mrp.production', string='Production')
    
    
    def create_returns(self):
        res = super(ReturnPicking, self).create_returns()
        
        if self.production_id and self.production_id.state == 'done':
            mo_name          = self.production_id.type_id.production_sequence_id.next_by_id()
            lot_producing_id = self.env['stock.production.lot'].sudo().create({
                    "name": mo_name,
                    "tanggal_produksi":self.production_id.date_planned_start.date(),
                    "location_id":self.production_id.picking_type_id.default_location_src_id.id,
                    "product_id":self.production_id.product_id.id,
                    "company_id":self.env.user.company_id.id
                })
            new_production = self.production_id.copy({
                "name":mo_name,
                "production_origin_id":self.production_id.id,
                "origin":self.production_id.name,
                "lot_producing_id": lot_producing_id.id,
                "labdip_extra_ids":[],
                "component_chemical_has_request":False,
                "qty_producing":self.production_id.qty_producing,
                "picking_finished_id" :False,
                "returned_finished_ids" : [],
            })
            new_production.message_post_with_view('mail.message_origin_link',
            values={'self': new_production, 
                    'origin': self.picking_id
                    
                    },
            subtype_id=self.env.ref('mail.mt_note').id)
            
            self.production_id.sudo().write({"state":'return'})
            picking_id = self.env['stock.picking'].browse([res.get('res_id')])
            
            _logger.warning('='*40)
            _logger.warning('return ')
            _logger.warning(new_production)
            _logger.warning(picking_id.write({"production_id":self.production_id.id}))
            _logger.warning(picking_id.production_id.name)
            _logger.warning('='*40)
            
        
        
        
        
        return res
        
        
        