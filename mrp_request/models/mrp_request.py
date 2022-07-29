from odoo import models, fields, api, _
from odoo.exceptions import UserError
from ast import literal_eval


class ManufacturingRequest(models.Model):
    _name = 'mrp.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    

    name                = fields.Char(string='Manufacture Request',default=_('New'))
    order_ids           = fields.Many2many(comodel_name='stock.point.order', relation='mrp_request_stock_point_order_rel',string='Stock Point Order',domain=[('state', '=', 'confirm')])
    order_lines         = fields.Many2many(comodel_name='stock.point.order.line', string='Details Request',)
    # order_detail_lines  = fields.Many2many(comodel_name='stock.point.order.line', compute="_get_stock_point_order",string='Details Product Request',)
    request_date        = fields.Datetime(string='Request Date',default=fields.Datetime.now())
    user_id             = fields.Many2one('res.users', string='User',default=lambda self: self.env.user.id)
    line_ids            = fields.One2many('mrp.request.line', 'request_id', string='Details')
    note                = fields.Text(string='Note')
    picking_ids         = fields.Many2many(comodel_name='stock.picking', relation='mrp_request_stock_picking_rel',string='Transfer')
    picking_count       = fields.Integer(string='Transfer Count',compute="_compute_picking")
    state               = fields.Selection([('draft', 'Draft'),('confirm', 'Confirm'),('done', 'Done'),('cancel', 'Cancelled'),], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    
    def _compute_picking(self):
        for request in self:
            request.picking_count = len(request.picking_ids)
            
            
    def action_confirm(self):
        if self.name == 'New':
            ir_config        = self.env['ir.config_parameter'].sudo()
            mor_sequence_id  = ir_config.get_param('mor_sequence_id')
            if mor_sequence_id:
                seq = self.env['ir.sequence'].browse(int(mor_sequence_id)).next_by_id()
                self.name = seq
        self.state = 'confirm'
        
        
    def action_generate(self):
        if self.state in ('draft','confirm'):
            if self.line_ids:
                self.line_ids = False
            order_lines = []
            line_ids = self.order_lines.read_group([('mrp_request_id','=',self.id)],['quantity'],'product_id',lazy=False)
            for line in line_ids:
                order_lines += [(0,0,{"product_id":line.get('product_id')[0]})]
            self.line_ids = order_lines
                
        
        
    def action_done(self):
        self.state = 'done'
        
    def action_back_to_draft(self):
        self.state = 'draft'
        
        
    
    
    def _get_stock_point_order(self):
        for request in self:
            request.order_lines = [(4,line.id) for order in request.order_ids  for line in order.line_ids]
            
    
    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action['domain'] = [('picking_id','in',self.picking_ids.ids)]
        action['context'] = {}
        return action
    
    


class ManufacturingRequestLine(models.Model):
    _name = 'mrp.request.line'
    
    name            = fields.Text(string='Description', )
    request_id      = fields.Many2one('mrp.request', string='Request')
    order_id        = fields.Many2one('stock.point.order', string='Stock Point Order')
    production_id   = fields.Many2one('mrp.production', string='Production')
    product_id      = fields.Many2one('product.product', string='Product',domain=lambda self:self._get_domain())
    default_code    = fields.Char(related='product_id.default_code', string='Code')
    line_product_id  = fields.Many2one('line.product', related='product_id.line_product_id',string='Line')
    product_uom_id  = fields.Many2one(related='product_id.uom_id', string='Satuan')
    satuan_id       = fields.Many2one(related='product_id.satuan_id', string='Satuan Produksi')
    konversi_butir  = fields.Float(related='product_id.konversi_butir', string='Butir')
    konversi_bungkus = fields.Float(related='product_id.konversi_bungkus', string='Bungkus')
    product_qty_conv = fields.Float(string='Hasil Conv',compute="_get_spo_quantity")
    product_qty_est  = fields.Float(string='Request Produksi')
    product_orig_ids = fields.Many2one('product.product', string='Product',domain=lambda self:self._get_domain())
    product_uom_qty = fields.Float(string='Quantity',compute="_get_spo_quantity")
    product_qty     = fields.Float(string='Production Quantity',related="production_id.product_qty")
    display_type    = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    
    def _get_spo_quantity(self):
        for line in self:
            line.product_uom_qty = sum(line.request_id.order_lines.filtered(lambda l: l.product_id.id == line.product_id.id).mapped('quantity'))
            line.product_qty_conv = line.product_uom_qty / line.konversi_butir if line.product_uom_qty > 0 and line.konversi_butir > 0  else 0 
    
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