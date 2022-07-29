from odoo import fields, models, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class MRPRawRevisionWizard(models.TransientModel):

    _name = 'mrp.raw.revision.wizard'
    
    
            
    
    @api.model
    def default_get(self, fields_list):
        res = super(MRPRawRevisionWizard, self).default_get(fields_list)
        picking_id = self.env.context.get("default_picking_id", False)
        move_ids = self.env['stock.move'].search([('picking_id','=',picking_id)])
        res.update({"move_raw_ids" :  [(6,0,move_ids.ids)]})
        return res
    
    
    name          = fields.Char(string='Revision')
    production_id = fields.Many2one('mrp.production', string='Production')
    picking_id   = fields.Many2one('stock.picking', string='Stock Picking')
    greige_id     = fields.Many2one('product.product', string='Greige',domain=[('categ_id.name', '=', 'GREY')])
    product_id    = fields.Many2one('product.product', string='Greige Revision',domain=[('categ_id.name', '=', 'GREY')])
    uom_id        = fields.Many2one(related='greige_id.uom_id', string='Uom')
    quantity      = fields.Float(string='Quantity')
    move_raw_ids  = fields.Many2many('stock.move','stock_move_raw_revision_wiz_rel', string='Move Raw')
    note          = fields.Text(string='Note')
    user_id       = fields.Many2one('res.users', string='Requested By',default=lambda self: self.env.user.id)
    
    

    def create_revision(self):
        id = self._context.get('active_id')
        
        revision = self.env['mrp.raw.revision']\
        .sudo().create({"production_id":self.production_id.id,"greige_id":self.greige_id.id,
                        "picking_id":self.picking_id.id,
                        "move_raw_ids": [(6,0,self.move_raw_ids.ids)],
                        "product_id":self.product_id.id,"quantity":self.quantity,
                        "note":self.note,"state":"confirm"})
        

        self.picking_id.sudo().write({"raw_revision_id":revision.id})
        
        # self.picking_id.button_validate()
        
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Mrp Raw Revision',
        #     'res_model': 'mrp.raw.revision',
        #     'view_mode': 'form',
        #     'res_id':revision.id,
        #     'target': 'current',
        # }
