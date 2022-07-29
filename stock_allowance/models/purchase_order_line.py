from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    allowance          = fields.Float(string='Allowance', related='product_id.allowance')
    quantity_allowance = fields.Float(string='Quantity Allowance', compute='get_quantity_allowance',)
    
    @api.depends('product_qty')
    def get_quantity_allowance(self):
        for rec in self:
            rec.quantity_allowance = rec.product_qty + (rec.product_qty * rec.allowance / 100)

    
    # @api.depends('product_uom', 'quantity_allowance', 'product_id.uom_id')
    # def _compute_product_uom_qty(self):
    #     for line in self:
    #         line
    #         if line.product_id and line.product_id.uom_id != line.product_uom:
    #             line.product_uom_qty = line.product_uom._compute_quantity(line.quantity_allowance, line.product_id.uom_id)
    #         else:
    #             line.product_uom_qty = line.quantity_allowance