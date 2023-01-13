from odoo import fields, models, api, _
from odoo.exceptions import UserError

class MakeOrderWizard(models.TransientModel):
    _name = 'make.order.wizard'

    detail_ids = fields.One2many('make.order.detail.wizard', 'make_order_id', 'Line')

    def action_make(self):
        print('action_make')

    def default_get(self,fields):
        ctx = self.env.context
        mr_obj = self.env['mrp.request'].browse(ctx.get('active_id'))
        result = super(MakeOrderWizard, self).default_get(fields)
        result.update({
                'detail_ids': [(0, 0, {'product_id': d.product_id.id, 'quantity': d.qty_produce}) for d in mr_obj.line_ids]
            })
        return result

class MakeOrderDetailWizard(models.TransientModel):
    _name = 'make.order.detail.wizard'

    product_id = fields.Many2one('product.product', string='Product')
    quantity   = fields.Float(string='Quantity')
    make_order_id = fields.Many2one('make.order.wizard', 'Make Order')
