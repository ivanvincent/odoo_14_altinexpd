from odoo import models, fields, api

class MasterFlowprocess(models.Model):
    _name = 'master.flowprocess'

    name = fields.Char(string='Name')
    flowprocess_line_ids = fields.One2many('master.flowprocess.line', 'master_flowprocess_id', string='Flowprocess Line')
    workcenter_name = fields.Char(string='Workcenter', compute='_compute_workcenter_name')

    def _compute_workcenter_name(self):
        for rec in self:
            rec.workcenter_name = ', '.join(rec.flowprocess_line_ids.mapped('workcenter_id.name'))


class MasterFlowprocessLine(models.Model):
    _name = 'master.flowprocess.line'

    workcenter_id = fields.Many2one('mrp.workcenter', string='Workcenter')
    no_urut = fields.Integer(string='No urut')
    mesin_id = fields.Many2one('mrp.machine', string='Mesin')
    process_type_id = fields.Many2one('process.type', string='Process Type')
    parameter_ids = fields.One2many('flowprocess.parameter.line', 'flowprocess_line_id', string='Parameter Line')
    chemical_ids = fields.One2many('flowprocess.chemical.line', 'flowprocess_line_id', string='Chemical Line')
    master_flowprocess_id = fields.Many2one('master.flowprocess', string='Flowprocess')
    bom_id = fields.Many2one('mrp.bom', string='Bom')

    price = fields.Float(string='Price',
    # compute="_compute_master_process"
    )
    description_process = fields.Text(string='Description',
    # compute="_compute_master_process"
    )

    # def _compute_master_process(self):
    #     for rec in self:
    #         if rec.proses_master_id:
    #             rec.price = rec.proses_master_id.price
    #             rec.description_process = rec.proses_master_id.description

class FlowprocessParameterLine(models.Model):
    _name = 'flowprocess.parameter.line'

    no_urut = fields.Integer(string='No Urut')
    parameter_id = fields.Many2one('master.parameter', string='Parameter',required=True, )
    qty_plan = fields.Float(string='Plan')
    plan = fields.Char(string='Plan')
    qty_actual = fields.Char(string='Actual')
    uom_id = fields.Many2one('uom.uom', string='Uom')
    flowprocess_line_id = fields.Many2one('master.flowprocess.line', string='Flowprocess')

class FlowprocessChemicalLine(models.Model):
    _name = 'flowprocess.chemical.line'

    no_urut = fields.Integer(string='No Urut')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one('uom.uom', string='Uom')
    flowprocess_line_id = fields.Many2one('master.flowprocess.line', string='Flowprocess')