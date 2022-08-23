from odoo import models, fields, api, _
from odoo.exceptions import UserError
from ast import literal_eval
import json
from odoo.tools.float_utils import  float_is_zero


class ManufacturingRequest(models.Model):
    _name = 'mrp.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    

    name                = fields.Char(string='Manufacture Request',default=_('New'))
    # order_ids           = fields.Many2many(comodel_name='stock.point.order', relation='mrp_request_stock_point_order_rel',string='Stock Point Order',domain=[('state', '=', 'confirm')])
    # order_lines         = fields.Many2many(comodel_name='stock.point.order.line', string='Details Request',)
    order_lines_product = fields.One2many('mrp.request.line.product','request_id', string='Group By Line',)
    # order_detail_lines  = fields.Many2many(comodel_name='stock.point.order.line', compute="_get_stock_point_order",string='Details Product Request',)
    request_date        = fields.Datetime(string='Request Date',default=fields.Datetime.now())
    user_id             = fields.Many2one('res.users', string='User',default=lambda self: self.env.user.id)
    line_ids            = fields.One2many('mrp.request.line', 'request_id', string='Details')
    note                = fields.Text(string='Note')
    picking_ids         = fields.Many2many(comodel_name='stock.picking', relation='mrp_request_stock_picking_rel',string='Transfer')
    picking_count       = fields.Integer(string='Transfer Count',compute="_compute_picking")
    production_count    = fields.Integer(string='Transfer Count',compute="_compute_picking")
    state               = fields.Selection([('draft', 'Draft'),('confirm', 'Confirm'),('done', 'Done'),('cancel', 'Cancelled'),], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    production_ids      = fields.One2many('mrp.production', 'request_id', string='Production')
    estimated_ids       = fields.One2many('mrp.production.estimated', 'request_id', string='Estimated')
    sale_id             = fields.Many2one('sale.order', string='Sale')
    partner_id          = fields.Many2one('res.partner', string='Customer')
    
    
    def check_validation(self):
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self.line_ids:
            if float_is_zero(line.qty_produce,precision_digits=precision_digits):
                raise UserError('Mohon maaf pastikan %s \nquantity produksi tidak nol'%(line.product_id.name))
        
    def action_estimated(self):
        self.ensure_one()
        self.check_validation()
        estimated_ids = []
        if not self.estimated_ids:
            for line in self.line_ids:
                src_from_other = self.line_ids.filtered(lambda x:x.product_orig_id and x.product_orig_id.id == line.product_id.id)
                if not line.product_orig_id and line.product_id.id != src_from_other.product_orig_id.id:
                    estimated_ids += [(0,0,{
                        "product_id":line.product_id.id,
                        "production_qty":line.product_qty_est,
                        "satuan_id":line.satuan_id.id,
                        "product_uom_qty": line.product_qty_est_conv,
                        "estimate_date": fields.Date.today(),
                        "production_date":self.request_date.date()
                    })]
                    
                elif not line.product_orig_id and line.product_id.id in [x.id for x in src_from_other.mapped('product_orig_id')]:
                    estimated_ids += [(0,0,{
                        "product_id":line.product_id.id,
                        "production_qty":line.product_qty_est - sum(src_from_other.mapped('product_qty_est')),
                        "satuan_id":line.satuan_id.id,
                        "product_uom_qty": line.product_qty_est_conv - sum(src_from_other.mapped('product_qty_est_conv')),
                        "estimate_date": fields.Date.today(),
                        "production_date":self.request_date.date()
                    })]
                elif line.product_orig_id:
                    estimated_ids += [(0,0,{
                        "product_id":line.product_id.id,
                        "production_qty":line.product_qty_est,
                        "satuan_id":line.satuan_id.id,
                        "product_uom_qty": line.product_qty_est_conv,
                        "estimate_date": fields.Date.today(),
                        "production_date":self.request_date.date()
                    })]
                    
                    
            self.estimated_ids = estimated_ids
            self.state = 'estimated'
                
    
    def action_create_production(self):
        self.ensure_one()
        production_ids = []
        self.check_validation()
        if not self.production_ids:
            for line in self.line_ids:
                picking_type_id = None  if not line.type_id else line.type_id.picking_type_id.id if line.type_id.picking_type_id else None
                # product_categ_id = line.product_id.categ_id
                
                # bom_id = self.env['mrp.bom'].search([('product_tmpl_id','=',line.product_id.product_tmpl_id.id)],limit=1)
                bom_id = self._prepare_bom(line.product_id, line.product_id.product_tmpl_id, line.operation_template_id)
                picking_type_id = self.env['stock.picking.type'].sudo().browse(picking_type_id)
                production_id = self.env['mrp.production'].create({
                    'product_id':line.product_id.id,
                    'type_id':line.type_id.id,
                    'product_uom_id':line.product_id.uom_id.id,
                    'product_qty': line.qty_produce,
                    'mrp_qty_produksi':line.qty_produce,
                    'bom_id': bom_id.id,
                    # 'satuan_id':line.satuan_id.id,
                    'picking_type_id': picking_type_id.id,
                    'origin':self.name,
                    'location_src_id': picking_type_id.default_location_src_id.id,
                    'location_dest_id':picking_type_id.default_location_dest_id.id,
                    'date_planned_start':line.request_id.request_date,
                    'request_id':self.id,
                })
                
                if production_id:
                    production_id._onchange_bom_id()
                    production_id._onchange_move_raw()
                    production_id._onchange_move_finished()
                    production_id._onchange_workorder_ids()
                    # line.production_ids = [(4,production_id.id)]
                    self._request_material(production_id)
                self.state = 'done'
    
    
    def _compute_picking(self):
        for request in self:
            request.picking_count = len(request.picking_ids)
            request.production_count = len(request.production_ids)
            
            
    def action_confirm(self):
        if self.name == 'New':
            ir_config        = self.env['ir.config_parameter'].sudo()
            mor_sequence_id  = ir_config.get_param('mor_sequence_id')
            if mor_sequence_id:
                seq = self.env['ir.sequence'].browse(int(mor_sequence_id)).next_by_id()
                self.name = seq
        self.state = 'confirm'

        # self.action_generate()
        
        
    def action_generate(self):
        if self.state in ('draft','confirm'):
            if not self.line_ids:
                order_lines = []
                line_ids = self.order_lines.read_group([('mrp_request_id','=',self.id)],['quantity'],'product_id',lazy=False)
                for line in line_ids:
                    order_lines += [(0,0,{"product_id":line.get('product_id')[0]})]
                self.line_ids = order_lines
            if not self.order_lines_product:
                order_lines_product = []
                line_product_ids = self.line_ids.read_group([('request_id','=',self.id)],['konversi_butir','product_qty_conv','product_qty_est','product_qty_est_conv'],['line_product_id','product_uom_id','satuan_id'],lazy=False)
                for line in line_product_ids:
                    order_lines_product += [(0,0,
                                             {"line_product_id":line.get('line_product_id')[0],
                                              "product_uom_id":line.get('product_uom_id')[0],
                                              "satuan_id":line.get('satuan_id')[0] if line.get('satuan_id') else False,
                                              "qty_production":line.get('product_qty_est'),
                                              })]
                self.order_lines_product = order_lines_product
        
        
    def action_done(self):
        self.state = 'done'
        
    def action_cancel_estimate(self):
        self.state = 'confirm'
        self.estimated_ids = False
        
    def action_back_to_draft(self):
        self.state = 'draft'
        self.line_ids = False
        self.estimated_ids = False
        self.order_lines_product = False
        for production in self.production_ids:
            if production.state in ('draft','cancel'):
                production.action_cancel()
                production.unlink()
        
        
    
    
    def _get_stock_point_order(self):
        for request in self:
            request.order_lines = [(4,line.id) for order in request.order_ids  for line in order.line_ids]
            
    
    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action['domain'] = [('id','in',self.picking_ids.ids)]
        action['context'] = {}
        return action
    
    def action_view_production(self):
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        action['domain'] = [('id','in',self.production_ids.ids)]
        action['context'] = {}
        return action
    
    def _prepare_bom(self, product_id, product_tmpl_id, operation_tmpl_id):
        bom_obj = self.env['mrp.bom'].search([('product_tmpl_id','=',product_tmpl_id.id),('operation_template_id', '=', operation_tmpl_id.id)],limit=1)
        if bom_obj:
            return bom_obj
        else:
            bom_obj = self.env['mrp.bom'].create({
                'product_tmpl_id': product_tmpl_id.id,
                'product_id': product_id.id,
                'product_qty': 1,
                'type': 'normal',
                'operation_template_id': operation_tmpl_id.id
            })
            bom_obj._get_operations()
            return bom_obj
    
    def _request_material(self, production_id):
        type_id = production_id.type_id
        location_id = type_id.picking_type_request_material_id.default_location_src_id.id
        location_dest_id = production_id.type_id.picking_type_request_material_id.default_location_dest_id.id
        picking_obj = self.env['stock.picking'].create({
            'picking_type_id' : type_id.picking_type_request_material_id.id,
            'location_id'     : location_id,
            'location_dest_id': location_dest_id,
            'mrp_request_id'  : production_id.request_id.id,
            'production_id'   : production_id.id,
            "origin"          : production_id.name,
            'move_ids_without_package': [(0, 0, {
                'name'            : raw.product_id.name,
                'product_id'      : raw.product_id.id,
                'product_uom_qty' : raw.product_uom_qty,
                'product_uom'     : raw.product_id.uom_id.id,
                'location_id'     : location_id,
                'location_dest_id': location_dest_id,
            }) for raw in production_id.move_raw_ids]
        })
        self.picking_ids = [(4, picking_obj.id)]


class ManufacturingRequestLine(models.Model):
    _name = 'mrp.request.line'
    
    name             = fields.Text(string='Description', )
    type_id          = fields.Many2one('mrp.production.type', string='Production Type',
        # compute="_get_production_type",
    )
    request_id       = fields.Many2one('mrp.request', string='Request')
    request_date     = fields.Datetime(string='Date',related="request_id.request_date",store=True,)
    order_id         = fields.Many2one('stock.point.order', string='Stock Point Order')
    production_id    = fields.Many2one('mrp.production', string='Production')
    product_id       = fields.Many2one('product.product', string='Product',domain=lambda self:self._get_domain())
    # default_code     = fields.Char(related='product_id.default_code', string='Code')
    line_product_id  = fields.Many2one('line.product', related='product_id.line_product_id',string='Line',store=True,)
    # product_categ_id = fields.Many2one(related='product_id.categ_id',string='Category')
    # capacity         = fields.Float(related='product_id.line_product_id.capacity',string='Capacity')
    product_uom_id   = fields.Many2one(related='product_id.uom_id', string='UoM',store=True,)
    # satuan_id        = fields.Many2one(related='product_id.satuan_id', string='Satuan Produksi',store=True,)
    # konversi_butir   = fields.Float(related='product_id.konversi_butir', string='Butir')
    # konversi_bungkus = fields.Float(related='product_id.konversi_bungkus', string='Bungkus')
    # product_qty_conv = fields.Float(string='Hasil Conv',compute="_get_spo_quantity",)
    # product_qty_est  = fields.Float(string='Request Produksi')
    # product_qty_est_conv  = fields.Float(string='Request Produksi Conv',compute="_get_spo_quantity",)
    # product_orig_id = fields.Many2one('product.product', string='Product',)
    # product_orig_id = fields.Many2one('product.product', string='Product',compute="_compute_product_orig_id",inverse="_set_product_orig_id")
    product_uom_qty  = fields.Float(string='Quantity',
    # compute="_get_spo_quantity"
    )
    product_qty      = fields.Float(string='Production Quantity',related="production_id.product_qty")
    # qty_onhand       = fields.Float(string='On Hand',compute="_compute_qty_onhand")
    display_type     = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    team = fields.Selection([("1","1"),("2","2"),("3","3")], string='Team')
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    design_id = fields.Many2one('makloon.design', string='Design')
    operation_template_id = fields.Many2one('mrp.operation.template', string='Operation Template')
    treatment_id = fields.Many2one('treatment', string='Treatment', 
    related='sale_line_id.treatment_id'
    )
    qty_produce = fields.Float(string='Qty Produce')
    shape = fields.Selection([("caplet","Caplet"),("round","Round")], string='Shape', related='sale_line_id.shape')
#     product_orig_id_domain = fields.Char(
#     compute="_compute_product_id_domain",
#     readonly=True,
#     store=False,
# )
    
    
    def _get_production_type(self):
        for line in self:
            production_type_id = self.env['mrp.production.type'].search([('finished_category_ids','in',line.product_categ_id.id)],limit=1)
            line.type_id = production_type_id.id

    # @api.depends('product_id')
    # def _compute_product_id_domain(self):
    #     for line in self:
    #         line.product_orig_id_domain = json.dumps(
    #             [('id', '!=', line.product_id.id),('id', 'in', line.request_id.line_ids.filtered(lambda x:x.line_product_id.id == line.line_product_id.id).mapped('product_id').ids), ('line_product_id', '=', line.line_product_id.id)]
    #         )
    
    @api.depends('product_id')
    def _compute_product_orig_id(self):
        for order in self:
            order.product_orig_id = order.move_finished_ids.filtered(lambda m: m.product_id != order.product_id)

    def _set_product_orig_id(self):
        move_finished_ids = self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id)
        self.move_finished_ids = move_finished_ids | self.move_byproduct_ids
    
    def _compute_qty_onhand(self):
        for line in self:
            domain = [('product_id', '=', line.product_id.id)]
            quant = self.env['stock.quant'].search(domain).mapped('quantity')
            line.qty_onhand = sum(quant)
    
    
    def _get_spo_quantity(self):
        for line in self:
            line.product_uom_qty = sum(line.request_id.order_lines.filtered(lambda l: l.product_id.id == line.product_id.id).mapped('quantity'))
            line.product_qty_conv = line.product_uom_qty / line.konversi_butir if line.product_uom_qty > 0 and line.konversi_butir > 0  else 0 
            line.product_qty_est_conv = line.product_qty_est * line.konversi_butir if line.product_qty_est > 0 and line.konversi_butir > 0  else 0 
    
    @api.model
    def create(self,values):
        if values.get('product_id'):
            values['name'] = self.env['product.product'].browse(values.get('product_id')).name
        return super(ManufacturingRequestLine,self).create(values)
    
    def _get_domain(self):
        domain = []
        ir_config             = self.env['ir.config_parameter'].sudo()
        filter_product        = ir_config.get_param('mor_filter_product')
        product_category_ids  = ir_config.get_param('mor_product_category_ids')
        if filter_product and product_category_ids:
            domain += [('categ_id','in', literal_eval(product_category_ids))]
        return domain
    
    def _get_domain_orig(self):
        domain = []
        ir_config             = self.env['ir.config_parameter'].sudo()
        filter_product        = ir_config.get_param('mor_filter_product')
        product_category_ids  = ir_config.get_param('mor_product_category_ids')
        if filter_product and product_category_ids:
            domain += [('categ_id','in', literal_eval(product_category_ids))]
        return domain
    
    

