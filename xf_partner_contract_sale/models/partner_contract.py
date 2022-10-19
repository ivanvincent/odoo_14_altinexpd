# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import MissingError


class PartnerContract(models.Model):
    _inherit = 'xf.partner.contract'

    # Fields
    sale_order_ids = fields.One2many(
        string='Sale Orders',
        comodel_name='sale.order',
        inverse_name='contract_id',
        readonly=True,
    )
    sale_order_ids_count = fields.Integer(
        compute='_compute_sale_order_ids_count',
        compute_sudo=True,
    )

    # Compute and search fields, in the same order of fields declaration
    @api.depends('sale_order_ids')
    def _compute_sale_order_ids_count(self):
        for record in self:
            record.sale_order_ids_count = len(record.sale_order_ids)

    # Constraints and onchanges
    # Built-in methods overrides
    # Action methods

    def action_create_sale_order(self):
        self.ensure_one()
        sale_order_vals = self._prepare_sale_order()
        sale_order = self.env['sale.order'].create(sale_order_vals)
        sale_order.apply_contract_lines()
        return self.action_view_sale_orders()

    def action_view_sale_orders(self):
        self.ensure_one()
        action = {
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
        }
        if self.sale_order_ids_count == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.sale_order_ids.id,
            })
        else:
            action.update({
                'name': _("Sale Order generated from the contract %s", self.name),
                'domain': [('id', 'in', self.sale_order_ids.ids)],
                'view_mode': 'tree,form',
            })
        return action

    # Business methods

    def _prepare_sale_order(self):
        self.ensure_one()
        return {
            'contract_id': self.id,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'origin': self.ref,
            'note': self.notes,
            'payment_term_id': self.payment_term_id.id,
        }


class PartnerContractLine(models.Model):
    _inherit = 'xf.partner.contract.line'

    def _prepare_sale_order_line(self, order):
        self.ensure_one()
        if not self.product_id:
            raise MissingError('Please set product for each contract line as is required to generate sale orders')
        vals = {
            'name': self.name,
            'sequence': self.sequence,
            'product_uom_qty': self.quantity,
            'product_uom': self.product_uom_id.id or self.product_id.uom_po_id.id,
            'product_id': self.product_id.id,
            'price_unit': self.price_unit,
            'discount': self.discount,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
        if order:
            vals['order_id'] = order
        return vals
