from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta ,datetime
import logging
_log = logging.getLogger(__name__)


class ManufacturingRequest(models.Model):
    _name = 'mrp.request'
    _description = 'Material Production Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.onchange('sale_id')
    def _get_sale_order_line(self):
        for request in self:
            request.order_temp_ids = False
            for line in request.sale_id.order_line:
                request.order_temp_ids = [(0,0,{
                    "product_id":line.product_id.id,
                    "order_line_id":line.id,
                    "sale_id":line.order_id.id,
                    "mrp_request_id":self.id,
                    "product_uom_id":line.product_uom.id,
                    "quantity":line.product_uom_qty,
                    "remaining_qty":line.remaining_qty,
                    "state":line.state
                })]
                
    def _update_sale_order_line(self):
        for request in self:
            request.order_line_ids = False
            for line in request.order_temp_ids:
                request.update({"order_line_ids": [(4,line.order_line_id.id)]})
    
    @api.depends('quantity','shrinkage_id')
    def _compute_quantity_shrinkage(self):
        for request in self:
            shrinkage = 0
            if request.quantity > 0 and request.shrinkage_id:
                shrinkage = request.quantity * request.shrinkage_id.percentage / 100
            request.quantity_shrinkage = request.quantity + shrinkage
            
    name                 = fields.Char(string='Name', default=lambda self: _('New'))
    state                = fields.Selection([('draft', 'Draft'),('confirm', 'Confirm'),('done', 'Done')], string='Status', default='draft')
    partner_id           = fields.Many2one('res.partner', string='Customer')
    production_type_id   = fields.Many2one('mrp.type', string='Production Type')
    sale_id              = fields.Many2one('sale.order', string='Sale Order')
    td_id                = fields.Many2one(related='sale_id.hanger_code', string='TD')
    process_type         = fields.Many2one(related='td_id.process_type', string='Process Type')
    process_category_id  = fields.Many2one(related='process_type.category_id', string='Process Category')
    sale_qty             = fields.Float(related='sale_id.amount_qty', string='Sale Quantity')
    tanggal              = fields.Date(string='Date',default=fields.Date.today())
    jumlah_spk           = fields.Integer(string='Jumlah Spk')
    product_id           = fields.Many2one('product.template', string='Product')
    
    # 
    component_type       = fields.Selection([("one","One Kind"),("combine","Combine")], string='Component Type')
    component_ids        = fields.One2many('mrp.request.component', 'mrp_request_id', string='Component')
    yarn_template_id     = fields.Many2one('product.template', string='Yarn Template',domain=[('categ_id.name', 'ilike', '%benang%')])
    yarn_id              = fields.Many2one(comodel_name='product.product', string='Product',domain=[('categ_id.name', 'ilike', '%benang%')])
    yarn_stock_ids       = fields.One2many('mrp.yarn.stock', 'mrp_request_id', string='Yarn Stock')
    sisir_id             = fields.Many2one('master.sisir', string='Sisir')
    total_end            = fields.Integer(string='Total End')
    total_creel          = fields.Integer(string='Creel')
    total_beam           = fields.Integer(string='Total Beam')
    sale_line_ids        = fields.One2many(string='Orders',related="sale_id.order_line")
    order_line_ids       = fields.Many2many(comodel_name='sale.order.line', string='Order Line',compute="_update_sale_order_line")
    order_temp_ids       = fields.One2many('sale.order.line.temp', 'mrp_request_id', string='Order Detail')      
    machine_temp_ids     = fields.One2many('machine.planning.temp', 'mrp_request_id', string='Machine Plan')      
    machine_id           = fields.Many2one('mrp.machine', string='Machine')    
    
    
    
    
    
    greige_template_id   = fields.Many2one('product.template', string='Greige Template',domain=[('categ_id.name', '=', 'GREY')])
    greige_id            = fields.Many2one('product.product', string='Greige Name',domain=[('categ_id.name', '=', 'GREY')])
    picking_ids          = fields.Many2many('stock.picking', compute='_compute_picking', string='Request Greige', copy=False,)
    picking_count        = fields.Integer(compute='_compute_picking', string='Picking count', default=0,)
    greige_stock_ids     = fields.One2many('mrp.greige.stock', 'mrp_request_id', string='Greige Stock')
    shrinkage_id         = fields.Many2one('mrp.shrinkage', string='Shrinkage')
    shrinkage_percentage = fields.Float(string='Shrinkage Percentage',related='shrinkage_id.percentage')
    quantity_shrinkage   = fields.Float(string='Quantity With Shrinkage',compute='_compute_quantity_shrinkage')
    mrp_picking_type     = fields.Many2one('stock.picking.type', string='Manufacture',domain=[('default_location_src_id.location_id.complete_name', 'ilike', '%GPD%'),('code','=','mrp_operation')])

    
    #fix me waving only
    pakan               = fields.Char(string='Pakan')
    std_susut           = fields.Float(string='Std Susut')
    pic                 = fields.Integer(string='Pic')
    gramasi             = fields.Integer(string='Gramasi')
    lebar               = fields.Integer(string='Lebar')
    density             = fields.Integer(string='Density')
    sale_type           = fields.Selection(string='Sale Type',related='sale_id.sale_type')
    handling            = fields.Selection(string='Handling',related='sale_id.handling')
    handling_id         = fields.Many2one('master.handling', string='Master Handling', related='sale_id.handling_id')
    
    quantity            = fields.Float(string='Quantity', required=True, )
    uom_id              = fields.Many2one('uom.uom', string='Uom', required=True, default=46 ,domain=[('category_id','=',4)])
    bom_id              = fields.Many2one('mrp.bom', string='BoM')
    picking_type_id     = fields.Many2one('stock.picking.type', string='Operation Type', related='production_type_id.picking_type_id')
    component_location  = fields.Many2one('stock.location', string='Component Location', related='production_type_id.component_location')
    finished_location   = fields.Many2one('stock.location', string='Finished Location', related='production_type_id.finished_location')
    location_id         = fields.Many2one('stock.location', string='Department',domain=[('usage', '=', 'internal')])
    detail_ids          = fields.One2many('mrp.request.detail', 'mrp_request_id', string='Detail')
    mrp_ids             = fields.One2many('mrp.production', 'mrp_request_id', string='Manufacturing Order')
    batched_count       = fields.Integer(string='Batched',compute="_count_batch")
    multiplier          = fields.Integer(string='Multiplier', default=1)

    mkt_production_id   = fields.Many2one('mkt.production.line', string='Mkt Production')
    type_twist          = fields.Selection([("interlace","Interlace"),("tfo","TFO")], string='Type Twist')
    revisi              = fields.Integer(string='Revisi')
    qty_mkt             = fields.Float(string='Total Order')
    qty_tarik           = fields.Float(string='Order Penarikan SW')
    yarn_type           = fields.Selection([("lusi","Lusi"),("pakan","Pakan")], string='Yarn Type')
    weaving_mc_type     = fields.Selection([("wjl","WJL"),("shuttle","Shutter")], string='Weaving Machine Type')
    
    @api.onchange('mkt_production_id')
    def get_mkt_production_id(self):
        for rec in self:
            rec.qty_mkt = rec.mkt_production_id.quantity
            rec.greige_id = rec.mkt_production_id.product_id.id
   
    
    def _count_batch(self):
        for request in self:
            request.batched_count = len(request.mrp_ids)
        
        
    @api.onchange('greige_id')
    def get_quants(self):
        if not self.greige_id:
            self.greige_stock_ids = False 
        variant_ids = self.env['product.product'].search([('product_tmpl_id','=',self.greige_template_id.id)])
        if self.greige_stock_ids:
            variant_ids = variant_ids.filtered(lambda x:x.id not in [ product.id for  product in self.greige_stock_ids.mapped('greige_id')])
        for variant in variant_ids:
            self.greige_stock_ids = [(0,0,{
                "mrp_request_id":self.id,
                "greige_id":variant.id,
                
            })]
            
            
    def create_bom(self,product):
        bom = self.env['mrp.bom'].create({
            "product_tmpl_id": product.product_tmpl_id.id,
            "product_id": product.id,
            "type":"normal",
            "location_destinaion":self.production_type_id.component_location.id,
            
        })
    
    
    
    def request_material(self):
        for production in self.mrp_ids:
            if self.production_type_id.id == 2:
                self.env['stock.picking'].sudo().create({
                    "picking_type_id":self.production_type_id.component_greige_picking_type_id.id,
                    "location_id":self.production_type_id.component_greige_location.id,
                    "location_dest_id":self.mrp_picking_type.default_location_src_id.id,
                    # "location_dest_id":self.production_type_id.component_location.id,
                    "mrp_request_id": self.id,
                    "production_id": production.id,
                    "greige_qty_req":sum(production.move_raw_ids.filtered(lambda x:x.product_id.categ_id.name == 'GREY').mapped('product_uom_qty')),
                    "origin": production.name,
                    "move_ids_without_package":[(0,0, {
                        "name":self.greige_id.name,
                        "product_id":self.greige_id.id,
                        "product_uom_qty":self.quantity_shrinkage,
                        "product_uom":self.greige_id.uom_id.id,
                        "location_id":self.production_type_id.component_greige_location.id,
                        # "location_dest_id":self.production_type_id.component_location.id,
                        "location_dest_id":self.mrp_picking_type.default_location_src_id.id,
                        "move_dest_ids":[(4,move.id) for move in production.move_raw_ids.filtered(lambda x: x.product_id.categ_id.name == "GREY")]
                    })]
                })
            else:
                # TWISTING
                self.env['stock.picking'].create({
                    "picking_type_id"   : self.picking_type_id.id,
                    "location_id"       : self.component_location.id,
                    "location_dest_id"  : self.finished_location.id,
                    "mrp_request_id"    : self.id,
                    "production_id"     : production.id,
                    "origin"            : production.name,
                    "move_line_ids_without_package":[(0,0, {
                        "lot_id"            : move.lot_id.id,
                        "product_id"        : move.product_id.id,
                        "product_uom_qty"   : move.product_uom_qty,
                        "product_uom_id"    : move.product_id.uom_id.id,
                        "location_id"       : self.component_location.id,
                        "location_dest_id"  : self.finished_location.id,
                    }) for move in production.move_raw_ids]
                })
                
        
    
    
    @api.depends('mrp_ids')
    def _compute_picking(self):
        for request in self:
            pickings = self.env['stock.picking'].search([('mrp_request_id','=',request.id)])
            request.picking_count = len(pickings)
            request.picking_ids = pickings
    
    
    @api.onchange('sale_id')
    def get_partner_id(self):
        self.partner_id         = self.sale_id.partner_id.id
        self.greige_template_id = self.sale_id.greige_id.id 
        self.product_id         = self.sale_id.product_id.id 
        self.production_type_id = 2 if self.sale_id else False
        self.gramasi            = self.sale_id.gramasi if self.sale_id else False
        self.lebar              = self.sale_id.lebar if self.sale_id else False
        self.handling           = self.sale_id.handling if self.sale_id else False
        self.density            = self.sale_id.density if self.sale_id else False
    
    
    
    def action_draft(self):
        self.state = 'draft'
        for picking in self.picking_ids:
            picking.unlink()
            
        for production in self.mrp_ids:
            production.write({"move_raw_ids":False})
        
        self.machine_temp_ids = False
            
        
        
    def action_view_picking(self):
        result = self.env["ir.actions.actions"]._for_xml_id('inherit_mrp.stock_picking_four_digits_action')
        pick_ids = self.mapped('picking_ids')
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = pick_ids.id
        return result
        
    

    def action_confirm(self):
        if self.production_type_id.id == 2:
            if not self.mrp_ids:
                mrp_ids = []
                machine_plan = []
                for line in self.order_temp_ids:
                    qty_kg_greige =  (self.gramasi / 1000 * self.lebar / 100) * 0.9144 * self.quantity_shrinkage 
                    
                # for line in self.order_temp_ids.filtered(lambda x: x.remaining_qty >= self.quantity):
                    bom_id = self.env['mrp.bom'].search([('product_id','=',line.product_id.id),('td_id','=',self.sale_id.hanger_code.id)])
                    color_final = self.env['labdip.color.final'].sudo().search([('color_id','=',line.product_id.color_id.id),('labdip_id','=',self.sale_id.design_id.labdip_id.id)],limit=1)
                    
                    if self.sale_id.design_id.labdip_id:
                        for design_line in self.sale_id.design_id.line_ids.filtered(lambda x: x.variant_id.id == line.product_id.id):
                            design_line.sudo().write({"greige_id":self.greige_id.id})
                    
                        
                    
                    if bom_id:
                        bom_id.write({
                            "picking_type_id":self.mrp_picking_type.id,
                            "labdip_id":self.sale_id.design_id.labdip_id.id,
                            "td_id":self.sale_id.hanger_code.id,
                            "location_id":self.mrp_picking_type.default_location_src_id.id,
                            
                        })
                        
                        # if not bom_id.operation_ids:
                        
                        bom_id.action_set_to_draft()
                        

                        bom_id.update({'material_td_ids': False, 'mrp_first_compenent_ids': False, 'bom_line_ids': False}) # delete material Td, lab, operations
                        bom_id.update({
                                            "mrp_first_compenent_ids":[(0,0,{"product_id":self.greige_id.id,
                                            "quantity":self.quantity_shrinkage,
                                            "quantity_finish":self.quantity_shrinkage,
                                            "product_uom_id":self.greige_id.uom_id.id,
                                            "location_id":self.mrp_picking_type.default_location_src_id.id
                                            # "location_id":self.production_type_id.finished_location.id
                                            })],  
                        })
                        bom_id.action_get_material_td(self.mrp_picking_type.default_location_src_id.id)
                        
                        bom_id.action_get_material_lab(self.mrp_picking_type.default_location_src_id.id,{
                            "qty_kg_greige":qty_kg_greige,
                        })
                        bom_id.action_confirm()
                        
                        # bom_line_ids = bom_id.bom_line_ids.filtered(lambda x:x.product_id.categ_id.id == 127)
                        # first_line_ids = bom_id.mrp_first_compenent_ids.filtered(lambda x:x.product_id.categ_id.id == 127)
                        # if len(bom_line_ids) > 0:
                        #     for bomline in bom_line_ids:
                        #         bomline.write({"product_id":self.greige_id.id,
                        #                     "product_qty":self.quantity_shrinkage,
                        #                     "product_uom_id":self.greige_id.uom_id.id,
                        #                     "location_id":self.production_type_id.finished_location.id})
                        # else:
                        #     bom_id.write({
                        #                     "bom_line_ids":[(0,0,{"product_id":self.greige_id.id,
                        #                     "product_qty":self.quantity_shrinkage,
                        #                     "product_uom_id":self.greige_id.uom_id.id,
                        #                     "location_id":self.production_type_id.finished_location.id})]})
                            
                        # if len(first_line_ids) > 0:
                        #     for fistline in first_line_ids:
                        #         fistline.write({"product_id":self.greige_id.id,
                        #                     "quantity":self.quantity_shrinkage,
                        #                     "product_uom_id":self.greige_id.uom_id.id,
                        #                     "location_id":self.production_type_id.finished_location.id})
                        # else:
                        #     bom_id.write({"mrp_first_compenent_ids":[(0,0,{"product_id":self.greige_id.id,
                        #                     "quantity":self.quantity_shrinkage,
                        #                     "product_uom_id":self.greige_id.uom_id.id,
                        #                     "location_id":self.production_type_id.finished_location.id})]})
                    else:
                        bom_id = bom_id.create({"product_tmpl_id":self.product_id.id,
                                                "product_id":line.product_id.id,
                                                "location_id":self.production_type_id.finished_location.id,
                                                "type":"normal",
                                                "picking_type_id":self.mrp_picking_type.id,
                                                "location_id":self.mrp_picking_type.default_location_src_id.id,
                                                
                                                
                                                "labdip_id":self.sale_id.design_id.labdip_id.id,
                                                "color_final_id": color_final.id,
                                                "td_id":self.sale_id.hanger_code.id,
                                                "product_uom_id":line.product_id.uom_id.id,
                                                "mrp_first_compenent_ids":[(0,0,{"product_id":self.greige_id.id,
                                                    "quantity":self.quantity_shrinkage,
                                                    "quantity_finish":self.quantity_shrinkage,
                                                    
                                                    "product_uom_id":self.greige_id.uom_id.id,
                                                    "location_id":self.mrp_picking_type.default_location_src_id.id
                                                    # "location_id":self.production_type_id.finished_location.id
                                                    })],
                                                # "bom_line_ids":[(0,0,{"product_id":self.greige_id.id,
                                                #     "product_qty":self.quantity_shrinkage,
                                                #     "product_uom_id":self.greige_id.uom_id.id,
                                                #     "location_id":self.production_type_id.finished_location.id})]
                                            })
                        # bom_id.action_set_to_draft()
                        bom_id.action_get_material_td(self.mrp_picking_type.default_location_src_id.id)
                        bom_id.action_get_material_lab(self.mrp_picking_type.default_location_src_id.id,{
                            "qty_kg_greige":qty_kg_greige,
                        })
                        bom_id.action_confirm()
                        
                    multiplier = self.multiplier
                    if multiplier > 0:
                        workorder_list = []
                        for work in bom_id.operation_ids:
                            param = [(0, 0, {'parameter_id': b.parameter_id.id, 'no_urut':b.no_urut, 'plan':b.plan,
                            'actual':b.actual, 'uom_id':b.uom_id.id}) for b in work.routing_paramter_ids]
                            duration = work.program_id.duration
                            dt = timedelta(minutes=duration) if work.program_id else False
                            dt_finished = datetime.combine(self.tanggal, datetime.min.time()) + dt if dt else False
                            
                            
                            workorder_list.append((0, 0, {"name": work.name,
                                            "workcenter_id": work.workcenter_id.id,
                                            "mesin_id": work.mesin_id.id,
                                            "program_id": work.program_id.id,
                                            "date_planned_start":datetime.combine(self.tanggal, datetime.min.time()),
                                            "date_planned_finished":dt_finished,
                                            "product_uom_id": self.uom_id.id,
                                            "consumption": 'flexible',
                                            "parameter_ids": param}))
                        for a in range(multiplier):
                            type_id          = self.env['mrp.type'].browse(self.production_type_id.id)
                            mo_name          = type_id.production_sequence_id.next_by_id()
                            lot_producing_id = self.env['stock.production.lot'].sudo().create({
                                    "name": mo_name,
                                    "inspect_date":self.tanggal,
                                    "tanggal_produksi":self.tanggal,
                                    "location_id":self.mrp_picking_type.default_location_dest_id.id,
                                    "product_id":line.product_id.id,
                                    "company_id":self.env.user.company_id.id
                                })
                            mrp_ids.append((0,0,{
                                "name":mo_name,
                                "product_id":line.product_id.id,
                                "lot_producing_id": lot_producing_id.id,
                                "type_id":self.production_type_id.id,
                                "product_uom_id":self.uom_id.id,
                                "date_planned_start": self.tanggal,
                                "bom_id":bom_id.id,
                                "mrp_request_id":self.id,
                                "quantity_request": self.quantity_shrinkage,
                                "greige_id":self.greige_id.id,
                                "gramasi_kain_finish":self.gramasi,
                                "lebar_kain_finish":self.lebar,
                                "density_kain_finish":self.density,
                                "qty_yard_kp" :self.quantity_shrinkage,
                                "product_qty" :self.quantity_shrinkage,
                                # "qty_producing":self.quantity_shrinkage,
                                "sale_line_id":line.order_line_id.id,
                                "origin": self.name,
                                "sale_type":self.sale_type,
                                "mesin_id":self.machine_id.id,
                                "sale_id":self.sale_id.id,
                                "sc_id":self.sale_id.sc_id.id,
                                "picking_type_id":self.mrp_picking_type.id,
                                "location_src_id":self.mrp_picking_type.default_location_src_id.id,
                                "location_dest_id":self.mrp_picking_type.default_location_dest_id.id,
                                # "picking_type_id":self.production_type_id.picking_type_id.id,
                                # "location_src_id":self.production_type_id.component_location.id,
                                # "location_dest_id":self.production_type_id.finished_location.id,
                                # "move_raw_ids": [(0,0,{
                                #     "name":self.greige_id.name,
                                #     "product_id":self.greige_id.id,
                                #     "product_uom_qty":self.quantity_shrinkage,
                                #     "product_uom":self.greige_id.uom_id.id,
                                #     "location_id":self.production_type_id.component_location.id,
                                #     "location_dest_id":15,
                                #     })],
                                # "workorder_ids": workorder_list,
                                "no_urut_labdip_final" : color_final.no_urut
                                }))
                
                self.mrp_ids = mrp_ids
                print('======IF=====')
                for mrp in self.mrp_ids:
                    mrp._onchange_bom_id()
                    mrp._onchange_move_raw()
                    mrp._onchange_move_finished()
                    mrp._onchange_workorder_ids()
                    mrp.update({'product_qty': self.quantity_shrinkage})
                    for wo in mrp.workorder_ids.filtered(lambda x:x.workcenter_id.is_planning):
                        machine_plan.append((0,0,{
                            "production_id":wo.production_id.id,
                            "workorder_id":wo.id,
                        }))
                        
                        
                    

                
                self.machine_temp_ids = machine_plan
                    # raise UserError('Quantity Request more than outstanding !!!')
            else:
                for production in self.mrp_ids:
                    print('======elseeee=====')
                    # production.write({"move_raw_ids": [(0,0,{
                    #             "name":self.greige_id.name,
                    #             "product_id":self.greige_id.id,
                    #             "product_uom_qty":self.quantity_shrinkage,
                    #             # "mesin_id":self.machine_id.id,
                    #             "product_uom":self.greige_id.uom_id.id,
                    #             "location_id":self.production_type_id.component_location.id,
                    #             "location_dest_id":15,
                    #         })],})
                    production._onchange_bom_id()
                    production._onchange_move_raw()
                    production._onchange_move_finished()
                    production._onchange_workorder_ids()
            self.request_material()
            # for line in self.order_temp_ids.filtered(lambda x: x.remaining_qty < self.quantity):
                
            #         title = _("Warning")
            #         message = _("Quantity Request More Than Outstanding!!")
            #         return {
            #             'type': 'ir.actions.client',
            #             'tag': 'display_notification',
            #             'params': {
            #                 'title': title,
            #                 'message': message,
            #                 'sticky': True,
            #             }
            #         }
                    

        else:
            # TWISTING
            if self.mrp_ids:
                for mrp in self.mrp_ids:
                    mrp._onchange_move_raw()
                self.request_material()
        self.write({"state": "confirm"})
    

    @api.model
    def create(self, vals):
        production_type_id = self.env['mrp.type'].browse(vals.get('production_type_id'))
        vals['name'] = production_type_id.request_sequence_id.next_by_id()
        return super(ManufacturingRequest, self).create(vals)


