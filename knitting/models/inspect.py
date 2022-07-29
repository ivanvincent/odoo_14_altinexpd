from odoo import models, fields, api, _ ,tools
from odoo.exceptions import UserError
from datetime  import datetime
import logging
_logger = logging.getLogger(__name__)

class ProduksiInspect(models.Model):
    _name = 'produksi.inspect'
    _description = 'Product Inspect'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    
    _sql_constraints = [
        ('production_uniq', 'unique(production_id)', 'Production harus unik !')
    ]
    
    
    
    @api.depends('picking_ids')
    def _compute_picking(self):
        for inspect in self:
            pickings = self.env['stock.picking'].search([('inspect_id','=',inspect.id)])
            inspect.picking_count = len(pickings)
            inspect.picking_ids = pickings
            
    @api.depends('produced_qty','production_qty')
    def _compute_qty_produced(self):
        for inspect in self:
            inspect.production_has_finish = True if inspect.produced_qty >= inspect.production_qty else False
            
    
    @api.depends('moveline_before_ids')
    def _compute_inspecting(self):
        for line in self:
            line.inspecting_count = len(line.moveline_before_ids.filtered(lambda x: x.state == 'inspecting'))
            line.transferred_count = len(line.moveline_before_ids.filtered(lambda x: x.state == 'transfer'))
            line.produced_count = len(line.moveline_before_ids.filtered(lambda x: x.state == 'produced'))
            line.to_return = line.produced_count > 0
            line.remaining_qty = line.production_qty - line.total_quantity
            
            
    @api.depends('production_id')
    def _get_barcode_greige(self):
        for line in self:
            if len(line.production_id.move_raw_ids.filtered(lambda x:x.product_id.categ_id.name == "GREY")) > 0 :
                for move in line.production_id.move_raw_ids.filtered(lambda x:x.product_id.categ_id.name == "GREY"):
                    line.move_raw_line_ids = move.move_line_ids
            else:
                line.move_raw_line_ids = False
            
            
            
    

    name                  = fields.Char(string='Name')
    state                 = fields.Selection([('draft', 'Draft'),('confirm', 'Confirm'),('done','Done')], string='Status', default='draft')
    inspect_ids           = fields.One2many('produksi.inspect.line', 'inspect_id', string='Inspect Line')
    inspect_category      = fields.Selection([("new","New"),("reinspect","Re - Inspect"),("emboss","Emboss")], string='Category',defaut="new")
    inspect_type          = fields.Selection([("generate","Generate"),("base_grege","Based On Greige")], string='Inspect Type',default="generate")
    quantity_gen          = fields.Float(string='Generate Quantity')
    amount_gen_roll       = fields.Integer(string='Amount')  
    production_id         = fields.Many2one('mrp.production', string='Production',required=True, domain=[('is_inspected', '=', False)])
    product_id            = fields.Many2one(related='production_id.product_id', string='Product')
    product_uom_id        = fields.Many2one(related='product_id.uom_id', string='Uom')
    production_qty        = fields.Float(related='production_id.product_qty', string='Production Quantity')
    produced_qty          = fields.Float(related='production_id.qty_produced', string='Produced Quantity')
    location_id           = fields.Many2one('stock.location', string='Location',related="production_type_id.finished_location")
    picking_ids           = fields.Many2many(comodel_name='stock.picking',compute='_compute_picking', string='Transfer')
    picking_count         = fields.Integer(compute='_compute_picking', string='Picking count', default=0,)
    inspecting_count      = fields.Float(compute='_compute_inspecting', string='Inspecting', store=False)
    transferred_count     = fields.Float(compute='_compute_inspecting', string='Transfer', store=False)
    produced_count        = fields.Float(compute='_compute_inspecting', string='Produced', store=False)
    remaining_qty         = fields.Float(compute='_compute_inspecting', string='Remaining', store=False)
    production_has_finish = fields.Boolean(string='Production Has Finish ?',compute='_compute_qty_produced')
    production_type_id    = fields.Many2one('mrp.type', string='Production Type',related="production_id.type_id")
    allowed_over_qty      = fields.Float(compute='_compute_over_quantity', string='Over Quantity', store=False)
    lot_producing_id      = fields.Many2one(related='production_id.lot_producing_id', string='Lot Production')
    
    @api.depends('moveline_before_ids')
    def _compute_over_quantity(self):
        for line in self:
            allowed_over_qty = line.production_qty * line.allowed_over_qty_percentage / 100
            allowed_over_qty = line.production_qty + allowed_over_qty
            line.allowed_over_qty = allowed_over_qty
    
    allowed_over_qty_percentage      = fields.Float(string='Allowed Over Quantity',related="production_type_id.allowed_over_qty_percentage")
    moveline_before_ids   = fields.One2many('stock.move.line.before', 'inspect_id', string='Stock Move Line Before')
    move_raw_line_ids     = fields.Many2many('stock.move.line', string='Barcode Greige',compute="_get_barcode_greige")
    date                  = fields.Date(string='Date' ,default=fields.Date.today())
    employee_id           = fields.Many2one('hr.employee', string='Employee')
    tot_roll              = fields.Integer(string='Total Roll', compute='_compute_quantity_all',)
    total_quantity        = fields.Float(string='Total Quantity', compute='_compute_quantity_all',)
    keterangan            = fields.Text(string='Keterangan')
    to_return             = fields.Boolean(string='Allow for return ?',compute='_compute_inspecting')
    
    
    
    
    
    @api.constrains('moveline_before_ids')
    def _check_quantity(self):
        for line in self:
            if line.total_quantity > line.allowed_over_qty:
                raise UserError('Quantity Inspect more then Allowed Over Quantity')

    def action_transfer(self):
        form_view = self.env.ref('knitting.inspect_transfer_wizard_form')
        
        return {
            'res_model': 'inspect.transfer.wizard',
            'type': 'ir.actions.act_window',
            'name': _("Transfer"),
            'views': [(form_view.id, 'form')],
            'context': {
                'active_model': 'produksi.inspect',
                'active_id': self.id,
                'default_inspect_id':self.id,
            },
            'view_mode': 'form',
            'target':'new'
        }
        
        
    def action_return_production(self):
        form_view = self.env.ref('knitting.inspect_return_wizard')
        
        return {
            'res_model': 'inspect.return.wizard',
            'type': 'ir.actions.act_window',
            'name': _("Return"),
            'views': [(form_view.id, 'form')],
            'context': {
                'active_model': 'produksi.inspect',
                'active_id': self.id,
                'default_inspect_id':self.id,
                'default_production_id':self.production_id.id,
            },
            'view_mode': 'form',
            'target':'new'
        }
        
    
    def _prepare_move_default_values(self,return_line):
        vals = {
            'product_id': return_line.product_id.id,
            'product_uom_qty': return_line.quantity,
            'product_uom': return_line.product_id.uom_id.id,
            'state': 'draft',
            'date': fields.Datetime.now(),
            'location_id': return_line.move_id.location_dest_id.id,
            'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
            'picking_type_id': return_line.picking_type_id.id,
            'warehouse_id': self.picking_id.picking_type_id.warehouse_id.id,
            'origin_returned_move_id': return_line.move_id.id,
            'procure_method': 'make_to_stock',
        }
        return vals
        
        
    def action_cancel_production(self):
        self.ensure_one()
        move_out_line_ids = []
        for move in self.moveline_before_ids.filtered(lambda x:x.state == 'produced'):
            move_out_line_ids.append((0,0,{
                        'product_id': move.lot_id.product_id.id,
                        'lot_id': move.lot_id.id,
                        'grade_id': move.lot_id.grade_id.id,
                        'product_uom_id': move.lot_id.product_id.uom_id.id,
                        'qty_done': move.quantity,
                        # 'product_uom_qty':move.quantity,
                        'company_id':self.env.company.id,
                        "location_id":self.location_id.id,
                        "location_dest_id":15,
                    }))
            
            move.write({"state":'inspecting'})
            
        stock_picking_in = self.env['stock.picking'].sudo().create({
            "picking_type_id": self.production_id.type_id.inspect_picking_type_id.warehouse_id.in_type_id.id,
            'location_id': 15,
            "origin": "CANCELLED PRODUCE",
            "location_dest_id": self.lot_producing_id.location_id.id,
            'move_line_ids_without_package':[(0,0,{
                    'product_id': self.lot_producing_id.product_id.id,
                    'lot_id': self.lot_producing_id.id,
                    'grade_id': self.lot_producing_id.grade_id.id,
                    'product_uom_id': self.lot_producing_id.product_id.uom_id.id,
                    'qty_done': sum([move.get('qty_done') for *x,move in move_out_line_ids]),
                    'company_id':self.env.company.id,
                    'location_id': 15,
                    "location_dest_id":self.lot_producing_id.location_id.id,
            })],
        })
        
      
        
        stock_picking_out = self.env['stock.picking'].sudo().create({
            "picking_type_id": self.production_id.type_id.inspect_picking_type_id.warehouse_id.out_type_id.id,
            'location_id': self.location_id.id,
            "location_dest_id": 15,
            "origin": "CANCELLED PRODUCE ",
            'move_line_ids_without_package':move_out_line_ids,
           
        })
        _logger.warning('='*40)
        _logger.warning('cancel_produce')
        _logger.warning(stock_picking_out)
        _logger.warning(stock_picking_in)
        _logger.warning('='*40)
        
        
        
        if stock_picking_in and stock_picking_out:
                stock_picking_in.action_confirm()
                stock_picking_in.action_assign()
                stock_picking_in.button_validate()
                stock_picking_out.action_confirm()
                stock_picking_out.action_assign()
                stock_picking_out.button_validate()
                
                _logger.warning('='*40)
                _logger.warning('cancel_produce')
                _logger.warning(stock_picking_out)
                _logger.warning(stock_picking_in)
                _logger.warning('='*40)
        
        
    def action_view_picking(self):
        result = self.env["ir.actions.actions"]._for_xml_id('stock.action_picking_tree_all')
        pick_ids = self.mapped('picking_ids')
        # choose the view_mode accordingly
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
    
    
    def action_produce(self):
        self.ensure_one()
        move_in_line_ids = []
        
        inspecting = self.moveline_before_ids.filtered(lambda x:x.state == "inspecting")
        for line in inspecting:
            # lot_name = self.env['ir.sequence'].next_by_code('stock.production.lot.gdj')
            new_lot = self.env['stock.production.lot'].sudo().create({
            "name":line.lot_name,
            "product_id":line.product_id.id,
            "product_category":line.product_id.categ_id.id,
            "location_id":self.location_id.id,
            "production_id":self.production_id.id,
            "product_uom_id":line.product_id.uom_id.id,
            "inspect_id":line.inspect_id.id,
            "ref":line.inspect_id.name,
            "inspect_date":fields.Date.today(),
            "tanggal_produksi":self.lot_producing_id.tanggal_produksi,
            "company_id":self.env.company.id,
            "grade_id": line.grade_id.id ,
            "lebar": self.lot_producing_id.lebar  or False,
            "pic": self.lot_producing_id.pic  or False,
            "move_line_ids": [(0,0,{
                "name":line.product_id.name,
                "product_id":self.lot_producing_id.product_id.id,
                "lot_parent_name": self.lot_producing_id.product_id.name,
                "location_id":self.lot_producing_id.location_id.id,
                "quantity":self.lot_producing_id.product_qty,
                "state":"split",
            })]
        
            })
            line.write({"state":"produced","lot_id": new_lot.id})
            
            move_in_line_ids.append((0,0,{
                        'product_id': new_lot.product_id.id,
                        'lot_id': new_lot.id,
                        'grade_id': new_lot.grade_id.id,
                        # 'lot_name': new_lot.name,
                        # 'lot_name': line.lot_id.name,
                        'product_uom_id': new_lot.product_id.uom_id.id,
                        'qty_done': line.quantity,
                        'product_uom_qty':line.quantity,
                        'company_id':self.env.company.id,
                        "location_id":15,
                        "location_dest_id":self.location_id.id,
                    }))
            
        # move_out_line_ids.append()
        
        
        stock_picking_in = self.env['stock.picking'].sudo().create({
            "picking_type_id": self.production_id.type_id.inspect_picking_type_id.warehouse_id.in_type_id.id,
            'location_id': 15,
            "origin": "INSPECT BARCODE ",
            "location_dest_id":self.location_id.id,
            'move_line_ids_without_package':move_in_line_ids,
        })
        
      
        
        stock_picking_out = self.env['stock.picking'].sudo().create({
            "picking_type_id": self.production_id.type_id.inspect_picking_type_id.warehouse_id.out_type_id.id,
            # "picking_type_id": self.production_id.type_id.inspect_picking_type_id.warehouse_id.out_type_id.id,
            'location_id': self.location_id.id,
            # 'location_id': self.lot_producing_id.location_id.id,
            "origin": "SPLIT BARCODE ",
            "location_dest_id":15,
            'move_line_ids_without_package':[(0,0,{
                    'product_id': self.lot_producing_id.product_id.id,
                    'lot_id': self.lot_producing_id.id,
                    'grade_id': self.lot_producing_id.grade_id.id,
                    'product_uom_id': self.lot_producing_id.product_id.uom_id.id,
                    'qty_done': sum([move.get('qty_done') for *x,move in move_in_line_ids]),
                    # 'product_uom_qty':sum([move.get('qty_done') for *x,move in move_in_line_ids]),
                    'company_id':self.env.company.id,
                    'location_id': self.location_id.id,
                    "location_dest_id":15,
                })],
        })
        
        
        if stock_picking_in and stock_picking_out:
                stock_picking_in.action_confirm()
                stock_picking_in.action_assign()
                stock_picking_in.button_validate()
                
                stock_picking_out.action_confirm()
                stock_picking_out.action_assign()
                stock_picking_out.button_validate()
        
        #     line.write({"state":"produced"})
        
        # stock_move_line = self.env['stock.move.line'].create(move_line)
        
        # for move in self.production_id.move_finished_ids:
        #     _logger.warning('='*40)
        #     _logger.warning('action_produce')
        #     _logger.warning(move.state)
        #     _logger.warning('='*40)
        #     move.sudo().write({"move_line_ids":stock_move_line})
            # self.production_id.sudo().write({"move_finished_ids":[(1,move.id,{
            #         "name":self.product_id.name,
            #         "product_id":self.product_id.id,
            #         "product_uom_qty":sum(stock_move_line.mapped('product_uom_qty')),
            #         "product_uom":self.product_id.uom_id.id,
            #         "location_id":15,
            #         "location_dest_id":self.location_id.id,
            #         "move_line_ids":stock_move_line
            #         })]})
            # move.sudo().write({"move_line_nosuggest_ids":stock_move_line}) 
        
        
        # _logger.warning([])
        # _logger.warning([move.sudo().write({"move_line_nosuggest_ids":stock_move_line}) for move in self.production_id.move_finished_ids])
        # _logger.warning([move.sudo().write({"move_line_nosuggest_ids":stock_move_line}) for move in self.production_id.move_finished_ids])
        
        # self.production_id.sudo().write({"move_finished_ids":[(0,0,{
        #                             "name":self.product_id.name,
        #                             "product_id":self.product_id.id,
        #                             "product_uom_qty":sum(stock_move_line.mapped('product_uom_qty')),
        #                             "product_uom":self.product_id.uom_id.id,
        #                             "location_id":15,
        #                             "location_dest_id":self.location_id.id,
        #                             "move_line_ids":stock_move_line
        #                             })]})
        # self.production_id.sudo()._post_inventory()
        # # productions_not_to_backorder._post_inventory(cancel_backorder=True)
        # # productions_to_backorder._post_inventory(cancel_backorder=False)
        # # backorders = productions_to_backorder._generate_backorder_productions()
        # _logger.warning('='*40)
        # _logger.warning('action_produce')
        # _logger.warning([moveline.lot_id for move in self.production_id.move_finished_ids for moveline in move.move_line_nosuggest_ids])
        # _logger.warning('='*40)
        
            
    
        
    def action_draft(self):
        # self.production_id.sudo().write({"move_finished_ids":False})
        for move in self.production_id.move_finished_ids:
            for moveline in move.move_line_ids.filtered(lambda x: x.lot_id.id in self.moveline_before_ids.filtered(lambda ml : ml.state == 'produced').mapped('lot_id').ids):
                moveline.write({"state":'cancel'})
                # moveline.unlink()
            
        for line in self.moveline_before_ids.filtered(lambda x : x.state != 'transfer'):
            self._cr.execute("DELETE FROM stock_quant WHERE location_id in (15,%s) AND product_id = %s AND lot_id = %s"%(self.location_id.id,self.product_id.id,line.lot_id.id))
            line.lot_id.unlink()
            line.write({"state":"inspecting"})
        self.state = 'draft'
    
    
    def generate_roll(self):
        move_line = []
        for line in range(self.amount_gen_roll):
            lot_name = self.env['ir.sequence'].next_by_code('stock.production.lot.gdj')
            move_line.append((0,0,{
                "lot_name": lot_name,
                "production_id":self.production_id.id,
                "product_id":self.production_id.product_id.id,
                "employee_id":self.employee_id.id,
                "quantity":self.quantity_gen,
                "state":'inspecting'
                
            }))
        self.moveline_before_ids = move_line
            
        

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('mrp.inspect')
        vals['name'] = seq
        result = super(ProduksiInspect, self).create(vals)
        return result

    @api.depends('moveline_before_ids.quantity')
    def _compute_quantity_all(self):
        for order in self:
            order.total_quantity = 0.0
            order.tot_roll = 0.0
            order.total_quantity = sum(line.quantity for line in order.moveline_before_ids)
            order.tot_roll = len(order.moveline_before_ids)

    def action_confirm(self):
        # _logger.warning('='*40)
        # _logger.warning('action_confirm')
        # _logger.warning([move.lot_id.id is False for move in self.moveline_before_ids.filtered(lambda x: x.state == 'inspecting' and not x.lot_id.id)])
        # _logger.warning('='*40)
        # for lot in self.moveline_before_ids.filtered(lambda x: x.state == 'inspecting' and not x.lot_id.id):
        #     new_lot = self.env['stock.production.lot'].sudo().create({
        #         "name":lot.lot_name,
        #         "location_id":self.location_id.id,
        #         "inspect_date":self.date,
        #         "tanggal_produksi":lot.production_id.date_planned_start.date(),
        #         "inspect_id":self.id,
        #         "production_id":lot.production_id.id,
        #         "product_id":lot.product_id.id,
        #         "grade_id":lot.grade_id.id,
        #         "company_id":self.env.user.company_id.id
        #     })
            
        #     lot.update({"lot_id":new_lot.id})
            
        self.state = 'confirm'
        self.action_produce()
    

