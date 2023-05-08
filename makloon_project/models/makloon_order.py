from collections import namedtuple
import json
import time

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
# from odoo.addons.procurement.models import procurement
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp

class MakloonOrder(models.Model):
    _name = 'makloon.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description="Makloon Order"


    # @api.one
    @api.depends('picking_ids')
    def _get_stock_move(self):
        self.stock_production_ids = False
        self.stock_result_ids = False
        sp_ids = []
        sr_ids = []

        if self.picking_ids:
            for pc in self.picking_ids:
                for mv in pc.move_lines:
                    if pc.picking_type_id.code=="outgoing" and mv.location_dest_id.usage=='production':
                        self.sp_ids.append(mv.id)
                    elif pc.picking_type_id.code=="incoming" and mv.location_id.usage=='production':
                        self.sr_ids.append(mv.id)

            self.stock_production_ids = sp_ids
            self.stock_result_ids = sr_ids


    # @api.one
    @api.depends('picking_ids')
    def _get_process_pack(self):
        self.stock_production_progress_pack_ids = False
        self.stock_result_progress_pack_ids = False
        spp_ids = []
        srp_ids = []
        material_ids = [x.product_id.id for x in self.material_ids]
        result_ids = [x.product_id.id for x in self.result_ids]
        if self.picking_ids:
            for pc in self.picking_ids:

                for pack in pc.move_ids_without_package:
                    if pc.picking_type_id.code == "outgoing" and pack.location_dest_id.usage == 'production':
                        if pack.state != 'done' and pack.product_id.id in material_ids:
                            spp_ids.append(pack.id)
                    elif pc.picking_type_id.code == "incoming" and pack.location_id.usage == 'production':
                        if pack.state != 'done' and pack.product_id.id in result_ids:
                            srp_ids.append(pack.id)

        if spp_ids:
            self.stock_production_progress_pack_ids = spp_ids
        if srp_ids:
            self.stock_result_progress_pack_ids = srp_ids

    # @api.one
    @api.depends('picking_ids')
    def _get_done_pack(self):
        self.stock_production_done_pack_ids = False
        self.stock_result_done_pack_ids = False
        spd_ids = []
        srd_ids = []
        material_ids = [x.product_id.id for x in self.material_ids]
        result_ids = [x.product_id.id for x in self.result_ids]
        if self.picking_ids:
            if material_ids and result_ids:
                for pc in self.picking_ids:
                    for pack in pc.move_ids_without_package:
                        if pc.picking_type_id.code == "outgoing" and pack.location_dest_id.usage == 'production':
                            if pack.state == 'done' and pack.product_id.id in material_ids:
                                spd_ids.append(pack.id)
                        elif pc.picking_type_id.code == "incoming" and pack.location_id.usage == 'production':
                            if pack.state == 'done' and pack.product_id.id in result_ids:
                                srd_ids.append(pack.id)
        if spd_ids:
            self.stock_production_done_pack_ids = spd_ids
        if srd_ids:
            self.stock_result_done_pack_ids = srd_ids

    # @api.one
    @api.depends('picking_ids')
    def _get_return_pack(self):
        # pack_return_ids = self.env['stock.pack.operation'].search([
        #     ('picking_id.makloon_order_id','=',self.id),
        #     ('picking_id.picking_type_id.code','=','outgoing'),
        #     ('location_id.usage','=','production'),
        # ])
        # self.stock_material_return_pack_ids = pack_return_ids and pack_return_ids.ids or False
        self.stock_material_return_pack_ids = False

    # @api.one
    @api.depends('picking_ids')
    def _get_return_result_pack(self):
        # stock_result_return_pack_ids = self.env['stock.pack.operation'].search([
        #     ('picking_id.makloon_order_id','=',self.id),
        #     ('picking_id.picking_type_id.code','=','incoming'),
        #     ('location_id.usage','=','internal'),
        # ])
        # self.stock_result_return_pack_ids = stock_result_return_pack_ids and stock_result_return_pack_ids.ids or False
        self.stock_result_return_pack_ids = False

    # @api.one
    @api.depends('picking_ids')
    def _get_scrap_product(self):
        self.stock_material_scrap_ids = False
        scrap_ids = []
        material_ids = [x.product_id.id for x in self.material_ids]
        if self.picking_ids:
            if material_ids:
                for pc in self.picking_ids:
                    for mov in pc.move_lines:
                        if mov.location_dest_id.usage == 'inventory':
                            if mov.state == 'done' and mov.product_id.id in material_ids:
                                scrap_ids.append(mov.id)
        if scrap_ids:
            self.stock_material_scrap_ids = scrap_ids


    # # @api.one
    # @api.depends('picking_ids')
    # def _compute_state(self):
    #     done_state={'done':0, 'not_done':0}
    #     if not self.picking_ids:
    #         self.state="draft"
    #     else:
    #
    #         if self.picking_out_count>0 and self.picking_in_count==0:
    #             self.state="confirm"
    #
    #         elif self.picking_in_count>0 and self.picking_out_count>0:
    #             self.state="process"
    #
    #         else:
    #             for pc in self.picking_ids:
    #                 if pc.state <> 'done':
    #                     done_state['not_done'] +=1
    #                 elif pc.state=='done':
    #                     done_state['done'] +=1
    #             if done_state['not_done'] <> 0:
    #                 self.state='process'
    #             elif done_state['done']<> 0 and done_state['not_done']==0:
    #                 self.state='done'

    # @api.one
    @api.depends('picking_ids')
    def _compute_picking(self):
        pick_out = 0
        pick_in = 0
        if self.picking_ids:
            for pc in self.picking_ids:
                if pc.picking_type_id.code=='outgoing':
                    pick_out +=1
        #         if pc.picking_type_id.code=='incoming':
        #             pick_in +=1
        self.picking_out_count = pick_out 
        picking = self.env['stock.picking'].search([('makloon_order_id', '=', self.id)])
        self.picking_in_count = len(picking)



    # @api.one
    @api.depends('po_ids')
    def _compute_po(self):
        po_cn = 0
        if self.po_ids:
            po_cn =len(self.po_ids)
        self.po_count = po_cn




    name = fields.Char("Number", default="MAKO Number")
    date_order = fields.Datetime(
        'Creation Date',
        default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id.id)
    partner_id = fields.Many2one('res.partner', "Makloon Company")
    origin = fields.Char("Source Document")
    stage_id = fields.Many2one("makloon.planning.stage", "Stage", 
    # related='stage_id.operation_id.purchase_category_id'
    )
    type = fields.Selection([('in', 'Makloon In'), ('out', 'Makloon Out')], string="Makloon Type")

    material_ids = fields.One2many('makloon.order.material', 'order_id', "Material List")
    result_ids = fields.One2many('makloon.order.result', 'order_id', "Result List")

    stock_production_ids = fields.One2many('stock.move', compute="_get_stock_move", string="Production")
    stock_result_ids = fields.One2many('stock.move', compute="_get_stock_move", string="Result")

    stock_production_progress_pack_ids = fields.One2many('stock.pack.operation', compute="_get_process_pack", string="In Progress")
    stock_result_progress_pack_ids = fields.One2many('stock.pack.operation', compute="_get_process_pack", string="In Progress")

    stock_production_done_pack_ids = fields.One2many('stock.pack.operation', compute="_get_done_pack",string="Done")
    stock_result_done_pack_ids = fields.One2many('stock.pack.operation', compute="_get_done_pack", string="Done")

    warehouse_id = fields.Many2one('stock.warehouse', "Source", required=True)
    production_loc = fields.Many2one('stock.location', 'Production Location', domain=[('usage','=','production')])
    state = fields.Selection([('draft','Draft'), ('confirm','Confirmed'),('process','On Process'),('cancel','Cancel'), ('done','Done'), ('close','Close')],
                             string="State", track_visibility='onchange', default="draft" ) #compute="_compute_state"

    picking_ids = fields.One2many('stock.picking', 'makloon_order_id', 'Picking')

    production_pick_ids = fields.One2many('stock.picking', 'makloon_order_id', 'Picking', domain=[('picking_type_id.code','=','outgoing')])
    result_pick_ids = fields.One2many('stock.picking', 'makloon_order_id', 'Picking', domain=[('picking_type_id.code','=','incoming')])

    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    picking_out_count = fields.Integer(compute='_compute_picking', string='Production', default=0)
    picking_in_count = fields.Integer(compute='_compute_picking', string='Result', default=0)

    po_ids = fields.One2many('purchase.order', 'makloon_id', 'Purchase Order')
    po_count = fields.Integer(compute='_compute_po', string='Result', default=0)

    planning_id = fields.Many2one("makloon.planning", related="stage_id.planning_id")

    notes = fields.Text("Notes")

    stock_material_return_pack_ids = fields.One2many('stock.pack.operation', compute="_get_return_pack", string="Material Return")
    stock_result_return_pack_ids = fields.One2many('stock.pack.operation', compute="_get_return_result_pack", string="Result Return")
    stock_material_scrap_ids = fields.One2many('stock.move', compute="_get_scrap_product", string="Valasi/Loss")

    supplier    = fields.Char(string='Supplier')
    product     = fields.Char(string='Product')
    note        = fields.Char(string='Note')

    # @api.multi
    def _create_sequence_mo(self):
        me = self[0]

        if me.name == 'MAKO Number':
            obj_sequence = self.env['ir.sequence'].get('makloon.order')
            new_name = obj_sequence
            if new_name:
                me.write({'name': new_name})
        # return self.write({'state': 'user_approve'})


    # @api.multi
    def button_approve(self):
        # self.write({'state': 'purchase'})
        for me in self:
            if not (me.material_ids and me.result_ids):
                raise UserError(_('Material and result are empty'))

        self._create_sequence_mo()
        self._create_po()
        self._create_picking_out()

        self.write({'state': 'confirm'})

        return True

    # @api.multi
    def button_process(self):
        # self.write({'state': 'purchase'})
        self._create_picking_in()

        self.write({'state': 'process'})

        return True

    # @api.multi
    def button_done(self):
        self.ensure_one()

        # if not self.stock_result_done_pack_ids:
        #     return False
        # self._reentries_journal()

        self.state = 'done'
        # self.write({'state': 'done'})

        self.stage_id.mark_as_done()

        return True


    # @api.multi
    def _reentries_journal(self):
        # code for cleaning journal here
        return


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id.id:
            location_prod_id = self.env['stock.location'].search([('usage','=','production'),('partner_id','=', self.partner_id.id)])
            if location_prod_id:
                self.production_loc=location_prod_id.id
            else:
                self.production_loc = False



    # @api.multi
    def _create_po(self):
        po_obj = self.env['purchase.order']
        po_line_obj = self.env['purchase.order.line']
        for me in self:
            if me.result_ids:
                po_data = {
                    'origin': me.name,
                    'partner_id': me.partner_id.id,
                    # 'makloon_id': me.id,
                    'type_id': 4,
                    # 'order_line': []
                }
                po_obj.create(po_data)
                # for rs in me.result_ids:
                #     line = {
                #         'name': rs.service_product_id.name,
                #         'order_id': po_id.id,
                #         'product_id': rs.service_product_id.id,
                #         'price_unit': rs.service_product_id.standard_price,
                #         'product_uom': rs.service_product_id.uom_id.id,
                #         'product_qty': rs.product_uom_qty,
                #         'date_planned': me.date_order
                #     }
                #     po_line_obj.create(line)

        #         return True

        # return False

    # @api.multi
    def create_so(self):
        return

    # @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    # @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})    


    @api.model
    def _prepare_picking_out(self):

        if not self.production_loc.id:
            raise UserError(_("You must set a Vendor Location Production for this partner %s") % self.partner_id.name)

        # print "LOCATION OUT ORDER ", self.warehouse_id.wh_output_stock_loc_id.id,
        return {
            'picking_type_id': self.warehouse_id.out_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self.production_loc.id,
            'location_id': self.warehouse_id.lot_stock_id.id,
            'company_id': self.company_id.id,
            'makloon_order_id': self.id
        }

    # @api.multi
    def _create_picking_out(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if order.type=="out":
                if any([ptype in ['product', 'consu'] for ptype in order.material_ids.mapped('product_id.type')]):
                    # pickings = StockPicking.search([('makloon_order_id','=', order.id)])
                    # if not pickings:
                    res = order._prepare_picking_out()
                    picking = StockPicking.create(res)
                    # else:
                    #     picking = pickings[0]
                    moves = order.material_ids._create_stock_moves_out(picking)
                    # moves = moves.filtered(lambda x: x.state not in ('done', 'cancel')).action_confirm()
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))
                    # moves.action_assign()
                    picking.message_post_with_view('mail.message_origin_link',
                                                   values={'self': picking, 'origin': order},
                                                   subtype_id=self.env.ref('mail.mt_note').id)
        return True

    @api.model
    def _prepare_picking_in(self):

        if not self.production_loc.id:
            raise UserError(_("You must set a Vendor Location Production for this partner %s") % self.partner_id.name)
        # print "LOCATION IN ORDER ", self.production_loc.id
        # supplier_loc = self.env['stock.location'].search([('usage','=','supplier')])
        # if len(supplier_loc)>1:
        #     supplier_loc = supplier_loc[0]

        return {
            'picking_type_id': self.warehouse_id.in_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'location_id': self.production_loc.id,
            'location_dest_id': self.warehouse_id.lot_stock_id.id,
            'company_id': self.company_id.id,
            'makloon_order_id': self.id
        }

    # @api.multi
    def _create_picking_in(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if order.type == "out":
                if any([ptype in ['product', 'consu'] for ptype in order.result_ids.mapped('product_id.type')]):
                    # pickings = StockPicking.search([('makloon_order_id', '=', order.id)])
                    # if not pickings:
                    res = order._prepare_picking_in()
                    picking = StockPicking.create(res)
                    # else:
                    #     picking = pickings[0]
                    moves = order.result_ids._create_stock_moves_in(picking)
                    # moves = moves.filtered(lambda x: x.state not in ('done', 'cancel')).action_confirm()
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))
                    # moves.force_assign()
                    # moves.action_assign()
                    for line in moves:
                        sp = self.env['stock.move'].search([('picking_id', '=', picking.id),
                                                            ('product_id', '=', line.product_id.id)])
                        # print 'sp=>', sp,'picking=>',picking,'pickingid=>',picking.id
                        if sp:
                            for line2 in sp:
                                product_merk_id = line.product_merk_id.id
                                product_setting_id = line.product_setting_id.id
                                product_gramasi_id = line.product_gramasi_id.id
                                product_corak_id = line.product_corak_id.id
                                product_warna_id = line.product_warna_id.id
                                product_resep_warna_id = line.product_resep_warna_id.id
                                product_category_warna_id = line.product_category_warna_id.id

                                line2.product_merk_id = product_merk_id
                                line2.product_setting_id = product_setting_id
                                line2.product_gramasi_id = product_gramasi_id
                                line2.product_corak_id = product_corak_id
                                line2.product_warna_id = product_warna_id
                                line2.product_resep_warna_id = product_resep_warna_id
                                line2.product_category_warna_id = product_category_warna_id
                                # print 'looping sp =>', product_merk_id, product_setting_id, product_gramasi_id, product_corak_id, product_warna_id, product_resep_warna_id, product_category_warna_id
                    picking.message_post_with_view('mail.message_origin_link',
                                                   values={'self': picking, 'origin': order},
                                                   subtype_id=self.env.ref('mail.mt_note').id)
                    # picking.action_generate_serial()

    # @api.multi
    def action_view_picking_out(self):

        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.mapped('production_pick_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action


    # @api.multi
    def action_view_picking_in(self):
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        # action['domain'] = [('makloon_order_id', '=', self.id),('picking_type_id.code','=','internal')]
        action['domain'] = [('makloon_order_id', '=', self.id)]
        # elif pickings:
        #     b
        #     action['views'] = [(self.env.ref('stock.view_picdgdking_form').id, 'form')]
        #     action['res_id'] = pickings.id
        
        # action['domain'] = [('makloon_order_id', '=', self.id)]
        # action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
        # action['res_id'] = pickings.id
        return action



    # @api.multi
    def action_view_po(self):
        action = self.env.ref('purchase.purchase_rfq').read()[0]

        po_id = self.mapped('po_ids')
        if len(po_id) > 1:
            action['domain'] = [('id', 'in', po_id.ids)]
        elif po_id:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = po_id.id
        return action

    # @api.multi
    def action_view_journal_item(self):
        action = self.env.ref('account.action_account_moves_all_a').read()[0]
        move_ids = []
        for me in self:
            for pick in me.picking_ids:
                move_data = self.env['account.move.line'].search([('ref', '=', pick.name)])
                for mv in move_data:
                    move_ids.append(mv.id)


        if move_ids:
            action['domain'] = [('id', 'in', move_ids)]
            return action
        else:
            return False


class MakloonOrderMaterial(models.Model):
    _name = 'makloon.order.material'

    name = fields.Char("Number")
    order_id =fields.Many2one("makloon.order", "Order No", ondelete="cascade")
    stage_id = fields.Many2one("makloon.planning.stage", "Stage")
    product_id = fields.Many2one("product.product","Material", required=True, domain=[('type', 'in', ['product', 'consu'])])
    product_uom_qty = fields.Float(
        'Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        default=1.0, required=True,)
    price_unit = fields.Float("Price")

    product_uom = fields.Many2one(
        'uom.uom', 'Unit of Measure', required=True)
    size_id = fields.Many2one('size', string='Size')


    @api.onchange('product_id')
    def onchage_product_id(self):
        self.product_uom = False
        self.price_unit = 0
        if self.product_id:
            self.name = self.product_id.name
            self.product_uom = self.product_id.uom_id.id
            self.price_unit = self.product_id.standard_price



    # @api.multi
    def _get_stock_move_price_unit(self):
        self.ensure_one()
        line = self[0]
        order = line.order_id
        price_unit = line.price_unit
        # if line.taxes_id:
        #     price_unit = \
        #     line.taxes_id.with_context(round=False).compute_all(price_unit, currency=line.order_id.currency_id,
        #                                                         quantity=1.0)['total_excluded']
        if line.product_uom.id != line.product_id.uom_id.id:
            price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
        if order.currency_id != order.company_id.currency_id:
            price_unit = order.currency_id.compute(price_unit, order.company_id.currency_id, round=False)
        return price_unit

    # @api.multi
    def _create_stock_moves_out(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            if line.product_id.type not in ['product', 'consu']:
                continue
            qty = 0.0
            price_unit = line._get_stock_move_price_unit()
            # for move in line.move_ids.filtered(lambda x: x.state != 'cancel'):
            #     qty += move.product_qty

            # print "LOCATION OUT MATERIAL .., ", line.order_id.warehouse_id.wh_output_stock_loc_id.id


            template = {
                'name': line.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.product_uom.id,
                'date': line.order_id.date_order,
                # 'date_expected': line.order_id.date_order,
                'location_id': line.order_id.warehouse_id.lot_stock_id.id, #sself.warehouse_id.wh_output_stock_loc_id.id,
                'location_dest_id': line.order_id.production_loc.id,
                'picking_id': picking.id,
                'partner_id': line.order_id.partner_id.id,
                # 'move_dest_id': False,
                'state': 'draft',
                # 'purchase_line_id': line.id,
                'company_id': line.order_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': line.order_id.warehouse_id.out_type_id.id,
                'group_id': False,
                # 'procurement_id': False,
                'origin': line.order_id.name,
                # 'route_ids': line.order_id.picking_type_id.warehouse_id and [
                #     (6, 0, [x.id for x in line.order_id.picking_type_id.warehouse_id.route_ids])] or [],
                'warehouse_id': line.order_id.warehouse_id.id,
            }
            # Fullfill all related procurements with this po line
            diff_quantity = line.product_uom_qty - qty

            if float_compare(diff_quantity, 0.0, precision_rounding=line.product_uom.rounding) > 0:
                template['product_uom_qty'] = diff_quantity
                done += moves.create(template)
        return done





class MakloonOrderResult(models.Model):
    _name = 'makloon.order.result'

    name = fields.Char("Number")
    order_id = fields.Many2one("makloon.order", "Order No", ondelete="cascade")
    stage_id = fields.Many2one("makloon.planning.stage", "Stage")

    product_id = fields.Many2one("product.product", "Result Product", required=True,
                                 domain=[('type', 'in', ['product', 'consu'])])
    product_uom_qty = fields.Float(
        'Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        default=1.0, required=True)
    product_uom = fields.Many2one(
        'uom.uom', 'Unit of Measure', required=True)
    service_product_id = fields.Many2one("product.product", "Makloon Service Product", required=True,
                                         domain=[('type', '=', 'service')])

    price_unit = fields.Float("Price")
    waste_valasi = fields.Float("Waste/Valasi in %")

    @api.onchange('product_id')
    def onchage_product_id(self):
        self.product_uom = False
        self.price_unit = 0
        if self.product_id:
            self.name = self.product_id.name
            self.product_uom = self.product_id.uom_id.id
            self.price_unit = self.product_id.standard_price

    # @api.multi
    def _get_stock_move_price_unit(self):
        self.ensure_one()
        line = self[0]
        order = line.order_id
        price_unit = 0.0 #line.price_unit   line.product_id.product_tmpl_id
        construct_product = line.product_id.product_tmpl_id.construct_ids
        if construct_product:
            for cp in construct_product:
                price_unit += cp.product_id.standard_price*(cp.struct_persentage/100)
                if line.waste_valasi>0.0:
                    price_unit += line.product_uom_qty*(line.waste_valasi/100)*cp.product_id.standard_price*(cp.struct_persentage/100)
        if line.service_product_id:
            price_unit += line.service_product_id.standard_price
        if line.product_uom.id != line.product_id.uom_id.id:
            price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
        if order.currency_id != order.company_id.currency_id:
            price_unit = order.currency_id.compute(price_unit, order.company_id.currency_id, round=False)
        return price_unit

    # @api.multi
    def _create_stock_moves_in(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            if line.product_id.type not in ['product', 'consu']:
                continue
            qty = 0.0
            price_unit = line._get_stock_move_price_unit()

            # print "LOCATION IN RESULT .., ", line.order_id.production_loc.id

            template = {
                'name': line.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.product_uom.id,
                'date': line.order_id.date_order,
                # 'date_expected': line.order_id.date_order,

                'location_id': picking.location_id.id, #line.order_id.production_loc.id,  # self.production_loc.id
                'location_dest_id': line.order_id.warehouse_id.lot_stock_id.id,


                'picking_id': picking.id,
                'partner_id': line.order_id.partner_id.id,
                # 'move_dest_id': False,
                'state': 'draft',
                # 'purchase_line_id': line.id,
                'company_id': line.order_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': line.order_id.warehouse_id.in_type_id.id,
                'group_id': False,
                # 'procurement_id': False,
                'origin': line.order_id.name,
                'warehouse_id': line.order_id.warehouse_id.id,
            }
            diff_quantity = line.product_uom_qty - qty
            if float_compare(diff_quantity, 0.0, precision_rounding=line.product_uom.rounding) > 0:
                template['product_uom_qty'] = diff_quantity
                done += moves.create(template)
        return done





