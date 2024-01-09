from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

_STATES = [
    ("draft", "Draft"),
    ("waiting", "Waiting"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("done", "Done"),
]

class InheritStockWarehouseIssue(models.Model):
    _inherit = 'stock.warehouse'

    user_id = fields.Many2one(
        comodel_name="res.users", 
        string="Responsible by",
        copy=False,
        track_visibility="onchange",)

class InheritStockLocationIssue(models.Model):
    _inherit = 'stock.location'

    set_location_src_issue = fields.Boolean("Set Source Issue Location", default=False)
    set_location_dest_issue = fields.Boolean("Set Dest Issue Location", default=False)


class RequestRequisition(models.Model):
    _name = 'request.requisition'
    _description = "Request Requisition"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    # @api.model
    # def _get_default_assigned_to(self):
    #     return self.warehouse_id.user_id.id

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("request.requisition")

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state == "draft":
                rec.is_editable = True
            else:
                rec.is_editable = False

    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"
    

    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("You cannot delete a request requisition which is not draft.")
                )
        return super(RequestRequisition, self).unlink()

    def button_draft(self):
        self.mapped("order_ids").do_uncancel()
        return self.write({"state": "draft"})

    def button_request(self):
        self.to_approve_allowed_check()
        return self.write({"state": "waiting"})

    def button_approved(self):
        return self.write({"state": "approved","approved_by" : self.env.user.id})
       
            
            

    def button_done(self):
        return self.write({"state": "done"})

    def _default_warehouse(self):
        for request in self:
            warehouse = request.requested_by.default_warehouse_ids.mapped('name')
            if len(warehouse) == 0:
                request.request_by_warehouse = False
            else:
                request.request_by_warehouse = warehouse[0]
            if self.env.user.id == 214:
                request.request_by_warehouse = request.location_id.location_id.name
            
        

    name          = fields.Char(string="Request Number", track_visibility="onchange", readonly=True)
    origin        = fields.Char(string="Source Document")
    employee_id   = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string='Department')
    request_by_warehouse = fields.Char(string='Request By Warehouse', compute='_default_warehouse',)
    product_id    = fields.Many2one('product.product', related='order_ids.product_id', string='Product', readonly=False)
    lot_id        = fields.Many2one('stock.production.lot', related='order_ids.lot_id', string='Lot', readonly=False,)
    spesification = fields.Char(related='order_ids.spesification', string='Spesification',)
    request_date  = fields.Date(string='Request Date',default=fields.Date.today())
    vehicle_id     = fields.Many2one('fleet.vehicle', string='Vehicle')
    transfer_date = fields.Date(string='Transfer Date')
    note = fields.Text()
    order_ids = fields.One2many(
        comodel_name="request.requisition.line",
        inverse_name="order_id",
        string="Products to Requisition",
        readonly=False,
        copy=True,
        track_visibility="onchange",
    )
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        track_visibility="onchange",
        required=True,
        copy=False,
        default="draft",
    )
    is_editable = fields.Boolean(
        string="Is editable", compute="_compute_is_editable", readonly=True
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested by",
        required=True,
        copy=False,
        track_visibility="onchange",
        default=_get_default_requested_by,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Issued by",
        required=False,
        copy=False,
        readonly=True,
        related="warehouse_id.user_id"
        # track_visibility="onchange",
        # default=_get_default_assigned_to,
    )
    approve_by = fields.Many2one(
        comodel_name="res.users",
        string="Approver",
        # track_visibility="onchange",
        related="requested_by.approver_rr_id",
        readonly=True,
        # domain=lambda self: [
        #     (
        #         "groups_id",
        #         "in",
        #         self.env.ref("request_requisition.group_request_requisition_manager").id,
        #     )onchange_
    )
    # to_approve_allowed = fields.Boolean(compute="_compute_to_approve_allowed")
    group_id = fields.Many2one(
        comodel_name="procurement.group", string="Procurement Group", copy=False
    )
    approved_by = fields.Many2one(comodel_name="res.users", string='Approved by')
    # picking_ids = fields.Many2many(comodel_name='stock.picking', string='Stock Picking')
    move_count = fields.Integer(string="Stock Move count",  readonly=True )
    # compute="_compute_move_count",
    line_count = fields.Integer(string="Purchase Request Line count", compute="_compute_line_count", readonly=True, )
    print_count = fields.Integer(string='Print Counted')
    to_approve_allowed = fields.Boolean(compute="_compute_to_approve_allowed")
    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", string="Warehouse",
    domain = lambda self : [('id','in',self.env.user.default_dest_warehouse_ids.ids)],
    required=True)
    internal_transfer_count = fields.Integer(string='Transfer', compute='_compute_internal_transfer_count')
    internal_transfer_picking = fields.Many2one("stock.picking.type", "Picking Type",required=True, )
    location_id = fields.Many2one("stock.location", 
        "Location", required=True, 
        default=lambda self: self._default_location(),                                   
        domain=lambda self: self._default_internal_to(),
        help="This is the location where the user currently receives the product",
    )
    request_id = fields.Many2one(comodel_name="purchase.request", string="Purchase Request", copy=False)
    no_komunikasi = fields.Char(string='No Komunikasi')
    pegawai_id = fields.Many2one('hr.employee', string='Admin Yang Memerlukan')
    dqups_id = fields.Many2one('quotation.request.form', string='D-QUPS')
    product_id       = fields.Many2one('product.product', 'Product Finish',
        domain="""[
            ('type', 'in', ['product', 'consu']),
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id)
        ]
        """,
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)]})
    mrp_id = fields.Many2one('mrp.production', string='MO')


    @api.model
    def create(self, vals):
        location_id = self.env['stock.location'].browse(vals.get('location_id'))
        seq = location_id.rr_sequence_id
        if not seq:
            raise UserError('Sequence Untuk Lokasi %s Belum Di Setting Mohon Hubungi Administrator'%(location_id.location_id.name))
        seq = location_id.rr_sequence_id.next_by_id()
        name = 'RR/%s' %(seq)
        vals['name'] = name
        res = super(RequestRequisition, self).create(vals)
        return res

    def _default_internal_to(self):
        domain = [('id','in', self.env.user.stock_location_dest_ids.ids)]
        return domain
    
    @api.model
    def _default_location(self):
        location_id = self.env.user.default_warehouse_ids.lot_stock_id.mapped('id')
        if len(location_id) != 1:
            return False
        return location_id[0]
    
    @api.onchange('warehouse_id')
    def delete_record_order_ids(self):
        self.order_ids = [(5,0,0)]

    @api.onchange("warehouse_id")
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            self.internal_transfer_picking = self.warehouse_id.int_type_id.id
            res = {}
            res['domain'] = {'internal_transfer_picking' : [('id','=',self.warehouse_id.lot_stock_id.id)]}
            return res


    @api.onchange("employee_id")
    def onchange_employee_id(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id.id

    @api.depends("state", "order_ids.quantity", "order_ids.cancelled")
    def _compute_to_approve_allowed(self):
        for rec in self:
            rec.to_approve_allowed = rec.state == "draft" and any(
                [not line.cancelled and line.quantity for line in rec.order_ids]
            )

    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update(
            {
                "state": "draft",
                "name": self.env["ir.sequence"].next_by_code("request.requisition"),
            }
        )
        return super(RequestRequisition, self).copy(default)

    def action_cancel_request(self):
        self.state = 'draft'

    def _check_valid_quantity(self):
        return self.order_ids.filtered(lambda x: x.qty_onhand < 1)
        
        
            

    @api.depends("order_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.mapped("order_ids"))

    def _compute_internal_transfer_count(self):
        for order in self:
            int_ids = self.env['stock.picking'].search([('request_requisition_id', '=', order.id)])
            if int_ids:
                order.internal_transfer_count = len(int_ids)
            else:
                order.internal_transfer_count = 0

    def action_open_picking_transfer(self):
        return {
            'name': 'Transfers Issued',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('request_requisition_id', '=', self.id)],
            'context': {'create': False},
            'target': 'current'
        }

    def to_approve_allowed_check(self):
        for rec in self:
            if not rec.to_approve_allowed:
                raise UserError(
                    _(
                        "You can't request an approval for a purchase request "
                        "which is empty. (%s)"
                    )
                    % rec.name
                )

    def create_purchase_request(self):
        vals =  {
                'origin'                : self.name,
                'date_start'            : self.request_date,
                'requested_by'          : self.assigned_to.id,
                'assigned_to'           : self.approve_by.id,
                'description'           : self.note,
                'picking_type_id'       : self.warehouse_id.in_type_id.id,
                'requested_by'          : self.env.user.id,
                'rr_id'                 : self.id,
                'rr_ids'                : [(4,self.id)],
                'line_ids'              : [(0,0,{'request_id': self.id,'name': line.product_id.name,'product_id': line.product_id.id, 'specifications':line.spesification,
                                                 'product_qty': line.quantity,'product_uom_id': line.uom_id.id, 'lot_id': line.lot_id.id}) for line in self.order_ids]
            }
        
        request = self.env['purchase.request'].sudo().create(vals)
        
        self.sudo().write({'request_id': request.id})
        
        # request.button_to_approve()
        
        return
    
    def create_multi_purchase_request(self):
        line_vals = []
        rr_ids = []
        picking_type_ids = self.mapped('warehouse_id').in_type_id
        picking_type_ids = [internal_tf.id for internal_tf in picking_type_ids]
        if picking_type_ids:
            result = all(internal_tf == picking_type_ids[0] for internal_tf in picking_type_ids)
            if not result:
                raise UserError('Lokasi penerima tidak sama')
        for request in self:
            if request.state == 'approve' and request.internal_transfer_count == 0:
                continue
            rr_ids += [(4,request.id)]
                
            for line in request.order_ids:
                line_vals.append((0, 0, {'name': line.product_id.name,'no_komunikasi':request.no_komunikasi,'specifications':line.spesification,'product_id': line.product_id.id,'product_qty': line.quantity,'product_uom_id': line.uom_id.id}))
            
        vals = {
            # 'origin'                : request.name,
            'date_start'            : fields.Date.today(),
            # 'requested_by'          : request.assigned_to.id,
            # 'assigned_to'           : request.approve_by.id,
            # 'description'           : request.note,
            
            'picking_type_id'       : self.warehouse_id.in_type_id[0].id,
            # 'requested_by'          : request.env.user.id,
            'line_ids'               : line_vals,
            'rr_ids'                 : rr_ids
            # 'rr_id'                 : request.id,
            } 
            
        pr = self.env['purchase.request'].sudo().create(vals)
            
            
        pr.button_to_approve()
        
        for request in self:
            request.sudo().write({'request_id': pr.id})
            
        return {
            'name': 'Purchase Request',
            'view_mode': "form",
            'res_model': 'purchase.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': pr.id,
            }
            
        

    def create_picking_issue(self):
        data = []
        for order in self:
            
            for rec in order.order_ids:
                data.append((0, 0, {
                    'name': rec.product_id.name,
                    'product_id': rec.product_id.id,
                    'product_uom': rec.product_id.uom_id.id,
                    "location_id": order.mrp_id.location_src_id.id,
                    "location_dest_id":15,
                }))
            order.mrp_id.write({
                'move_raw_ids' : data
            })

            pick = {
                'picking_type_id': order.internal_transfer_picking.id,
                'date': order.request_date,
                'scheduled_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'origin': order.name,   
                'location_id': order.internal_transfer_picking.default_location_src_id.id,
                'vehicle_id':order.vehicle_id.id,
                'location_dest_id': order.location_id.id,
                'immediate_transfer': False,
                'requested_by' : order.requested_by.id,
                'request_requisition_id': order.id
                }
    
            picking = self.env['stock.picking'].create(pick)
            moves = order.order_ids.filtered(lambda r: r.product_id.type in ['product', 'consu'])._create_stock_moves(picking)
            picking.message_post_with_view('mail.message_origin_link', values={'self': picking, 'origin': order}, subtype_id=self.env.ref('mail.mt_note').id)
            
            if picking:
                picking.action_confirm()
                picking.action_assign()
                return {
                    'name': 'Transfer',
                    'view_mode': "form",
                    'res_model': 'stock.picking',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': picking.id,
                }
        return True

class RequestRequisitionLine(models.Model):
    _name = 'request.requisition.line'
    _description = "Request Requisition Line"
    
    def get_product_category(self):
        return [category.id for warehouse in self.env.user.default_warehouse_ids for category in warehouse.product_category_ids]


    name = fields.Char(string="Description", track_visibility="onchange")
    order_id = fields.Many2one(
        comodel_name="request.requisition",
        inverse_name="order_ids",
        string="Request to Requisition",
        readonly=False,
        copy=True,
        track_visibility="onchange",
    )
    partner_id = fields.Many2one('res.partner', string='Partner')
    requested_by = fields.Many2one(related='order_id.requested_by', string='Reqeuest By' ,store=True,)
    no_komunikasi = fields.Char(related='order_id.no_komunikasi', string='No Komunikasi')
    warehouse_id = fields.Many2one(related="order_id.warehouse_id", string="Warehouse", store=True,)
    product_category_ids = fields.Many2many(
        string='Product Category',related="warehouse_id.product_category_ids"
        )
    
    product_id = fields.Many2one('product.product', string='Product',
    domain=lambda self: [('categ_id','in',self.get_product_category())],
    required=True, )
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one('uom.uom', string='Uom', related="product_id.uom_id")
    remark = fields.Float(string='Remark')
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        track_visibility="onchange",
        required=True,
        copy=False,
        default="draft",
    )
    request_date = fields.Date(string='Request Date', related='order_id.request_date')
    cancelled = fields.Boolean(string="Cancelled", readonly=True, default=False, copy=False)
    qty_on_hand   = fields.Float(string="Qty On Hand", related="product_id.qty_available")
    qty_available = fields.Float(string="Qty Available", store=True, compute="_compute_qty_available")
    spesification = fields.Char(string='Specification',required=True, )
    chart_of_account_id = fields.Many2one('account.account', string="Coa")
    location_account_id = fields.Many2one('stock.location', string="Dest Loc",)
    qty_received = fields.Float(string='Received', compute="_compute_qty_received")
    qty_onhand = fields.Float(string='On Hand', compute="_compute_qty_onhand")
    is_request_pr = fields.Boolean(string='Request PR',default=False)
    lot_id          = fields.Many2one('stock.production.lot', string='Lot')
    variasi = fields.Char(string='Variasi', compute='_compute_variasi')
    code_product = fields.Char(string='Code')
    request_date = fields.Date(string='Request Date', related='order_id.request_date', store=True,)

    @api.onchange('lot_id')
    def onchange_lot(self):
        for rec in self:
            rec.product_id = rec.lot_id.product_id.id

    def _compute_variasi(self):
        for rec in self:
            rec.variasi = rec.product_id.product_template_attribute_value_ids.filtered(lambda x: x.attribute_id.name == 'Variasi').name
   
   
    def create_purchase_request(self):
        line_vals = []
        picking_type_ids = self.mapped('order_id').warehouse_id.in_type_id
        picking_type_ids = [internal_tf.id for internal_tf in picking_type_ids]
        if picking_type_ids:
            result = all(internal_tf == picking_type_ids[0] for internal_tf in picking_type_ids)
            if not result:
                raise UserError('Lokasi penerima tidak sama')

        for line in self:
            if line.order_id.state == 'approve' and line.order_id.internal_transfer_count == 0:
                continue
            
            if line.is_request_pr:
                raise UserError("PR sudah di buat di %s"%(line.order_id.request_id.name))
            
            line_vals.append((0, 0, {'name': line.product_id.name,'specifications':line.spesification,'product_id': line.product_id.id,'product_qty': line.quantity,'product_uom_id': line.uom_id.id}))
            
            
        vals = {
            # 'origin'                : request.name,
            'date_start'            : fields.Date.today(),
            # 'requested_by'          : request.assigned_to.id,
            # 'assigned_to'           : request.approve_by.id,
            # 'description'           : request.note,
            'picking_type_id'       : picking_type_ids[0],
            # 'requested_by'          : request.env.user.id,
            'line_ids'              : line_vals
            # 'rr_id'                 : request.id,
            } 
            
        pr = self.env['purchase.request'].sudo().create(vals)
        pr.button_to_approve()
        
        for line in self:
            line.sudo().write({'is_request_pr': True})
            
        return {
            'name': 'Purchase Request',
            'view_mode': "form",
            'res_model': 'purchase.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': pr.id,
            }
    
    @api.onchange('chart_of_account_id')
    def onchange_location_dest_id(self):
        for rec in self:
            if rec.chart_of_account_id:
                rec.location_dest_id = rec.location_account_id.search([('valuation_in_account_id','=',rec.chart_of_account_id.id)]).id

    @api.depends('qty_on_hand')
    def _compute_qty_available(self):
        # warehouse_user_ids = self.env.user.default_warehouse_ids.ids
        # ('warehouse_id','in',warehouse_user_ids)
        for rec in self:
            product = rec.product_id.id
            model = self.env['stock.quant'].search([('product_id','=',product)])
            available = rec.qty_on_hand - sum(model.mapped('reserved_quantity'))
            rec.qty_available = available



    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.uom_id = self.product_id.uom_id.id
        res = {}
        product = self.product_id.id
        if product:
            res['domain'] = {'lot_id': [('product_id', '=', product)]}
        return res

    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({"cancelled": True})

    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({"cancelled": False})

    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            if line.product_id.type not in ['product', 'consu']:
                continue
            template = {
                'name'              : line.product_id.name,
                'description_picking': line.name,
                'product_id'        : line.product_id.id,
                'product_uom'       : line.uom_id.id,
                'x_ket'             : line.name,
                'date'              : picking.date,
                'location_id'       : picking.location_id.id, 
                'location_dest_id'  : picking.location_dest_id.id, 
                'picking_id'        : picking.id,
                'state'             : 'draft',
                'company_id'        : picking.company_id.id,
                'price_unit'        : line.product_id.standard_price,
                'picking_type_id'   : picking.picking_type_id.id,
                'origin'            : picking.name,
                'warehouse_id'      : picking.picking_type_id.warehouse_id.id,
                'variasi'           : line.variasi,
                
            }
            diff_quantity = line.quantity
            move_id = moves.create(template)
            print(move_id.id)
            if float_compare(diff_quantity, 0.0, precision_rounding=line.uom_id.rounding) > 0:
                template['product_uom_qty'] = diff_quantity

                done += moves.create(template)
        return done

    def _compute_qty_received(self):
        for rec in self:
            picking_obj = self.env['stock.picking'].search([('origin', '=', rec.order_id.name), ('state', '=', 'done')])
            rec.qty_received = sum(picking_obj.move_ids_without_package.filtered(lambda a: a.product_id.id == rec.product_id.id).mapped('quantity_done')) or 0

    @api.depends('product_id')
    def _compute_qty_onhand(self):
        for rec in self:
            domain = [('product_id', '=', rec.product_id.id), ('location_id', '=', rec.order_id.internal_transfer_picking.default_location_src_id.id)]
            if rec.lot_id.id:
                domain.append(('lot_id', '=', rec.lot_id.id))
            quant = self.env['stock.quant'].search(domain).mapped('quantity')
            rec.qty_onhand = sum(quant)

    @api.onchange('code_product')
    def _onchange_code_product(self):
        for rec in self:
            if rec.code_product:
                lob_obj = self.env['stock.production.lot'].search([('ref', '=', rec.code_product)])
                rec.lot_id = lob_obj.id


class P(models.Model):
    _inherit = 'purchase.request'

    rr_id = fields.Many2one('request.requisition', string='RR Id')
    rr_ids = fields.Many2many(
        comodel_name='request.requisition', 
        relation='rr_purhchase_request_rel',
        column1='rr_id',
        column2='request_id',
        string='Request requistion'
        )