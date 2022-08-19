from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpOperationTemplate(models.Model):
    _name = 'mrp.operation.template'

    name        = fields.Char(string='Template name')
    description = fields.Text(string='Description')
    line_ids    = fields.One2many('mrp.operation.template.line', 'template_id', 'Details')
    product_id  = fields.Many2one('product.product', string='Product')
    
    
    
    
class MrpOperationTemplateLine(models.Model):
    _name = 'mrp.operation.template.line'
    
    sequence      = fields.Integer(string='No',compute="_get_sequence")
    template_id   = fields.Many2one('mrp.operation.template', 'Template')
    workcenter_id = fields.Many2one('mrp.workcenter', string='Workcenter')
    machine_id    = fields.Many2one('mrp.machine', string='Machine')
    parameter_ids = fields.One2many('mrp.operation.template.line.parameter', 'line_id', 'Parameters')
    
    def _get_sequence(self):
        seq = 0
        for line in self:
            seq +=1
            line.sequence = seq
    
    def action_open_parameters(self):
        view = self.env.ref('mrp_request.mrp_operation_template_parameter_view_form')
        
        return {
            'name': _('Parameters'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mrp.operation.template.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
            ),
        }



class MrpOperationTemplatelineParameter(models.Model):
    _name = 'mrp.operation.template.line.parameter'
    
    sequence      = fields.Integer(string='No',compute="_get_sequence")
    line_id      = fields.Many2one('mrp.operation.template.line', string='Line')
    template_id  = fields.Many2one(related='line_id.template_id', string='Template')
    parameter_id = fields.Many2one('mrp.parameter', string='Parameter')
    factor       = fields.Float(string='Factor')
    uom_id = fields.Many2one(comodel_name='uom.uom',related="parameter_id.uom_id",string='Uom')
    mrp_operation_template_line_parameter_tool_ids = fields.One2many('mrp.operation.template.line.parameter.tool', 'template_line_parameter_id', 'Tool Line')
    machine_id = fields.Many2one('mrp.machine', string='Machine')
    
    def _get_sequence(self):
        seq = 0
        for line in self:
            seq +=1
            line.sequence = seq

    def action_open_tools(self):
        view = self.env.ref('mrp_request.mrp_operation_template_line_parameter_form')
        
        return {
            'name': _('Tools'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mrp.operation.template.line.parameter',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
            ),
        }
class MrpOperationTemplateLineParameterTool(models.Model):
    _name = 'mrp.operation.template.line.parameter.tool'

    sequence      = fields.Integer(string='No',compute="_get_sequence")
    product_id = fields.Many2one('product.product', string='Tools')
    qty = fields.Float(string='Qty')
    template_line_parameter_id = fields.Many2one('mrp.operation.template.line.parameter', 'Tools')

    def _get_sequence(self):
        seq = 0
        for line in self:
            seq +=1
            line.sequence = seq