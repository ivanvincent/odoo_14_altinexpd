from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = 'stock.move'

    image_ids   = fields.One2many('stock.move.image', 'move_id', string='Image')
    supplier_id = fields.Many2one('res.partner', string='Supplier', compute="_compute_supplier_id")
    just_flag = fields.Boolean(string='Flag ?', store=False,) #Flag For Change Domain Product
    qty_onhand = fields.Float(string='On Hand', compute="_compute_qty_onhand")
    sat_line_ids = fields.One2many('stock.move.sat', 'stock_move_id', 'Line')

    def action_show_image(self):
        action = self.env.ref('inherit_inventory.stock_move_action').read()[0]
        action['res_id'] = self.id
        action['name'] = "Images of %s" % (self.product_id.name)
        return action
    
    def _compute_supplier_id(self):
        for rec in self:
            supplier_ids = rec.move_line_ids.mapped('supplier_id.id')
            rec.supplier_id = list(set(supplier_ids))[0] if len(supplier_ids) > 0 else False

    @api.onchange('just_flag')
    def _onchange_just_flag(self):
        """
            User id 2 = Administrator
        """
        user = self.env.user.id
        if user != 2:
            res = {}
            categ_ids = [category.id  for warehouse in self.env.user.default_warehouse_ids for category in warehouse.product_category_ids ] #settingan ada di user (res.users)
            res['domain'] = {'product_id': [('categ_id', 'in', categ_ids)]}
            return res
    
    @api.depends('product_id')
    def _compute_qty_onhand(self):
        for rec in self:
            quant = self.env['stock.quant'].search([('product_id', '=', rec.product_id.id),
                ('location_id', '=', rec.location_id.id)
                ])
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning('='*40)
            _logger.warning('QUANT')
            _logger.warning(sum(quant.mapped('quantity')))
            _logger.warning('='*40)
            # rec.qty_onhand = sum(quant.mapped('quantity'))
            rec.qty_onhand = sum(quant.mapped('quantity'))

    @api.model
    def create(self, values):
        product_id = values.get('product_id')
        if product_id:
            values['product_uom'] = self.env['product.product'].browse(product_id).uom_id.id
        result = super(StockMove, self).create(values)
        return result

    def stock_move_fat_action(self):
        action = self.env.ref('inherit_inventory.stock_move_fat_action').read()[0]
        action['res_id'] = self.id
        return action
