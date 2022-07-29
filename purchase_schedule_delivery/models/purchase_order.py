# Copyright 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2015-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError 
    

class PurchaseOrderLineSchedule(models.Model):
    _name = "purchase.order.line.schedule"
    _description = "Purchase Line Schedule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    po_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="PO line",
        readonly=True,
    )
    quantity_schedule = fields.Float(string="Qty Schedule")
    date_schedule = fields.Date(
        string="Schedule date",
        help="Date when the user initiated the request.",
        default=fields.Date.context_today,
        tracking=True,
    )
    description = fields.Text(string="Description")
    quantity_allowance = fields.Float(string='Price Total', related='po_line_id.quantity_allowance')

    # @api.onchange('quantity_schedule')
    # def _onchange_quantity_schedule(self):
    #     self.ensure_one()
    #     for rec in self:
    #         if rec.quantity_schedule:
    #             if sum(rec.po_line_id.line_schedule_ids.mapped('quantity_schedule')) > rec.quantity_allowance:
    #                 raise UserError(_("Mohon maaf quantity schedule tidak boleh melebihi quantity allowance"))

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"


    line_schedule_ids = fields.One2many(
        comodel_name="purchase.order.line.schedule",
        inverse_name="po_line_id",
        string="Line Schedule",
        readonly=False,
        copy=True,
        tracking=True,
    )
    total_qty = fields.Float(string='Qty Schedule', compute='compute_total_qty')
    
    
    @api.constrains('line_schedule_ids')
    def check_qty_schedule(self):
        for record in self:
            # if record.allowance == 0:
            #     raise UserError(_("Mohon maaf quantity allowance belum disetting"))
            if record.total_qty > record.quantity_allowance:
                raise UserError(_("Mohon maaf quantity schedule tidak boleh melebihi quantity allowance"))

    def action_open_schedule(self):
        print('action_open_schedule')
        action = self.env.ref('purchase_schedule_delivery.purchas_order_line_schedule_action').read()[0]
        action['res_id'] = self.id
        print(action)
        return action

    # @api.depends('po_line_id', 'quantity_schedule')
    def compute_total_qty(self):
        for rec in self:
            rec.total_qty = sum(self.line_schedule_ids.mapped('quantity_schedule'))
            
            
    