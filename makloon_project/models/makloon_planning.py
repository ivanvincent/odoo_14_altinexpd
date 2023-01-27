from collections import namedtuple
import json
import time
from datetime import datetime

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
# from odoo.addons.procurement.models import procurement
from odoo.exceptions import UserError


class MakloonPlanning(models.Model):

    _name = "makloon.planning"

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return warehouse_ids



    # # @api.multi
    @api.depends("stage_ids")
    def _get_makloon_order(self):
        self.mako_ids = False
        mako_data = self.env['makloon.order'].search([('planning_id','=',  self.id)])
        if mako_data:
            self.mako_ids = mako_data


    # # @api.multi
    @api.depends("mako_ids")
    def _get_mako_count(self):
        self.mako_count = 0
        if self.mako_ids:
            self.mako_count= len(self.mako_ids)

    name = fields.Char("Name", default="New", required=True)
    date = fields.Date("Date Planning")
    due_date = fields.Date("Due Date")
    stage_ids = fields.One2many("makloon.planning.stage", "planning_id", "Makloon Stages")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id.id)
    mako_ids = fields.One2many("makloon.order", string="Makloon Order", compute="_get_makloon_order")

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True,
        default=_default_warehouse_id)

    mako_count = fields.Integer("Mako Count", compute="_get_mako_count")
    desc = fields.Text("Planning Description")
    sale_id = fields.Many2one('sale.order', string='No SO')




    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('makloon.planning') or 'New'
        return super(MakloonPlanning, self).create(vals)


class MakloonPlanningStage(models.Model):

    _name = "makloon.planning.stage"

    # # # @api.multi
    # @api.depends("operation_id", "planning_id")
    # def _find_next_stage(self):
    #     self.next_stage = False
    #     next_stg = self.env['makloon.planning.stage'].search([('planning_id','=', self.planning_id)])
    #     if next_stg:
    #         for nx in next_stg:
    #             if nx.operation_id.sequence > self.operation_id.sequence:
    #                 self.next_stage = nx.id


    # # @api.multi
    @api.depends('order_ids')
    def _get_makloon_progress(self):
        self.progress = 0.0
        result_planning = 0.0
        result_done = 0.0
        if self.order_ids:
            for oi in self.order_ids:
                for rp in oi.result_ids:
                    result_planning += rp.product_uom_qty
                for rd in oi.stock_result_done_pack_ids:
                    result_done += rd.qty_done

        if result_done != 0.0 and result_planning != 0.0:
            self.progress = (result_done/result_planning)*100


    name = fields.Char("Name", required=True)
    planning_id = fields.Many2one("makloon.planning")
    partner_id = fields.Many2one("res.partner", "Makloon Company",  required=True)
    operation_id = fields.Many2one("makloon.operation", string="Operation")
    state = fields.Selection([('draft', 'Draft'),('process', 'Process'), ('done','Done'),('cancel','Cancel')], string="State", default="draft")
    # next_stage = fields.Many2one("makloon.planning.stage", string="Next Stage", compute="_find_next_stage")
    progress = fields.Float('Makloon Progress', compute="_get_makloon_progress")
    first_stage = fields.Boolean("First Stage", default=False)
    last_stage = fields.Boolean("Last Stage",default=False)
    order_ids = fields.One2many('makloon.order', 'stage_id', "Makloon Order List")
    company_id = fields.Many2one('res.company', 'Company', related="planning_id.company_id")
    production_loc = fields.Many2one('stock.location', 'Production Location', domain=[('usage', '=', 'production')])


    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     location_prod_id = self.env['stock.location'].search(
    #         [('usage', '=', 'production'), ('partner_id', '=', self.partner_id.id)])
    #     if location_prod_id:
    #         if len(location_prod_id)>1:
    #             self.production_loc = location_prod_id[0].id
    #         else:
    #             self.production_loc = location_prod_id.id
    #     else:
    #         self.production_loc = False

    @api.onchange("operation_id")
    def onchange_operation_id(self):
        self.name = self.operation_id.name


    # @api.multi
    def create_makloon_order(self):
        self.ensure_one()
        mak_order = self.env['makloon.order']
        data = {
            # 'name':'/',
            'partner_id': self.partner_id.id,
            'origin': self.planning_id.name,
            'stage_id':self.id,
            'type': 'out',
            'warehouse_id': self.planning_id.warehouse_id.id,
            'production_loc': self.production_loc.id,
            'material_ids': [(0, 0, 
                {
                    'product_id': sale.product_id.id,
                    'no_po': self.planning_id.source_po.name,
                    'product_uom_qty': sale.product_uom_qty,
                    'product_uom': sale.product_uom.id,
                })
            for sale in self.planning_id.sale_id.order_line],
            'result_ids':  [(0, 0, 
                {
                    'product_id': sale.product_id.id,
                    'product_uom_qty': sale.product_uom_qty,
                    'product_uom': sale.product_uom.id,
                    'service_product_id': self.env['product.product'].search([('name', '=', 'Biaya Makloon')]).id,
                    'price_unit': sale.product_id.standard_price,
                })
            for sale in self.planning_id.sale_id.order_line],

        }
        mak_order.create(data)
        self.state="process"
        self.action_view_makloon_order()


        # return True

    # @api.multi
    def action_view_makloon_order(self):

        action = self.env.ref('makloon_project.action_makloonorder_list').read()[0]

        orders = self.mapped('order_ids')
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders.ids)]
        elif orders:
            action['views'] = [(self.env.ref('makloon_project.view_makloon_order_form').id, 'form')]
            action['res_id'] = orders.id
        return action

    # @api.multi
    def mark_as_done(self):
        self.ensure_one()
        if self.order_ids:
            for order in self.order_ids:
                if order.state !='done':
                    return False

        self.state='done'
        return True