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


class PurchaseRequest(models.Model):

    _name = "purchase.request"
    _description = "Purchase Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("purchase.request")
    
    
    @api.model
    def _filter_by_receipt(self):
        domain = []
        picking_type_id = self.env.user.default_picking_type_ids.filtered(lambda type:type.sequence_code == 'IN').mapped('id')
        if picking_type_id:
            domain = [('id','in',picking_type_id)]
        return domain

    @api.model
    def _default_picking_type(self):
        # picking_type_ids = self.env.user.default_picking_type_ids.filtered(lambda type:type.sequence_code == 'IN').mapped('id')
        # return picking_type_ids[0] if picking_type_ids and len(picking_type_ids) > 0 else False
        # return self.requested_by.property_warehouse_id
        picking_type_ids = self.env['stock.picking.type'].search([('warehouse_id','=', self.env.user.property_warehouse_id.id)]).filtered(lambda type:type.sequence_code == 'IN').mapped('id')
        # print(picking_type_ids)
        return picking_type_ids[0] if picking_type_ids else False
        

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("to_approve", "approved", "rejected", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True

    name = fields.Char(
        string="Request Reference",
        required=True,
        default=lambda self: _("New"),
        tracking=True,
    )
    is_name_editable = fields.Boolean(
        default=lambda self: self.env.user.has_group("base.group_no_one"),
    )
    origin = fields.Char(string="Source Document")
    date_start = fields.Date(
        string="Creation date",
        help="Date when the user initiated the request.",
        default=fields.Date.context_today,
        tracking=True,
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested by",
        required=True,
        copy=False,
        tracking=True,
        default=_get_default_requested_by,
        index=True,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Approver",
        tracking=True,
        domain=lambda self: [
            (
                "groups_id",
                "in",
                self.env.ref("purchase_request.group_purchase_request_manager").id,
            )
        ],
        index=True,
    )
    description = fields.Text(string="Note")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=_company_get,
        tracking=True,
    )
    line_ids = fields.One2many(
        comodel_name="purchase.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=False,
        copy=True,
        tracking=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="line_ids.product_id",
        string="Product",
        readonly=True,
    )
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
    )
    is_editable = fields.Boolean(
        string="Is editable", compute="_compute_is_editable", readonly=True
    )
    to_approve_allowed = fields.Boolean(compute="_compute_to_approve_allowed")
    picking_type_id = fields.Many2one(
        # comodel_name="stock.picking.type",
        related='po_categ_id.picking_type_id',
        string="Picking Type",
        required=True,
        default=_default_picking_type,
        domain = lambda self : self._filter_by_receipt(),
    )
    group_id = fields.Many2one(
        comodel_name="procurement.group",
        string="Procurement Group",
        copy=False,
        index=True,
    )
    line_count = fields.Integer(
        string="Purchase Request Line count",
        compute="_compute_line_count",
        readonly=True,
    )
    move_count = fields.Integer(
        string="Stock Move count", compute="_compute_move_count", readonly=True
    )
    purchase_count = fields.Integer(
        string="Purchases count", compute="_compute_purchase_count", readonly=True, store=True
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    
    
    estimated_cost = fields.Monetary(
        compute="_compute_estimated_cost",
        string="Total Estimated Cost",
        store=True,
    )
    
    no_komunikasi = fields.Char(string='No Komunikasi')
    
    # po_categ_id = fields.Many2one('purchase.order.category', string='PO Category',help="Tujuan Pembelian", default=lambda self:self.env.user.po_categ_id)
    po_categ_id = fields.Many2one('purchase.order.category', string='PO Category',help="Tujuan Pembelian")

    categ_id = fields.Many2one('product.category')
    # , related='order_id.categ_id'
    
    location_id  = fields.Many2one('stock.location', string='Location',
    related='picking_type_id.default_location_dest_id'
    )
    date_line = fields.Date(string='Date Request')
    # tipe_permintaan = fields.Selection([('produksi', 'Produksi'), ('non_produksi', 'Non Produksi')], string="Tipe Permintaan", default=lambda self:self.env.user.tipe_permintaan)
    tipe_permintaan = fields.Selection([('produksi', 'Produksi'), ('non_produksi', 'Non Produksi')], string="Tipe Permintaan")
    # product_categ_id = fields.Many2one('product.category', string='Product Category')
    product_category_ids = fields.Many2many(related='po_categ_id.product_category_ids', string='Product Category')

    @api.depends("line_ids", "line_ids.estimated_cost")
    def _compute_estimated_cost(self):
        for rec in self:
            rec.estimated_cost = sum(rec.line_ids.mapped("estimated_cost"))

    @api.depends("line_ids","tipe_permintaan")
    def _compute_purchase_count(self):
        for rec in self:
            # rec.purchase_count = len(rec.mapped("line_ids.purchase_lines.order_id"))
            po = self.env['purchase.order'].search([('purchase_request_id', '=', rec.id)])
            rec.purchase_count = len(po)

    def action_view_purchase_order(self):
        action = self.env.ref("purchase.purchase_rfq").sudo().read()[0]
        # lines = self.mapped("line_ids.purchase_lines.order_id")
        lines = self.env['purchase.order'].search([('purchase_request_id', '=', self.id)])

        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_move_count(self):
        for rec in self:
            rec.move_count = len(
                rec.mapped("line_ids.purchase_request_allocation_ids.stock_move_id")
            )

    def action_view_stock_move(self):
        action = self.env.ref("stock.stock_move_action").sudo().read()[0]
        # remove default filters
        action["context"] = {}
        lines = self.mapped("line_ids.purchase_request_allocation_ids.stock_move_id")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [(self.env.ref("stock.view_move_form").id, "form")]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.mapped("line_ids"))

    def action_view_purchase_request_line(self):
        action = (
            self.env.ref("purchase_request.purchase_request_line_form_action")
            .sudo()
            .read()[0]
        )
        lines = self.mapped("line_ids")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase_request.purchase_request_line_form").id, "form")
            ]
            action["res_id"] = lines.ids[0]
        return action

    @api.depends("state", "line_ids.product_qty", "line_ids.cancelled")
    def _compute_to_approve_allowed(self):
        for rec in self:
            rec.to_approve_allowed = rec.state == "draft" and any(
                not line.cancelled and line.product_qty for line in rec.line_ids
            )

    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({"state": "draft", "name": self._get_default_name()})
        return super(PurchaseRequest, self).copy(default)

    @api.model
    def _get_partner_id(self, request):
        user_id = request.assigned_to or self.env.user
        return user_id.partner_id.id

    @api.model
    def create(self, vals):
    
        # if vals.get("name", _("New")) == _("New"):
        query = "select max(id) from purchase_request;"
        self._cr.execute(query)
        result = self._cr.fetchone()
        next_id = 0
        if result[0]:
            next_id = result[0]
        vals["name"] = 'New - %s' % int(next_id + 1)

        # self.change_name()
        request = super(PurchaseRequest, self).create(vals)
        if vals.get("assigned_to"):
            partner_id = self._get_partner_id(request)
            request.message_subscribe(partner_ids=[partner_id])
        if self.env.user.property_warehouse_id.code == 'GDB':
            request.button_to_approve()
            request.button_approved()
        return request
    
    def change_name(self):
        self.name = 'New - %s ' % self._origin.id

    def write(self, vals):
        res = super(PurchaseRequest, self).write(vals)
        for request in self:
            if vals.get("assigned_to"):
                partner_id = self._get_partner_id(request)
                request.message_subscribe(partner_ids=[partner_id])
        return res

    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"

    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("You cannot delete a purchase request which is not draft.")
                )
        return super(PurchaseRequest, self).unlink()

    def button_draft(self):
        self.mapped("line_ids").do_uncancel()
        return self.write({"state": "draft"})

    def button_to_approve(self):
        self.to_approve_allowed_check()
        if self.name.split('-')[0] == 'New ':
            # name = self.env['ir.sequence'].warehuse_sequencing(self.picking_type_id.warehouse_id.code, self.picking_type_id.warehouse_id.name)
            seq = self.location_id.pr_sequence_id
            if not seq:
                raise UserError('Sequence Untuk Lokasi %s Belum Di Setting Mohon Hubungi Administrator'%(self.location_id.location_id.name))
            seq = self.location_id.pr_sequence_id.next_by_id()
            name = 'PR/%s' %(seq)
            return self.write({"name" : name, "state": "to_approve"})
        else:
            self.write({"state": "to_approve"})

    def button_approved(self):
        return self.write({"state": "approved", "assigned_to": self.env.user.id})

    def button_rejected(self):
        self.mapped("line_ids").do_cancel()
        return self.write({"state": "rejected"})

    def button_done(self):
        return self.write({"state": "done"})

    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({"state": "rejected"})

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
