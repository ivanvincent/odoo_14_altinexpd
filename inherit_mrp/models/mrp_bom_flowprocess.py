from odoo import models, fields, api

class MrpBomFlowprocessLine(models.Model):
    _name = 'mrp.bom.flowprocess'

    proses_master_id = fields.Many2one('master.proses', string='Process')
    no_urut = fields.Integer(string='No urut')
    mesin_id = fields.Many2one('mrp.machine', string='Mesin')
    process_type_id = fields.Many2one('process.type', string='Process Type')
    parameter_ids = fields.One2many('bom.parameter.line', 'flowprocess_line_id', string='Parameter Line')
    chemical_ids = fields.One2many('bom.chemical.line', 'flowprocess_line_id', string='Chemical Line')
    bom_id = fields.Many2one('mrp.bom', string='Bom')

    price = fields.Float(string='Price',
    compute="_compute_master_process"
    )
    description_process = fields.Text(string='Description',
    compute="_compute_master_process"
    )

    def _compute_master_process(self):
        for rec in self:
            if rec.proses_master_id:
                rec.price = rec.proses_master_id.price
                rec.description_process = rec.proses_master_id.description
            else:
                rec.price = 0
                rec.description_process = 0

class BomParameterLine(models.Model):
    _name = 'bom.parameter.line'

    no_urut = fields.Integer(string='No Urut')
    parameter_id = fields.Many2one('master.parameter', string='Parameter')
    qty_plan = fields.Float(string='Plan')
    qty_actual = fields.Float(string='Actual')
    uom_id = fields.Many2one('uom.uom', string='Uom')
    flowprocess_line_id = fields.Many2one('mrp.bom.flowprocess', string='Flowprocess')

class BomChemicalLine(models.Model):
    _name = 'bom.chemical.line'

    no_urut = fields.Integer(string='No Urut')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one('uom.uom', string='Uom')
    flowprocess_line_id = fields.Many2one('mrp.bom.flowprocess', string='Flowprocess')