import re
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from collections import defaultdict
from datetime import datetime
from ast import literal_eval
from odoo.tools.misc import format_date, OrderedSet
from odoo.tools.float_utils import float_compare, float_is_zero, float_round





_STATE = [
    ("draft", "Draft"),
    ("confirm", "Confirm"),
    ("delivery", "On Delivery"),
    ("delivered", "Delivered"),
    ("done", "Done"),
    ("cancel", "Cancelled"),
]

class DoHeadOffice(models.Model):
    _name = 'do.head.office'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    

    name                      = fields.Char(string='DO',default=_('New'),copy=False,required=True, )
    order_date                = fields.Datetime(string='Date', default=fields.Datetime.now(),required=True,)
    date_done                 = fields.Datetime(string='Date Done')
    company_id                = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    default_warehouse_src_id  = fields.Many2one('stock.warehouse', string='From',required=True, domain=lambda self: self._get_domain_warehouse(), default=lambda self: self._get_default_warehouse())
    default_warehouse_dest_id = fields.Many2one('stock.warehouse', string='To',required=True,domain=[('is_stock_point', '=', True)])
    location_id               = fields.Many2one('stock.location', string='Location',related="default_warehouse_dest_id.lot_stock_id")
    order_id                  = fields.Many2one('stock.point.order', string='Order')
    order_ids                 = fields.Many2many(comodel_name='stock.point.order', relation='stock_order_point_do_ho_rel',string='Stock Point Order')
    picking_type_id           = fields.Many2one('stock.picking.type', string='Stock Picking Type',domain=[('warehouse_id', '=', default_warehouse_src_id)])
    driver_id                 = fields.Many2one('hr.employee', string='Driver',required=True, )
    user_id                   = fields.Many2one('res.users', string='User',default=lambda self: self.env.user.id,readonly=True)
    salesman_id               = fields.Many2one('res.users', string='Salesman',)
    vehicle_id                = fields.Many2one('fleet.vehicle', string='Vehicle',required=True, )
    do_lines                  = fields.One2many('do.head.office.line', 'do_id', string='Details DO')
    line_ids                  = fields.One2many('do.head.office.line', 'do_id', string='Details',compute="_compute_line_ids",inverse="_set_line_ids")
    line_fg_ids               = fields.One2many('do.head.office.line.fg', 'do_id', string='Finish Goods')
    line_siba_ids             = fields.One2many('do.head.office.line.siba', 'do_id', string='SIBA')
    line_return_ids           = fields.One2many('do.head.office.line.return', 'do_id', string='Return')
    picking_ids               = fields.Many2many('stock.picking', relation='do_transfer_rel',string='Transfer')
    return_picking_ids        = fields.Many2many('stock.picking', relation='do_return_transfer_rel',string='Return Transfer')
    fg_amount                 = fields.Float(string='FG count',compute="_compute_all_product")
    siba_amount               = fields.Float(string='Siba count',compute="_compute_all_product")
    return_amount             = fields.Float(string='Return count',compute="_compute_all_product")
    amount_quantity           = fields.Float(string='Total Quantity',compute="_compute_all_product")
    picking_count             = fields.Integer(compute='_compute_picking', string='Picking Count', store=False)
    picking_return_count      = fields.Integer(compute='_compute_picking', string='Return Picking Count', store=False)
    state                     = fields.Selection(selection=_STATE, string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    
    
    def _compute_all_product(self):
        for do in self:
            do.fg_amount = sum(do.line_fg_ids.mapped('quantity'))
            do.siba_amount = sum(do.line_siba_ids.mapped('quantity'))
            do.return_amount = sum(do.line_return_ids.mapped('quantity'))
            do.amount_quantity = sum(do.do_lines.mapped('quantity'))
        

    #todo
    ########################################################################
    ### 
    ### 1. buat picking return saat validate transfer truck ke stock point
    ### 2. tambah expense
    ### 
    ########################################################################
    
    # def _create_picking_return(self):
    #     if self.picking_count == 0:
    #         picking = se
    
    
    
    def _get_line_ids(self):
        self.ensure_one()
        line_ids = self.env['do.head.office.line']
        line_ids = self.do_lines
        return line_ids
    
    
    @api.depends('state', 'do_lines', 'do_lines.quantity')
    def _compute_line_ids(self):
        for do in self:
            do.line_ids = do._get_line_ids()
        
    
    def do_line_group_by_product(self):
        query = """ 
                SELECT pt.name as product_id,uo.name as uom_id,sum(dol.quantity) as quantity
                FROM do_head_office_line dol
                LEFT JOIN product_product pp on dol.product_id = pp.id
                LEFT JOIN product_template pt on pp.product_tmpl_id = pt.id
                LEFT JOIN uom_uom uo on pt.uom_id = uo.id 
                WHERE do_id = %s
                GROUP BY pt.name,uo.name
                ORDER BY pt.name,quantity desc
                """%(self.id)
        self._cr.execute(query)
        results = self._cr.dictfetchall()
        return results
    
    
    def _set_line_ids(self):
        new_line = self[0].line_ids
        for do in self.line_ids:
            old_mwp = do._get_line_ids()
            do.do_lines = (do.do_lines - old_mwp) | new_line
            moves_to_unlink = old_mwp - new_line
            if moves_to_unlink:
                moves_to_unlink.unlink()

   
                    
    @api.depends('picking_ids')
    def _compute_picking(self):
        for order in self:
            order.picking_count = len(order.picking_ids)
            
            
    @api.onchange('default_warehouse_src_id')
    def get_picking_type(self):
        if self.default_warehouse_src_id:
            self.picking_type_id = self.env['stock.picking.type'].sudo().search([('warehouse_id','=',self.default_warehouse_src_id.id),('code','=','internal'),('default_location_siba_id','!=',False)],limit=1).id
    
            
    def _get_domain_warehouse(self):
        domain = []
        ir_config             = self.env['ir.config_parameter'].sudo()
        filter_warehouse      = ir_config.get_param('do_filter_warehouse')
        do_warehouse_src_ids  = ir_config.get_param('do_warehouse_src_ids')
        if self.user_has_groups('do_head_office.group_do_head_office_user') and self.env.user.default_warehouse_ids:
            if filter_warehouse and do_warehouse_src_ids:
                if len(self.env.user.default_warehouse_ids) == 1:
                    domain += [('id','=', self.env.user.default_warehouse_ids[0].id)]
                else:
                    domain += [('id','in', literal_eval(do_warehouse_src_ids))]
                    
        elif self.user_has_groups('do_head_office.group_do_head_office_manager'):
            if filter_warehouse and do_warehouse_src_ids:
                domain += [('id','in', literal_eval(do_warehouse_src_ids))]
        return domain
    
    def _get_default_warehouse(self):
        if self.user_has_groups('do_head_office.group_do_head_office_user') and self.env.user.default_warehouse_ids:
            if len(self.env.user.default_warehouse_ids) == 1:
                return self.env.user.default_warehouse_ids.id
            else:
                return self.env.user.default_warehouse_ids[0].id
    
    

    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        action['domain'] = [('id','in',self.picking_ids.ids)]
        action['context'] = {}
        return action
    
    def action_confirm(self):
        if self.name == 'New':
            seq = self.env['ir.sequence'].next_by_code('do.head.office.sequence')
            self.name = seq
        if len(self.picking_ids) == 0:
            self.create_picking()
        self.state = 'confirm'
        
    
    
    def _create_vehicle_picking(self,procure_stock):
        ir_config               = self.env['ir.config_parameter'].sudo()
        vehicle_picking_type_id = ir_config.get_param('vehicle_picking_type_id')
        
        if not vehicle_picking_type_id:
                raise UserError('Mohon maaf operation Delivery belum ditentukan')
            
        if procure_stock == 'fg':
            vehicle_fg = self.env['stock.picking'].create({
                'picking_type_id': int(vehicle_picking_type_id),
                'date': self.order_date,
                'do_id': self.id,
                'scheduled_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'origin': self.name,   
                'location_id': self.vehicle_id.fg_stock_location_id.id,
                'vehicle_id':self.vehicle_id.id,
                'location_dest_id': self.location_id.id,
                'immediate_transfer': False,
                'move_ids_without_package': [(0,0,{ 'name': line.product_id.name,
                        'description_picking': line.do_id.name,
                        'product_id'        : line.product_id.id,
                        'product_uom'       : line.product_uom_id.id,
                        'product_uom_qty'   : line.quantity,
                        'x_ket'             : line.do_id.name,
                        'date'              : self.order_date,
                        'location_id'       : self.vehicle_id.fg_stock_location_id.id, 
                        'location_dest_id'  : self.location_id.id,
                        'state'             : 'draft',
                        'company_id'        : self.env.company.id,
                        'price_unit'        : line.product_id.standard_price,
                        'picking_type_id'   : int(vehicle_picking_type_id),
                        'origin'            : self.name,
                        'warehouse_id'      : self.default_warehouse_src_id.id,
                    }) for line in self.line_fg_ids]
                })
            
            if vehicle_fg.id:
                self.picking_ids = [(4,vehicle_fg.id)]
                
                
        elif procure_stock == 'siba':
            dest_location = self.env['stock.picking.type'].\
                search([('warehouse_id','=',self.default_warehouse_dest_id.id),('default_location_siba_id','!=',False),('is_stock_point','=',True)],limit=1)
            
            if not dest_location:
                raise UserError('Mohon maaf operation type %s \n Lokasi Sibanya stock belum ditentukan'%(self.default_warehouse_dest_id.name ))
            
            vehicle_siba = self.env['stock.picking'].create({
                'picking_type_id': int(vehicle_picking_type_id),
                'date': self.order_date,
                'scheduled_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'origin': self.name,   
                'do_id': self.id,
                'procure_stock':'siba',
                'location_id' : self.vehicle_id.siba_stock_location_id.id, 
                'vehicle_id':self.vehicle_id.id,
                'location_dest_id': dest_location.default_location_siba_id.id,
                'immediate_transfer': False,
                'move_ids_without_package': [(0,0,{ 'name': line.product_id.name,
                        'description_picking': line.do_id.name,
                        'product_id'        : line.product_id.id,
                        'product_uom'       : line.product_uom_id.id,
                        'product_uom_qty'   : line.quantity,
                        'x_ket'             : line.do_id.name,
                        'date'              : self.order_date,
                        'location_id'       : self.vehicle_id.siba_stock_location_id.id, 
                        'location_dest_id'  : dest_location.default_location_siba_id.id,
                        'state'             : 'draft',
                        'company_id'        : self.env.company.id,
                        'price_unit'        : line.product_id.standard_price,
                        'picking_type_id'   : int(vehicle_picking_type_id),
                        'origin'            : self.name,
                        'warehouse_id'      : self.default_warehouse_src_id.id,
                    }) for line in self.line_siba_ids]
            })
            
                    
            if vehicle_siba.id:
                self.picking_ids = [(4,vehicle_siba.id)]
            
        
        
    
        
    def create_picking(self):
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self.line_ids:
            if float_is_zero(line.quantity,precision_digits=precision_digits):
                raise UserError('Mohon maaf pastikan %s \nquantity product yang akan dikirim tidak nol'%(line.product_id.name))
            
            
        if self.line_fg_ids:
            picking_fg = self.env['stock.picking'].create({
                'picking_type_id': self.picking_type_id.id,
                'date': self.order_date,
                'do_id': self.id,
                'scheduled_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'origin': self.name,   
                'procure_stock':'fg',
                'location_id': self.picking_type_id.default_location_src_id.id,
                'vehicle_id':self.vehicle_id.id,
                'location_dest_id': self.vehicle_id.fg_stock_location_id.id,
                'immediate_transfer': False,
                'move_ids_without_package': [(0,0,{ 'name': line.product_id.name,
                        'description_picking': line.do_id.name,
                        'product_id'        : line.product_id.id,
                        'product_uom'       : line.product_uom_id.id,
                        'product_uom_qty'   : line.quantity,
                        'x_ket'             : line.do_id.name,
                        'date'              : self.order_date,
                        'location_id'       : self.picking_type_id.default_location_src_id.id, 
                        'location_dest_id'  : self.vehicle_id.fg_stock_location_id.id,
                        'state'             : 'draft',
                        'company_id'        : self.env.company.id,
                        'price_unit'        : line.product_id.standard_price,
                        'picking_type_id'   : self.picking_type_id.id,
                        'origin'            : self.name,
                        'warehouse_id'      : self.default_warehouse_src_id.id,
                    }) for line in self.line_fg_ids]
            })
            
            if picking_fg.id:
                self.picking_ids = [(4,picking_fg.id)]
        
        
        if self.line_siba_ids:
            picking_siba = self.env['stock.picking'].create({
                'picking_type_id': self.picking_type_id.id,
                'date': self.order_date,
                'scheduled_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'origin': self.name,   
                'do_id': self.id,
                'procure_stock':'siba',
                'location_id': self.picking_type_id.default_location_siba_id.id,
                'vehicle_id':self.vehicle_id.id,
                'location_dest_id': self.vehicle_id.siba_stock_location_id.id,
                'immediate_transfer': False,
                'move_ids_without_package': [(0,0,{ 'name': line.product_id.name,
                        'description_picking': line.do_id.name,
                        'product_id'        : line.product_id.id,
                        'product_uom'       : line.product_uom_id.id,
                        'product_uom_qty'   : line.quantity,
                        'x_ket'             : line.do_id.name,
                        'date'              : self.order_date,
                        'location_id'       : self.picking_type_id.default_location_siba_id.id, 
                        'location_dest_id'  : self.vehicle_id.siba_stock_location_id.id,
                        'state'             : 'draft',
                        'company_id'        : self.env.company.id,
                        'price_unit'        : line.product_id.standard_price,
                        'picking_type_id'   : self.picking_type_id.id,
                        'origin'            : self.name,
                        'warehouse_id'      : self.default_warehouse_src_id.id,
                    }) for line in self.line_siba_ids]
            })
            
                    
            if picking_siba.id:
                self.picking_ids = [(4,picking_siba.id)]
            
    
        
    def action_done(self):
        self.state = 'done'
        
        
    def action_cancel(self):
        self.state = 'cancel'
        
        
    def action_draft(self):
        if len( self.picking_ids) > 0:
            self.picking_ids.unlink()
        
        self.state = 'draft'
        
        

class DoHeadOfficeLine(models.Model):
    _name = 'do.head.office.line'
    
    do_id          = fields.Many2one('do.head.office', string='DO')
    lot_id         = fields.Many2one('stock.production.lot', string='Lot')
    fg_id          = fields.Many2one('do.head.office.line.fg', string='FG ID')
    siba_id        = fields.Many2one('do.head.office.line.siba', string='SIBA ID')
    type           = fields.Selection([("fg","Finish Good"),("siba","Siba")], string='Type')
    product_id     = fields.Many2one('product.product', string='Product',domain=lambda self:self._get_domain())
    product_uom_id = fields.Many2one( related='product_id.uom_id', string='Satuan')
    quantity       = fields.Float(string='Quantity')
    
    
        
    def _recompute_lines(self):
        lines_to_write = defaultdict(OrderedSet)
        for line in self:
            lines_to_write.add(line.id)
    
    def _get_domain(self):
        domain = []
        ir_config             = self.env['ir.config_parameter'].sudo()
        filter_product        = ir_config.get_param('do_filter_product')
        product_category_ids  = ir_config.get_param('do_product_category_ids')
        if filter_product and product_category_ids:
            domain += [('categ_id','in', literal_eval(product_category_ids))]
        return domain
            
    
    
class DoHeadOfficeLineFg(models.Model):
    _name = 'do.head.office.line.fg'
    
    
    
    
    
    do_id           = fields.Many2one('do.head.office', string='DO')
    lot_id          = fields.Many2one('stock.production.lot', string='Lot')
    line_id         = fields.Many2one('do.head.office.line', string='Line')
    location_id     = fields.Many2one('stock.location', string='Location',related="do_id.picking_type_id.default_location_src_id")
    qty_onhand      = fields.Float(string='On Hand',compute="_compute_qty_onhand")
    product_id      = fields.Many2one('product.product', string='Product',domain=lambda self:self._get_domain())
    product_uom_id  = fields.Many2one( related='product_id.uom_id', string='Satuan')
    quantity        = fields.Float(string='Quantity')
    
    
    @api.model
    def create(self, vals):
        if vals.get('product_id'):
            do_line = self.env['do.head.office.line'].create({
                "do_id":vals.get('do_id'),
                "fg_id":self._origin.id,
                "type":"fg",
                "product_id":vals.get('product_id'),
                "quantity":vals.get('quantity')
                
            })
            vals['line_id'] = do_line.id
            
        return super(DoHeadOfficeLineFg, self).create(vals)
    
    
    @api.model
    def write(self, vals):
        product_id = vals.get('product_id') if vals.get('product_id') is not None else self.product_id.id
        quantity = vals.get('quantity') if vals.get('quantity') is not None else self.quantity
        line_id = vals.get('line_id') or self.line_id
        if product_id or quantity:
            do_line = self.env['do.head.office.line'].search([("do_id",'=',self.do_id.id),("id",'=',line_id.id),("type","=","fg")])
            if  do_line:
                do_line.write({
                    "quantity":quantity,
                    "product_id":product_id,
                })
        return super(DoHeadOfficeLineFg, self).write(vals)
    
    @api.model
    def unlink(self):
        self.mapped('line_id').unlink()
        res = super(DoHeadOfficeLineFg, self).unlink()
        return res


    
    
    @api.depends('product_id')
    def _compute_qty_onhand(self):
        for line in self:
            domain = [('product_id', '=', line.product_id.id), ('location_id', '=', line.do_id.picking_type_id.default_location_src_id.id)]
            quant = self.env['stock.quant'].search(domain).mapped('quantity')
            line.qty_onhand = sum(quant)
    
    
    def _get_domain(self):
        domain = []
        ir_config             = self.env['ir.config_parameter'].sudo()
        filter_product        = ir_config.get_param('do_filter_product')
        product_category_ids  = ir_config.get_param('do_product_category_ids')
        if filter_product and product_category_ids:
            domain += [('categ_id','in', literal_eval(product_category_ids))]
        return domain
    
   
    
    
class DoHeadOfficeLineSiba(models.Model):
    _name = 'do.head.office.line.siba'
    
    
    do_id           = fields.Many2one('do.head.office', string='DO')
    lot_id          = fields.Many2one('stock.production.lot', string='Lot')
    line_id         = fields.Many2one('do.head.office.line', string='Line')
    picking_type_id = fields.Many2one('stock.picking_type', string='Picking Type')
    product_id      = fields.Many2one('product.product', string='Product',domain=lambda self:self._get_domain())
    qty_onhand      = fields.Float(string='On Hand',compute="_compute_qty_onhand")
    product_uom_id = fields.Many2one( related='product_id.uom_id', string='Satuan')
    quantity       = fields.Float(string='Quantity')
    
    
    @api.model
    def create(self, vals):
        if vals.get('product_id'):
            do_line = self.env['do.head.office.line'].create({
                "do_id":vals.get('do_id'),
                "siba_id":self._origin.id,
                "type":"siba",
                "product_id":vals.get('product_id'),
                "quantity":vals.get('quantity')
                
            })
            vals['line_id'] = do_line.id
            
        return super(DoHeadOfficeLineSiba, self).create(vals)
    
    
    
    @api.model
    def write(self, vals):
        product_id = vals.get('product_id') if vals.get('product_id') is not None else self.product_id.id
        quantity = vals.get('quantity') if vals.get('quantity') is not None else self.quantity
        line_id = vals.get('line_id') or self.line_id
        if product_id or quantity:
            do_line = self.env['do.head.office.line'].search([("do_id",'=',self.do_id.id),("id",'=',line_id.id),("type","=","siba")])
            if  do_line:
                do_line.write({
                    "quantity":quantity,
                    "product_id":product_id,
                })
        return super(DoHeadOfficeLineSiba, self).write(vals)
    
    
    @api.model
    def unlink(self):
        self.mapped('line_id').unlink()
        res = super(DoHeadOfficeLineSiba, self).unlink()
        return res

    
    
    @api.depends('product_id')
    def _compute_qty_onhand(self):
        for line in self:
            domain = [('product_id', '=', line.product_id.id), ('location_id', '=', line.do_id.picking_type_id.default_location_siba_id.id)]
            quant = self.env['stock.quant'].search(domain).mapped('quantity')
            line.qty_onhand = sum(quant)
    
       
    def _get_domain(self):
        domain = []
        ir_config             = self.env['ir.config_parameter'].sudo()
        filter_product        = ir_config.get_param('do_filter_product')
        product_category_ids  = ir_config.get_param('do_product_category_ids')
        if filter_product and product_category_ids:
            domain += [('categ_id','in', literal_eval(product_category_ids))]
        return domain
    
    
    
class DoHeadOfficeLineReturn(models.Model):
    _name = 'do.head.office.line.return'
    
    
    do_id           = fields.Many2one('do.head.office', string='DO')
    lot_id          = fields.Many2one('stock.production.lot', string='Lot')
    picking_type_id = fields.Many2one('stock.picking_type', string='Picking Type')
    product_id      = fields.Many2one('product.product', string='Product',domain=lambda self:self._get_domain())
    product_uom_id  = fields.Many2one( related='product_id.uom_id', string='Satuan')
    quantity        = fields.Float(string='Quantity')
    
    
    
    def _get_domain(self):
        domain = []
        ir_config             = self.env['ir.config_parameter'].sudo()
        filter_product        = ir_config.get_param('do_filter_product')
        product_category_ids  = ir_config.get_param('do_product_category_ids')
        if filter_product and product_category_ids:
            domain += [('categ_id','in', literal_eval(product_category_ids))]
        return domain
    
