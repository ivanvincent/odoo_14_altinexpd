from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools.float_utils import float_compare, float_is_zero, float_repr, float_round
import logging
_logger = logging.getLogger(__name__)

class inspectTransferWizard(models.TransientModel):

    _name = 'inspect.transfer.wizard'
    
    @api.depends('inspect_id')
    def _compute_produced(self):
        for line in self:
            move_line = line.inspect_id.moveline_before_ids.filtered(lambda x:x.state == 'produced')
            line.moveline_ids += move_line
    
    
    inspect_id    = fields.Many2one('produksi.inspect', string='Inspect')
    transfer_type = fields.Selection([("new","New"),("exist","Existing")], string='Transfer Type',default="new")
    picking_id    = fields.Many2one('stock.picking', string='Stock Picking')
    moveline_ids  = fields.Many2many(comodel_name='stock.move.line.before', relation='inspect_transfer_wizard_rel',compute="_compute_produced",domain=[('state', '=', 'produced')],string='Details')
    
    

    def do_transfer(self):
        if self.transfer_type == 'new':
            move_line = []
            move_ids = []
            for move in self.moveline_ids:
                rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                uom_quantity = move.product_id.uom_id._compute_quantity(move.quantity, move.product_id.uom_id, rounding_method='HALF-UP')
                uom_quantity = float_round(uom_quantity, precision_digits=rounding)
                
                move_line.append((0,0,{
                    'product_id': move.product_id.id,
                    'lot_id': move.lot_id.id,
                    'grade_id': move.grade_id.id,
                    'lot_name': move.lot_id.name,
                    'product_uom_id': move.product_id.uom_id.id,
                    'grade_id': move.grade_id.id,
                    "location_id":self.inspect_id.production_type_id.inspect_location_id.id,
                    "location_dest_id":self.inspect_id.production_type_id.inspect_location_dest_id.id,
                    'qty_done': uom_quantity,
                    # 'product_uom_qty':uom_quantity,
                    'company_id':self.env.company.id,
                }))
                
                
                move_ids.append((0,0,{
                    'name': self.inspect_id.product_id.name,
                    'date':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'picking_type_id': self.inspect_id.production_type_id.inspect_picking_type_id.id,
                    'product_id': self.inspect_id.product_id.id,
                    "location_id":self.inspect_id.production_type_id.inspect_location_id.id,
                    "location_dest_id":self.inspect_id.production_type_id.inspect_location_dest_id.id,
                    'product_uom': self.inspect_id.product_id.uom_id.id,
                    'product_uom_qty': uom_quantity,
                    'company_id': self.env.company.id,
                    }))
            
            picking = self.env['stock.picking'].create({ 
                'picking_type_id': self.inspect_id.production_type_id.inspect_picking_type_id.id,
                'date': fields.Date.today(),
                'scheduled_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'production_id':self.inspect_id.production_id.id,
                'origin':self.inspect_id.name,
                'inspect_id':self.inspect_id.id,
                "location_id":self.inspect_id.production_type_id.inspect_location_id.id,
                "location_dest_id":self.inspect_id.production_type_id.inspect_location_dest_id.id,
                'immediate_transfer': False,
                'move_line_nosuggest_ids': move_line,
                'move_lines': move_ids,
            })
            
            if picking.id:
                # picking.action_confirm()
                for move in self.inspect_id.moveline_before_ids.filtered(lambda x:x.state == 'produced'):
                    move.write({'state':'transfer'})
                
                return {
                    'name': 'Transfer',
                    'view_mode': "form",
                    'res_model': 'stock.picking',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': picking.id,}