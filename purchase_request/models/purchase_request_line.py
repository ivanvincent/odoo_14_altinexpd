# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_STATES = [
    ("draft", "Draft"),
    ("to_approve", "To be approved"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("done", "Done"),
]


class PurchaseRequestLine(models.Model):

    _name = "purchase.request.line"
    _description = "Purchase Request Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"



    @api.model
    def _filter_product(self):
        domain = []        
        domain += [('categ_id','in','categ_id')]
        return domain
    
    # @api.model
    # def _filter_product(self):
    #     domain = []
    #     if self.env.user.id != 2:
    #         domain += [('categ_id','in',[category.id for warehouse in self.env.user.default_warehouse_ids for category in warehouse.product_category_ids])]
    #     return domain

    @api.model
    def _filter_lot(self):
        domain = []
        product_category_ids = self.env.user.property_warehouse_id.product_category_ids.mapped('id')
        if product_category_ids:
            domain = [('product_id.categ_id','in',product_category_ids)]
        return domain
    



    name = fields.Char(string="Description", tracking=True)
    product_uom_id = fields.Many2one(
        related='product_id.uom_id',
        # comodel_name="uom.uom",
        string="UoM",
        tracking=True,
    )
    product_qty = fields.Float(
        string="Quantity PO", tracking=True, digits="Product Unit of Measure"
    )
    request_id = fields.Many2one(
        comodel_name="purchase.request",
        string="Purchase Request",
        ondelete="cascade",
        readonly=True,
        index=True,
        auto_join=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="request_id.company_id",
        string="Company",
        store=True,
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        tracking=True,
    )
    analytic_tag_ids = fields.Many2many(
        "account.analytic.tag", string="Analytic Tags", tracking=True
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        related="request_id.requested_by",
        string="Requested by",
        store=True,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        related="request_id.assigned_to",
        string="Assigned to",
        store=True,
    )
    date_start = fields.Date(related="request_id.date_start", store=True)
    description = fields.Text(
        related="request_id.description",
        string="PR Description",
        store=True,
        readonly=False,
    )
    origin = fields.Char(
        related="request_id.origin", string="Source Document", store=True
    )
    date_required = fields.Date(
        string="Request Date",
        required=True,
        tracking=True,
        default=fields.Date.context_today,
    )
    is_editable = fields.Boolean(
        string="Is editable", compute="_compute_is_editable", readonly=True
    )
    specifications = fields.Text(string="Specifications", )
    request_state = fields.Selection(
        string="Request state",
        related="request_id.state",
        store=True,
    )
    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Preferred supplier",
        compute="_compute_supplier_id",
        compute_sudo=True,
        store=True,
    )
    cancelled = fields.Boolean(
        string="Cancelled", readonly=True, default=False, copy=False
    )

    purchased_qty = fields.Float(
        string="RFQ/PO Qty",
        digits="Product Unit of Measure",
        compute="_compute_purchased_qty",
    )
    purchase_lines = fields.Many2many(
        comodel_name="purchase.order.line",
        relation="purchase_request_purchase_order_line_rel",
        column1="purchase_request_line_id",
        column2="purchase_order_line_id",
        string="Purchase Order Lines",
        readonly=True,
        copy=False,
    )
    purchase_state = fields.Selection(
        compute="_compute_purchase_state",
        string="Purchase Status",
        selection=lambda self: self.env["purchase.order"]._fields["state"].selection,
        store=True,
    )
    move_dest_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="created_purchase_request_line_id",
        string="Downstream Moves",
    )

    orderpoint_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint", string="Orderpoint"
    )
    purchase_request_allocation_ids = fields.One2many(
        comodel_name="purchase.request.allocation",
        inverse_name="purchase_request_line_id",
        string="Purchase Request Allocation",
    )

    qty_in_progress = fields.Float(
        string="Qty In Progress",
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity in progress.",
    )
    qty_done = fields.Float(
        string="Qty Done",
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity completed",
    )
    qty_cancelled = fields.Float(
        string="Qty Cancelled",
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty_cancelled",
        store=True,
        help="Quantity cancelled",
    )
    qty_to_buy = fields.Boolean(
        compute="_compute_qty_to_buy",
        string="There is some pending qty to buy",
        store=True,
    )
    pending_qty_to_receive = fields.Float(
        compute="_compute_qty_to_buy",
        digits="Product Unit of Measure",
        copy=False,
        string="Pending Qty to Receive",
        store=True,
    )
    estimated_cost = fields.Monetary(
        string="Estimated Cost",
        currency_field="currency_id",
        # default=0.0,
        compute='get_estimated_cost',
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        # domain = lambda self : self._filter_product(),
        # domain="[('categ_id', '=', product_categ_id)]",
        tracking=True,
        required=True,
    )
    
    qty_on_hand   = fields.Float(string="Current Stock", compute="_get_onhand")
    
    
    no_komunikasi   = fields.Char(string='No Komunikasi')
    note            = fields.Char(string='Ket')
    last_price      = fields.Float(string='Last Price')
    price           = fields.Float(string='Price')
    grade_id        = fields.Many2one('makloon.grade', string='Grade')
    lot_id          = fields.Many2one('stock.production.lot', string='Lot',
                                    #   domain = lambda self : self._filter_lot(),
                                      )
    picking_type_id = fields.Many2one(related='request_id.picking_type_id', string='Picking Type')
    image_ids       = fields.One2many('insert.image', 'purchase_line_id', string='Image')
    date_dtg_brg = fields.Date(string='Date Dtg Barang')
    outstanding_po = fields.Float(string='Outstanding Po', compute='_compute_outstanding_po')
    po_categ_id = fields.Many2one('purchase.order.category', string='PO Category',help="Tujuan Pembelian")
    product_category_ids = fields.Many2many(related='po_categ_id.product_category_ids', string='Product Category')

    categ_id = fields.Many2one('product.category' , related='request_id.categ_id')
    estimated_price = fields.Float(string="Estimated Price", required=True)
    image_product = fields.Binary(related="product_id.image_1920", string="Image")
    subtotal_estimate = fields.Monetary(string='Subtotal Estimate Price', compute='get_subtotal_estimate')
    conversion = fields.Float(string='Konversi')
    qty_pr = fields.Float(string='Quantity PR')
    status_po = fields.Many2one('uom.uom', string='Satuan PO')

    @api.onchange('product_id')
    def onchange_product(self):
        self.conversion = self.product_id.drum_liter
        self.status_po = self.product_id.uom_po_id

    @api.onchange('qty_pr')
    def onchange_qty_pr(self):
        # for line in self :
        self.product_qty = self.handle_division_zero(self.qty_pr , self.conversion)

    # def _get_hasil_konversi(self):
    #     for line in self :
    #         line.hasil_konversi = self.handle_division_zero(line.product_qty , line.conversion)

    def handle_division_zero(self,x,y):
        try:
            return x/y
        except ZeroDivisionError:
            return 0

    @api.depends('product_id')
    def _get_onhand(self):
        for line in  self:
            # domain = [('product_id', '=', line.product_id.id)]
            # quant = self.env['stock.quant'].search(domain).mapped('quantity')
            line.qty_on_hand = line.product_id.qty_available
            # ('location_id', '=', line.request_id.picking_type_id.default_location_dest_id.id)
 
    
    @api.onchange('lot_id')
    def onchange_lot(self):
        for rec in self:
            rec.product_id = rec.lot_id.product_id.id
   
    @api.depends('product_qty', 'estimated_price')
    def get_subtotal_estimate(self):
        for rec in self:
            rec.subtotal_estimate = rec.product_qty * rec.estimated_price
    
    @api.depends('product_qty', 'estimated_price')
    def get_estimated_cost(self):
        for rec in self:
            rec.estimated_cost = rec.product_qty * rec.estimated_price
    
    

    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id",
        "purchase_request_allocation_ids.purchase_line_id.state",
        "request_id.state",
    )
    def _compute_qty_to_buy(self):
        for pr in self:
            qty_to_buy = sum(pr.mapped("product_qty")) - sum(pr.mapped("qty_done"))
            pr.qty_to_buy = qty_to_buy > 0.0
            pr.pending_qty_to_receive = qty_to_buy

    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id.state",
        "purchase_request_allocation_ids.purchase_line_id",
    )
    def _compute_qty(self):
        for request in self:
            done_qty = sum(
                request.purchase_request_allocation_ids.mapped("allocated_product_qty")
            )
            open_qty = sum(
                request.purchase_request_allocation_ids.mapped("open_product_qty")
            )
            request.qty_done = done_qty
            request.qty_in_progress = open_qty

    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id.order_id.state",
        "purchase_request_allocation_ids.purchase_line_id",
    )
    def _compute_qty_cancelled(self):
        for request in self:
            if request.product_id.type != "service":
                qty_cancelled = sum(
                    request.mapped("purchase_request_allocation_ids.stock_move_id")
                    .filtered(lambda sm: sm.state == "cancel")
                    .mapped("product_qty")
                )
            else:
                qty_cancelled = sum(
                    request.mapped("purchase_request_allocation_ids.purchase_line_id")
                    .filtered(lambda sm: sm.state == "cancel")
                    .mapped("product_qty")
                )
                # done this way as i cannot track what was received before
                # cancelled the purchase order
                qty_cancelled -= request.qty_done
            if request.product_uom_id:
                request.qty_cancelled = (
                    max(
                        0,
                        request.product_id.uom_id._compute_quantity(
                            qty_cancelled, request.product_uom_id
                        ),
                    )
                    if request.purchase_request_allocation_ids
                    else 0
                )
            else:
                request.qty_cancelled = qty_cancelled

    @api.depends(
        "product_id",
        "name",
        "product_uom_id",
        "product_qty",
        "analytic_account_id",
        "date_required",
        "specifications",
        "purchase_lines",
    )
    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ("to_approve", "approved", "rejected", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True
        for rec in self.filtered(lambda p: p.purchase_lines):
            rec.is_editable = False

    @api.depends("product_id", "product_id.seller_ids")
    def _compute_supplier_id(self):
        for rec in self:
            sellers = rec.product_id.seller_ids.filtered(
                lambda si: not si.company_id or si.company_id == rec.company_id
            )
            rec.supplier_id = sellers[0].name if sellers else False

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = "[{}] {}".format(name, self.product_id.code)
            if self.product_id.description_purchase:
                name += "\n" + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name
            #self.last_price = self.product_id.last_purchase_price

    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({"cancelled": True})

    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({"cancelled": False})

    def write(self, vals):

        # for record in self:
        #     if record._context.get('old_values'):
        #         old_vals = record._context['product_qty'].get(record.id, {})
        #         if 'product_qty' in old_vals:
        #             record.message_post(body="Cost changed from %s.2f to %s.2f." 
        #                   % (old_vals['product_qty'],
        #                      record.product_qty))

        # request_obj = self.env["purchase.request"]
        # for po in self:
        #     requests_dict = {}
        #     for line in po:
        #         for request_line in line:
        #             request_id = request_line.request_id.id
        #             if request_id not in requests_dict:
        #                 requests_dict[request_id] = {}
        #             # date_planned = "%s" % line.date_planned
        #             data = {
        #                 "name": request_line.name,
        #                 "product_qty": line.product_qty,
        #                 # "product_uom": line.product_uom.name,
        #                 # "date_planned": date_planned,
        #             }
        #             requests_dict[request_id][request_line.id] = data
        #     for request_id in requests_dict:
        #         request = request_obj.browse(request_id)
        #         message = ('update')
        #         request.message_post(
        #             body=message, subtype_id=self.env.ref("mail.mt_comment").id
        #         )
        res = super(PurchaseRequestLine, self).write(vals)

        if vals.get("cancelled"):
            requests = self.mapped("request_id")
            requests.check_auto_reject()
        return res

    def _compute_purchased_qty(self):
        for rec in self:
            rec.purchased_qty = 0.0
            for line in rec.purchase_lines.filtered(lambda x: x.state != "cancel"):
                if rec.product_uom_id and line.product_uom != rec.product_uom_id:
                    rec.purchased_qty += line.product_uom._compute_quantity(
                        line.product_qty, rec.product_uom_id
                    )
                else:
                    rec.purchased_qty += line.product_qty

    @api.depends("purchase_lines.state", "purchase_lines.order_id.state")
    def _compute_purchase_state(self):
        for rec in self:
            temp_purchase_state = False
            if rec.purchase_lines:
                if any(po_line.state == "done" for po_line in rec.purchase_lines):
                    temp_purchase_state = "done"
                elif all(po_line.state == "cancel" for po_line in rec.purchase_lines):
                    temp_purchase_state = "cancel"
                elif any(po_line.state == "purchase" for po_line in rec.purchase_lines):
                    temp_purchase_state = "purchase"
                elif any(
                    po_line.state == "to approve" for po_line in rec.purchase_lines
                ):
                    temp_purchase_state = "to approve"
                elif any(po_line.state == "sent" for po_line in rec.purchase_lines):
                    temp_purchase_state = "sent"
                elif all(
                    po_line.state in ("draft", "cancel")
                    for po_line in rec.purchase_lines
                ):
                    temp_purchase_state = "draft"
            rec.purchase_state = temp_purchase_state

    @api.model
    def _get_supplier_min_qty(self, product, partner_id=False):
        seller_min_qty = 0.0
        if partner_id:
            seller = product.seller_ids.filtered(lambda r: r.name == partner_id).sorted(
                key=lambda r: r.min_qty
            )
        else:
            seller = product.seller_ids.sorted(key=lambda r: r.min_qty)
        if seller:
            seller_min_qty = seller[0].min_qty
        return seller_min_qty

    @api.model
    def _calc_new_qty(self, request_line, po_line=None, new_pr_line=False):
        purchase_uom = po_line.product_uom or request_line.product_id.uom_po_id
        # TODO: Not implemented yet.
        #  Make sure we use the minimum quantity of the partner corresponding
        #  to the PO. This does not apply in case of dropshipping
        supplierinfo_min_qty = 0.0
        if not po_line.order_id.dest_address_id:
            supplierinfo_min_qty = self._get_supplier_min_qty(
                po_line.product_id, po_line.order_id.partner_id
            )

        rl_qty = 0.0
        # Recompute quantity by adding existing running procurements.
        if new_pr_line:
            rl_qty = po_line.product_uom_qty
        else:
            for prl in po_line.purchase_request_lines:
                for alloc in prl.purchase_request_allocation_ids:
                    rl_qty += alloc.product_uom_id._compute_quantity(
                        alloc.requested_product_uom_qty, purchase_uom
                    )
        qty = max(rl_qty, supplierinfo_min_qty)
        return qty

    def _can_be_deleted(self):
        self.ensure_one()
        return self.request_state == "draft"

    def unlink(self):
        if self.mapped("purchase_lines"):
            raise UserError(
                _("You cannot delete a record that refers to purchase lines!")
            )
        for line in self:
            if not line._can_be_deleted():
                raise UserError(
                    _(
                        "You can only delete a purchase request line "
                        "if the purchase request is in draft state."
                    )
                )
        return super(PurchaseRequestLine, self).unlink()

    def action_show_image(self):
        action = self.env.ref('purchase_request.purchase_request_line_action').read()[0]
        action['res_id'] = self.id
        action['name'] = "Images of %s" % (self.product_id.name)
        return action

    def action_show_image_product(self):
        action = self.env.ref('purchase_request.purchase_request_line_image_action').read()[0]
        action['res_id'] = self.id
        action['name'] = "Images of %s" % (self.product_id.name)
        return action

    @api.depends('purchase_lines', 'product_qty')
    def _compute_outstanding_po(self):
        for rec in self:
            rec.outstanding_po = rec.product_qty - sum(rec.purchase_lines.mapped('product_qty'))