from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpProductionType(models.Model):
    _name = 'mrp.production.type'

    name                   =   fields.Char(string='Production Type',required=True, )
    component_category_ids = fields.Many2many(comodel_name='product.category', relation='component_category_rel',string='Components Category',required=True, )
    finished_category_ids  = fields.Many2many(comodel_name='product.category', relation='finished_category_rel',string='Finished Category',required=True, )
    picking_type_id        = fields.Many2one('stock.picking.type', string='Picking Type',domain=[('code', '=', 'mrp_operation')])
    sequence_id            = fields.Many2one('ir.sequence', string='Sequence',required=True, )
    # Request Bahan Baku
    picking_type_request_material_id = fields.Many2one('stock.picking.type', string='Operation Type Request Material')
    picking_type_finished_id = fields.Many2one('stock.picking.type', string='Picking Type Finished')