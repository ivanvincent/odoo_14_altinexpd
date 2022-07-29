from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Machine(models.Model):
    _inherit = 'mrp.machine'
    
    
    mrp_type_id = fields.Many2one('mrp.type', string='Production Type')
    
       
    @api.depends('mrp_type_id')
    def _compute_production(self):
        for machine in self:
            mrp_ids = self.env['mrp.production'].search([('type_id','=',2),('mesin_id','=',machine.id)])
            machine.mrp_ids = mrp_ids.ids
            machine.production_count = len(mrp_ids)
        
    
    
    mrp_ids = fields.Many2many(
        comodel_name='mrp.production', 
        string='Production',
        compute="_compute_production"
        )
    
    production_count = fields.Integer(compute='_compute_production', string='Production Count', store=False)
    

    

    