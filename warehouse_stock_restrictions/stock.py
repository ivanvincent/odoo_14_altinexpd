# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning

class ResUsers(models.Model):
    _inherit = 'res.users'

    restrict_locations = fields.Boolean('Restrict Location')

    stock_location_ids = fields.Many2many(
        'stock.location',
        'location_security_stock_location_users',
        'user_id',
        'location_id',
        'Stock Locations')

    stock_location_dest_ids = fields.Many2many(
        'stock.location',
        'location_security_stock_location_dest_users',
        'user_id',
        'location_dest_id',
        'Stock Dest Locations',
        # compute="_compute_stock_location_dest_ids"
        )

    default_picking_type_ids = fields.Many2many(
        'stock.picking.type', 'stock_picking_type_users_rel',
        'user_id', 'picking_type_id', string='Default Warehouse Operations')
    
    default_warehouse_ids = fields.Many2many(
        'stock.warehouse', 'stock_warehouse_users_rel',
        'user_id', 'warehouse_id', string='Default Warehouse Operations')

    default_dest_warehouse_ids = fields.Many2many(
        'stock.warehouse', 'stock_destination_warehouse_users_rel', string='Default Destination Warehouse Operations')
    
    default_journal_ids = fields.Many2many('account.journal', string='Access Journal')

    @api.onchange('default_warehouse_ids')
    def _onchange_warehouse_id(self):
        data = self.env['stock.picking.type']
        print(self.default_warehouse_ids.ids)
        needed = data.search([('active','=',True),('warehouse_id','in',self.default_warehouse_ids.ids)]).ids
        print(needed)
        self.default_picking_type_ids = needed

    @api.depends('default_warehouse_ids')
    @api.onchange('default_warehouse_ids')
    # def _compute_stock_location_dest_ids(self):
    def _onchange_stock_location_dest_ids(self):
        for rec in self:
            dft_loc = self.default_warehouse_ids.mapped('lot_stock_id.location_id.id')
            if len(dft_loc) != 0:
                location_parent_ids = dft_loc
                location_ids = self.env['stock.location'].search([('location_id', 'in', location_parent_ids)]).ids
                rec.stock_location_dest_ids = [(6, 0, location_ids)]
            else:
                rec.stock_location_dest_ids = False


class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.constrains('state', 'location_id', 'location_dest_id')
    def check_user_location_rights(self):
        # self.ensure_one()
        for a in self:
            if a.state == 'draft':
                return True
            user_locations = a.env.user.stock_location_ids
            print(user_locations)
            print("Checking access %s" %a.env.user.default_picking_type_ids)
            if a.env.user.restrict_locations:
                message = _(
                    'Invalid Location. You cannot process this move since you do '
                    'not control the location "%s". '
                    'Please contact your Adminstrator.')
                if a.location_id not in user_locations:
                    raise Warning(message % a.location_id.name)
                elif a.location_dest_id not in user_locations:
                    raise Warning(message % a.location_dest_id.name)


