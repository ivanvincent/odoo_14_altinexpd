from odoo import models, fields, api, _
from odoo.exceptions import UserError
from ast import literal_eval

from random import randint

class PurchaseOrderCategory(models.Model):
    _name = 'purchase.order.category'

    def _get_default_color(self):   
        return randint(1, 11)
    
    name                 = fields.Char(string='PO Category')
    # picking_type_id      = fields.Many2one('stock.picking.type', string='Picking Type')
    color                = fields.Integer(string='Color Index', default=_get_default_color)
    description          = fields.Text(string='Description')
    sequence_id          = fields.Many2one('ir.sequence', string='Sequence')
    product_category_ids = fields.Many2many(comodel_name='product.category',relation='purchase_product_category_rel',column1='product_categ_id',column2='po_categ_id',string='Product Category' )
    picking_type_ids     = fields.Many2many('stock.picking.type', column1='picking_type_id', string='Picking Type Ids')
    
    
    
    


    def _get_action(self, action_xmlid):
        action = self.env["ir.actions.actions"]._for_xml_id(action_xmlid)
        if self:
            action['display_name'] = self.display_name
        context = {
            'default_purchase_category_id': self.id,
            'default_picking_type_id': self.picking_type_id.id,
        }

        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        action['domain'] = [('purchase_category_id', '=', self.id)]
        return action

    
    def open_purchase_order(self):
        return self._get_action('inherit_purchase_order.purchase_rfq_view_action')