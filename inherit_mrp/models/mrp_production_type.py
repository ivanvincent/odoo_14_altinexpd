from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Mrp(models.Model):
    _name = 'mrp.type'

    name                               = fields.Char(string='Manufacturing Type',required=True, )
    code                               = fields.Char(string='Code')
    request_sequence_id                = fields.Many2one('ir.sequence', string='Request Sequence', required=True, )
    production_sequence_id             = fields.Many2one('ir.sequence', string='Production Sequence', required=True, )
    picking_type_id                    = fields.Many2one('stock.picking.type', string='Operation Type',domain=[('code', '=', 'mrp_operation')],required=True, )
    shrinkage_ids                      = fields.Many2many(comodel_name='mrp.shrinkage', string='Shrinkage')
    component_location                 = fields.Many2one('stock.location', string='Component Location',domain="[('usage','=','internal')]",required=True, )
    finished_location                  = fields.Many2one('stock.location', string='Finished Location',domain="[('usage','=','internal')]",required=True, )
    component_chemical_location        = fields.Many2one('stock.location', string='Chemical Location',domain="[('usage','=','internal')]", )
    component_greige_location          = fields.Many2one('stock.location', string='Greige Location',domain="[('usage','=','internal')]")
    component_greige_picking_type_id   = fields.Many2one('stock.picking.type', string='Greige Operation Type')
    component_chemical_picking_type_id = fields.Many2one('stock.picking.type', string='Chemical Operation Type')
    picking_type_finished_id           = fields.Many2one('stock.picking.type', string='Picking Type Finished')

    # Twisting
    component_location_pw_id        = fields.Many2one('stock.location', string='Component PW')
    location_pw_id                  = fields.Many2one('stock.location', string='PW')
    finished_location_pw_id         = fields.Many2one('stock.location', string='Finished PW')
    location_tfo_id                 = fields.Many2one('stock.location', string='TFO')
    finished_location_tfo_id        = fields.Many2one('stock.location', string='Finished TFO')
    location_vhs_id                 = fields.Many2one('stock.location', string='VHS')
    finished_location_vhs_id        = fields.Many2one('stock.location', string='Finished VHS')
    location_jumbo_id               = fields.Many2one('stock.location', string='Jumbo')
    finished_location_jumbo_id      = fields.Many2one('stock.location', string='Finished Jumbo')
    location_interlace_id           = fields.Many2one('stock.location', string='Interlace')

    allowed_over_qty_percentage     = fields.Float(string='Allowed Over Quantity')
    
    component_product_category_ids  = fields.Many2many('product.category', 'component_product_category_rel','mrp_type_id', string='Component Product Category')
    component_chemical_category_ids = fields.Many2many('product.category', 'component_chemical_category_rel','mrp_type_id', string='Component Chemical Category')
    finished_product_category_ids   = fields.Many2many('product.category', 'finished_product_category_rel','mrp_type_id', string='Finished Product Category')
    

class MrpShrinkage(models.Model):
    _name = 'mrp.shrinkage'
    
    
    name       = fields.Char(string='Shrinkage')
    percentage = fields.Float(string='Percentage')
    
    
    def name_get(self):
        result = []
        for shrinkage in self:
            result.append((shrinkage.id, str(shrinkage.percentage)))
        return result
    
    
    