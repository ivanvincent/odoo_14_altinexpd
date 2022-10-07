from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = 'stock.move'

    # # @api.multi
    # def create_picking_list(self):
    #     self.ensure_one()
    #     picking_list = self.env['makloon.picking.list']
    #     data = {
    #         'picking_id': self.picking_id.id,
    #         'product_id': self.product_id.id
    #     }
    #     picking_list.create(data)
    #     print data
    #
    # # @api.multi
    # def action_picking_list(self):
    #     # tree_view_id = self.env.ref('hr.view_employee_tree').ids
    #     # [tree_view_id, 'tree'],
    #     picking_list = self.env['makloon.picking.list'].search([('picking_id','=',self.picking_id.id),('product_id','=',self.product_id.id)])
    #     print 'picking_list=>',len(picking_list), picking_list
    #     if len(picking_list)==0:
    #         self.create_picking_list()
    #         print 'picking_list=>', len(picking_list), picking_list
    #     form_view_id = self.env.ref('tj_makloon_custom.view_wizard_tj_makloon_custom_picking_list').ids
    #     context = {
    #         'picking_id': [picking_list.picking_id.id],
    #         'product_id': [picking_list.product_id.id],
    #         'picking_list': picking_list.picking_list.ids,
    #         'active_ids': [picking_list.id],
    #                }
    #     print context
    #     return {
    #         'name': 'Picking List',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'views': [[form_view_id, 'form']],
    #         'res_model': 'makloon.picking.list',
    #         'type': 'ir.actions.act_window',
    #         'target': 'new',
    #         'context': context,
    #     }
        # action = self.env.ref('makloon_project.action_makloonorder_list').read()[0]
        #
        # orders = self.mapped('order_ids')
        # if len(orders) > 1:
        #     action['domain'] = [('id', 'in', orders.ids)]
        # elif orders:
        #     action['views'] = [(self.env.ref('tj_makloon_custom.view_wizard_tj_makloon_custom_picking_list').id, 'form')]
        #     action['res_id'] = orders.id
        # return action
        # return {
        #     'name': 'Purchase Wizard',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'my.wizard',
        #     'res_id': wizard_id,
        #     'type': 'ir.actions.act_window',
        #     'target': 'new',
        #     'context': context,
        # }

        # action = self.env.ref('view_wizard_tj_makloon_custom_picking_list').read()[0]
        # orders = self.mapped('picking_list')
        # if len(orders) > 1:
        #     action['domain'] = [('id', 'in', orders.ids)]
        # elif orders:
        #     action['views'] = [(self.env.ref('view_wizard_tj_makloon_custom_picking_list').id, 'form')]
        #     action['res_id'] = orders.id
        # return action