class ManufacturingRequestDetail(models.Model):
    _name = 'mrp.request.detail'

    name            = fields.Char(string='Name')
    mrp_request_id  = fields.Many2one('mrp.request', string='Mrp Request')
    product_id      = fields.Many2one('product.product', string='Product', related='mrp_request_id.product_id')
    quantity        = fields.Float(string='Quantity')
    uom_id          = fields.Many2one('uom.uom', string='Uom', related='mrp_request_id.uom_id')
    machine_id      = fields.Many2one('mrp.machine', string='Machine')
    picking_type_id = fields.Many2one('stock.picking.type', string='Operation Type', related='mrp_request_id.picking_type_id')
    
    

class MrpGreigestockAvailable(models.Model):
    _name = 'mrp.greige.stock'

    name              = fields.Char(string='Name')
    mrp_request_id    = fields.Many2one('mrp.request', string='Mrp Request')
    greige_id         = fields.Many2one('product.product', string='Greige Name',domain=[('categ_id.name', '=', 'GREY')])
    std_potong        = fields.Float(string='Std Potong',related="greige_id.std_potong")
    uom_id            = fields.Many2one('uom.uom', related='greige_id.uom_id', string='Uom')
    quantity          = fields.Float(string='Quantity',compute='_compute_quantities')
    reserved_quantity = fields.Float(compute='_compute_reserved', string='Reserved', store=False)
    
    @api.depends('greige_id')
    def _compute_quantities(self):
        Quant = self.env['stock.quant'].with_context(active_test=False)
        source_location = self.mrp_request_id.production_type_id.component_greige_location.id
        for stock in self:
            domain_quant = [('product_id', '=',stock.greige_id.id),('location_id','=',source_location)]
            quants_res = dict((item['product_id'][0], (item['quantity'], item['reserved_quantity'])) for item in Quant.read_group(domain_quant, ['product_id', 'quantity', 'reserved_quantity'], ['product_id'], orderby='id'))
            reserved_quantity = quants_res.get(stock.greige_id.id, [False, 0.0])[1]
            onhand_quantity = quants_res.get(stock.greige_id.id, [False, 0.0])[0]
            stock.quantity = onhand_quantity
            stock.reserved_quantity = reserved_quantity

