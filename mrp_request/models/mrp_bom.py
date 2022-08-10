from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    
    operation_template_id = fields.Many2one('mrp.operation.template', string='Operation Template')
    
    @api.onchange('operation_template_id')
    def _get_operations(self):
        operation_ids = []
        self.operation_ids = False
        for line in self.operation_template_id.line_ids:
            operation_ids+= [(0,0,{'name':line.workcenter_id.name,'template_line_id':line.id,'workcenter_id':line.workcenter_id.id,'machine_id':line.machine_id.id})]
        self.operation_ids = operation_ids
   

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'
    
    machine_id       = fields.Many2one('mrp.machine', string='Machine')
    template_line_id = fields.Many2one('mrp.operation.template.line', string='Template Line')
    parameter_ids    = fields.One2many('mrp.operation.template.line.parameter', string='Parameters',related="template_line_id.parameter_ids")

