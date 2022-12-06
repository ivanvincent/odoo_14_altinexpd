from odoo import models, fields, api

class WorkorderFat(models.Model):
    _name = 'workorder.fat'

    defect_id = fields.Many2one('product.defect', string='Defect')
    quantity = fields.Float(string='Qty')
    workorder_line_id = fields.Many2one('mrp.workorder.line', 'Workorder')