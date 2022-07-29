from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools.float_utils import float_compare, float_is_zero, float_repr, float_round
import logging
_logger = logging.getLogger(__name__)

class MrpDoppingWizard(models.TransientModel):
    _name = 'mrp.dopping.wizard'
    
    
    mrp_id          = fields.Many2one('mrp.production', string='Mrp')
    product_id      = fields.Many2one('product.product', string='Product')
    type_id         = fields.Many2one('mrp.type', string='Order Type')
    date            = fields.Datetime(string='Date')
    type_transfer   = fields.Selection([("in","In"),("out","Out")], string='In/Out')
    type_dopping    = fields.Selection([("pw","PW"),("tfo","TFO"),("vhs","VHS"),("jumbo","Jumbo"),("interlace","Interlace")], string='Type Dopping')
    employee_id     = fields.Many2one('hr.employee', string='Operator',)
    shift           = fields.Selection(selection=[('a', 'A'),('b', 'B'),('c', 'C'),],string='Shift' )
    quantity        = fields.Float(string='Quantity')
    
    def do_transfer(self):
        for rec in self:
            if rec.type_dopping == 'pw':
                component   = rec.type_id.component_location_pw_id
                production  = rec.type_id.location_pw_id
                finished    = rec.type_id.finished_location_pw_id
            elif rec.type_dopping == 'tfo':
                component   = rec.type_id.finished_location_pw_id
                production  = rec.type_id.location_tfo_id
                finished    = rec.type_id.finished_location_tfo_id
            elif rec.type_dopping == 'vhs':
                component   = rec.type_id.finished_location_tfo_id
                production  = rec.type_id.location_vhs_id
                finished    = rec.type_id.finished_location_vhs_id
            elif rec.type_dopping == 'jumbo':
                component   = rec.type_id.finished_location_vhs_id
                production  = rec.type_id.location_jumbo_id
                finished    = rec.type_id.finished_location_jumbo_id
            elif rec.type_dopping == 'interlacce':
                component   = rec.type_id.component_location_id
                production  = rec.type_id.Interlace
                finished    = rec.type_id.finished_location_id

            
            if rec.type_transfer == 'in':
                # Component
                smlb_obj = self.env['stock.move.line.before'].create({
                    'type_dopping'  : rec.type_dopping,
                    'type_transfer' : rec.type_transfer,
                    'production_id' : rec.mrp_id.id,
                    'quantity'      : rec.quantity,
                    'employee_id'   : rec.employee_id.id,
                    'shift'         : rec.shift,
                })

                for line in rec.mrp_id.move_raw_ids:
                    component_sm_obj = self.env['stock.move'].create({
                        # 'move_before_id'    : smlb_obj.id,
                        'date'              : rec.date,
                        'name'              : line.product_id.name,
                        'product_id'        : line.product_id.id,
                        'product_uom_qty'   : rec.quantity,
                        'product_uom'       : line.product_id.uom_id.id,
                        'location_id'       : component.id,
                        'location_dest_id'  : production.id,
                    })
                    component_sml_obj = self.env['stock.move.line'].create({
                        'production_id'     : rec.mrp_id.id,
                        'move_id'           : component_sm_obj.id,
                        'date'              : rec.date,
                        'lot_id'            : line.lot_id.id,
                        'product_id'        : line.product_id.id,
                        'qty_done'          : rec.quantity,
                        'product_uom_qty'   : rec.quantity,
                        'product_uom_id'    : line.product_id.uom_id.id,
                        'location_id'       : component.id,
                        'location_dest_id'  : production.id,
                    })

            else:
                smlb_obj = self.env['stock.move.line.before'].create({
                    'type_dopping'  : rec.type_dopping,
                    'type_transfer' : rec.type_transfer,
                    'production_id' : rec.mrp_id.id,
                    'quantity'      : rec.quantity,
                    'employee_id'   : rec.employee_id.id,
                    'shift'         : rec.shift,
                })


                # Finished
                for line in rec.mrp_id.move_raw_ids:
                    finished_sm_obj = self.env['stock.move'].create({
                        'move_before_id'    : smlb_obj.id,
                        'date'              : rec.date,
                        'name'              : line.product_id.name,
                        'product_id'        : line.product_id.id,
                        'product_uom_qty'   : rec.quantity,
                        'product_uom'       : line.product_id.uom_id.id,
                        'location_id'       : production.id,
                        'location_dest_id'  : finished.id,
                    })
                    finished_sml_obj = self.env['stock.move.line'].create({
                        'production_id'     : rec.mrp_id.id,
                        'move_id'           : finished_sm_obj.id,
                        'date'              : rec.date,
                        'lot_id'            : line.lot_id.id,
                        'product_id'        : line.product_id.id,
                        'qty_done'          : rec.quantity,
                        'product_uom_qty'   : rec.quantity,
                        'product_uom_id'    : line.product_id.uom_id.id,
                        'location_id'       : production.id,
                        'location_dest_id'  : finished.id,
                    })