class ManufacturingRequestLineProduct(models.Model):
    _name = 'mrp.request.line.product'
    
    request_id       = fields.Many2one('mrp.request', string='Request')
    request_date     = fields.Datetime(string='Date',related="request_id.request_date",store=True,)
    line_product_id = fields.Many2one('line.product', string='Line Product')
    product_ids     = fields.Many2many(comodel_name='product.product', relation='mrp_request_line_product_rel',string='Product',compute="_get_product")
    # capacity        = fields.Float(string='Capacity',related="line_product_id.capacity")
    qty_conv        = fields.Float(string='Qty Conv',compute="_get_product")
    konversi_butir  = fields.Float(string='Conv Butir',compute="_get_product")
    qty_production  = fields.Float(string='Qty Request Production',compute="_get_product")
    qty_production_conv = fields.Float(string='Qty Production Conv',compute="_get_product")
    product_uom_id = fields.Many2one('uom.uom', string='Satuan')
    satuan_id      = fields.Many2one('satuan.produksi', string='Satuan Produksi')
    
    
    @api.depends('line_product_id')
    def _get_product(self):
        for line in self:
            product_ids = []
            for product in line.request_id.line_ids.filtered(lambda l:l.line_product_id == line.line_product_id):
                product_ids += [(4,product.product_id.id)]
            line.product_ids = product_ids
            line.qty_conv = sum([x.product_qty_conv for x in line.request_id.line_ids.filtered(lambda l:l.line_product_id == line.line_product_id)])
            line.qty_production_conv = sum([x.product_qty_est_conv for x in line.request_id.line_ids.filtered(lambda l:l.line_product_id == line.line_product_id)])
            line.qty_production = sum([x.product_qty_est for x in line.request_id.line_ids.filtered(lambda l:l.line_product_id == line.line_product_id)])
            line.konversi_butir = sum([x.konversi_butir for x in line.request_id.line_ids.filtered(lambda l:l.line_product_id == line.line_product_id)])
    
  
    class MrpProductionEstimated(models.Model):
        _name = 'mrp.production.estimated'
  
        name            = fields.Char(string='Estimated',related="request_id.name")
        request_id      = fields.Many2one('mrp.request', string='No Permintaan Produksi')
        type_id         = fields.Many2one('mrp.production.type', string='Tipe Produksi',compute="_get_production_type", )
        estimate_date   = fields.Date(string='Tanggal Estimasi', default=fields.Date.today())
        production_date = fields.Date(string='Tanggal Produksi', default=fields.Date.today())
        product_id      = fields.Many2one('product.product', string='Product')
        default_code    = fields.Char(related='product_id.default_code', string='Code')
        production_qty  = fields.Float(string='Qty Permintaan')
        product_uom_qty = fields.Float(string='Qty')
        qty_conv        = fields.Float(string='Konversi')
        qty_butir       = fields.Float(string='Butir')
        product_uom_id  = fields.Many2one(related='product_id.uom_id', string='Satuan')
        production_ids  = fields.Many2many(comodel_name='mrp.production', relation='mrp_production_estimated_rel',string='Kartu Produksi')
        satuan_id       = fields.Many2one('satuan.produksi', string='Satuan Produksi')
        production_count = fields.Float(compute='_compute_production', string='Jumlah Kartu', store=True)
        production_outstanding_qty = fields.Float(compute='_compute_production', string='Sisa Permintaan', store=True)
        
        @api.depends('production_ids')
        def _compute_production(self):
            for line in self:
                line.production_count = len(line.production_ids)
                line.production_outstanding_qty = line.production_qty - sum(line.production_ids.mapped('mrp_qty_produksi')) if len(line.production_ids) > 0 else  line.production_qty
        
        
        def open_production_wizard(self):
            return {
                'type': 'ir.actions.act_window',
                'name': 'Generate Production',
                'res_model': 'mrp.generate.production.wizard',
                'view_mode': 'form',
                'context':{'default_estimated_id':self.id,'default_mrp_request_id':self.request_id.id,"mo_outstanding_qty":self.production_outstanding_qty},
                'target': 'new',
            }
           
        
        
        def _get_production_type(self):
            for line in self:
                production_type_id = self.env['mrp.production.type'].search([('finished_category_ids','in',line.product_id.categ_id.id)],limit=1)
                line.type_id = production_type_id.id