class MrpYarnStockAvailable(models.Model):
    _name = 'mrp.yarn.stock'

    name              = fields.Char(string='Name')
    mrp_request_id    = fields.Many2one('mrp.request', string='Mrp Request')
    yarn_id           = fields.Many2one('product.product', string='Yarn',domain=[('categ_id.name', 'ilike', '%benang%')])
    uom_id            = fields.Many2one('uom.uom', related='yarn_id.uom_id', string='Uom')
    quantity          = fields.Float(string='Quantity',compute='_compute_quantities')
    reserved_quantity = fields.Float(compute='_compute_reserved', string='Reserved', store=False)
    
    @api.depends('yarn_id')
    def _compute_quantities(self):
        Quant = self.env['stock.quant'].with_context(active_test=False)
        source_location = self.mrp_request_id.production_type_id.component_greige_location.id
        for stock in self:
            domain_quant = [('product_id', '=',stock.yarn_id.id),('location_id','=',source_location)]
            quants_res = dict((item['product_id'][0], (item['quantity'], item['reserved_quantity'])) for item in Quant.read_group(domain_quant, ['product_id', 'quantity', 'reserved_quantity'], ['product_id'], orderby='id'))
            reserved_quantity = quants_res.get(stock.yarn_id.id, [False, 0.0])[1]
            onhand_quantity = quants_res.get(stock.yarn_id.id, [False, 0.0])[0]
            stock.quantity = onhand_quantity
            stock.reserved_quantity = reserved_quantity


