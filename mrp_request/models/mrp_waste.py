from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpWasteCategory(models.Model):
    _name = 'mrp.waste.category'

    name        = fields.Char(string='Name',required=True, )
    is_active   = fields.Boolean(string='Is Active',default=True)
    description = fields.Text(string='Description')





class MrpWaste(models.Model):
    _name = 'mrp.waste'

    name              = fields.Char(string='Waste')
    workorder_line_id = fields.Many2one('mrp.workorder.line', string='Workorder Line')
    workorder_id      = fields.Many2one('mrp.workorder', string='Workorder',related="workorder_line_id.workorder_id")
    production_id     = fields.Many2one('mrp.production', string='Production',related="workorder_id.production_id")
    waste_categ_id    = fields.Many2one('mrp.waste.category', string='Category',required=True, )
    product_id        = fields.Many2one('product.product', string='Product',required=True, )
    product_uom_qty   = fields.Float(string='Quantity')
    uom_id            = fields.Many2one('uom.uom', string='Satuan',related="product_id.uom_id")
    
