# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Fields
    use_sale_contract = fields.Selection(
        string='Use Contract',
        related='company_id.use_sale_contract',
        readonly=True,
    )
    contract_id = fields.Many2one(
        string='Contract',
        comodel_name='xf.partner.contract',
        ondelete='restrict',
        domain=[('state', '=', 'running'), ('type', '=', 'sale')],
    )

    # Compute and search fields, in the same order of fields declaration
    # Constraints and onchanges

    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        if self.contract_id:
            self.partner_id = self.contract_id.partner_id

    # Built-in methods overrides
    # Action methods

    def action_apply_contract(self):
        self.apply_contract()

    # Business methods

    def apply_contract(self):
        for order in self:
            if not order.contract_id:
                continue
            so_vals = order.contract_id._prepare_sale_order()
            order.write(so_vals)
            order.apply_contract_lines()

    def apply_contract_lines(self):
        for order in self:
            if not order.contract_id:
                continue
            lines = self.env['sale.order.line']
            for line in order.contract_id.line_ids:
                so_line_vals = line._prepare_sale_order_line(order)
                so_line = lines.new(so_line_vals)
                lines |= so_line
            order.order_line = lines

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.contract_id:
            invoice_vals['contract_id'] = self.contract_id.id
        return invoice_vals