class MrpRequestComponent(models.Model):
    _name = 'mrp.request.component'
    
    mrp_request_id      = fields.Many2one('mrp.request', string='Mrp Request')
    production_type_id  = fields.Many2one(related='mrp_request_id.production_type_id', string='Production Type')
    yarn_id             = fields.Many2one('product.product', string='Yarn',domain=[('categ_id.name', 'ilike', '%benang%')])
    pakan_id            = fields.Many2one('product.product', string='Pakan',domain=[('categ_id.name', 'ilike', '%benang%')])
    sisir_id            = fields.Many2one('master.sisir', string='Sisir')
    # uom_id            = fields.Many2one('uom.uom', related='yarn_id.uom_id', string='Uom')
    
    


class SaleOrderLineTemp(models.Model):
    _name = 'sale.order.line.temp'
    
    sale_id         = fields.Many2one('sale.order', string='Sale')
    product_id      = fields.Many2one('product.product', string='Product')
    product_uom_id  = fields.Many2one(related='product_id.uom_id', string='Uom')
    order_line_id   = fields.Many2one('sale.order.line', string='Order Line')
    mrp_request_id  = fields.Many2one(comodel_name='mrp.request', string='Mrp Request')
    quantity        = fields.Float(string='Quantity')
    remaining_qty   = fields.Float(string='Outstanding')
    state           = fields.Char(string='State')
    
    
class MachinePlanningTemp(models.Model):
    _name = 'machine.planning.temp'
    
    mrp_request_id  = fields.Many2one(comodel_name='mrp.request', string='Mrp Request')
    machine_id      = fields.Many2one('mrp.machine', string='Machine')
    production_id   = fields.Many2one('mrp.production', string='Production')
    workorder_id    = fields.Many2one('mrp.workorder', string='Work Order')
    workcenter_id   = fields.Many2one('mrp.workcenter', string='Work Center',related="workorder_id.workcenter_id")
    
    
    
    def write(self, vals):
        if vals.get('machine_id'):
            if self.workcenter_id.name == 'DYEING':
                self.production_id.write({
                    "mesin_id":vals.get('machine_id')
                })
            self.workorder_id.write({
                "mesin_id":vals.get('machine_id')
            })
            
            
            
        
        
        return super(MachinePlanningTemp, self).write(vals)
        
    
    
    