class ProduksiInspectLine(models.Model):
    _name = 'produksi.inspect.line'

    name = fields.Char(string='Name')
    inspect_id = fields.Many2one('produksi.inspect', string='Inspect')
    greige_id = fields.Many2one('product.product', string='Greige')
    shift = fields.Selection([("pagi","Pagi"),("sore","Sore"),("malam","Malam")], string='Shift')
    operator_id = fields.Many2one('hr.employee', string='Operator MC')
    machine_id = fields.Many2one('mrp.machine', string='Machine')
    tanggal_potong = fields.Date(string='Tanggal Potong', related='inspect_id.date')
    no_potong = fields.Integer(string='No Potong')
    no_roll = fields.Integer(string='No Roll')
    lot_id = fields.Many2one('stock.production.lot', string='Barcode')
    qty = fields.Float(string='Quantity Potong KG')
    qty_inspect = fields.Float(string='Quantity Inspect KG')
    qty_bs = fields.Float(string='Quantity B/S KG', compute='get_qty_bs',)
    grade_id = fields.Many2one('makloon.grade', string='Grade')

    mrp_id = fields.Many2one('mrp.production', string='MRP')
    knitting_line_id = fields.Many2one('produksi.knitting.line', string='Knitting')
    barcode = fields.Char(string='Barcode')

    @api.onchange('barcode')
    @api.depends('inspect_id.scale')
    def get_onchange_barcode_mrp(self):
        barcode_lot = self.env['stock.production.lot']
        
        if self.barcode:
            lot                     = barcode_lot.search([('name', '=', self.barcode)])
            self.lot_id             = lot.id
            self.mrp_id             = lot.mrp_id.id
            self.greige_id          = lot.product_id.id
            self.qty                = lot.bruto
            self.knitting_line_id   = lot.knitting_line_id.id
            self.shift              = lot.knitting_line_id.shift
            self.machine_id         = lot.knitting_line_id.machine_id.id
            self.no_potong          = lot.knitting_line_id.no_potong
            self.no_roll            = lot.knitting_line_id.no_roll
            self.qty_inspect        = self.inspect_id.scale

    @api.depends('qty', 'qty_inspect')
    def get_qty_bs(self):
        self.qty_bs = self.qty - self.qty_inspect

class StockMoveLineBefore(models.Model):
    _inherit = 'stock.move.line.before'


    inspect_id = fields.Many2one('produksi.inspect', string='Inspect')
    
    @api.depends('inspect_id')
    @api.onchange('defect_ids')
    def set_grade(self):
        for move in self:
            if len(move.defect_ids) > 0:
                move.write({"grade_id":3})
    
    

class MrpProductionReturned(models.Model):
    _inherit = 'mrp.production.return'

    inspect_id = fields.Many2one('produksi.inspect', string='Inspect')
    
