from email.policy import default
from odoo import models, fields, api

class Quotation(models.Model):
    _name = 'quotation'

    name = fields.Char(string='Name', default='New')
    partner_id = fields.Many2one('res.partner', string='Customer')
    date = fields.Date(string='Date')
    # design_code_id = fields.Char(string='Design Code') #sementara
    design_code_id = fields.Many2one('makloon.design', string='Design')
    image_binary = fields.Binary(string='Image', store=False,)
    line_ids = fields.One2many('quotation.line', 'quotation_id', 'Line')
    state = fields.Selection([("draft","Draft"),("confirm","Confirm")], string='State', default='draft')
    amount_tax = fields.Monetary(string='Taxes', currency_field='currency_id', compute='_compute_amount')
    amount_untaxed = fields.Monetary(string='Amount Untaxed', currency_field='currency_id', compute='_compute_amount')
    amount_total = fields.Monetary(string='Amount Total', currency_field='currency_id', compute='_compute_amount')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', store=True,)
    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency',
                                        readonly=True, store=True, help='Utility field to express amount currency')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')
    drawing_internal = fields.Binary(string='Drawing Internal', related='design_code_id.drawing_internal')
    drawing_external = fields.Binary(string='Drawing External', related='design_code_id.drawing_external')

    @api.depends('line_ids.sub_total', 'line_ids.tax_ids')
    def _compute_amount(self):
        for rec in self:
            total_tax = 0
            total_untax = 0
            for l in rec.line_ids:
                for t in l.tax_ids:
                    total_tax += l.sub_total * (t.amount / 100)
                total_untax += l.sub_total
            rec.amount_tax = total_tax
            rec.amount_untaxed = total_untax
            rec.amount_total = total_tax + total_untax



    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('quotation')
        vals['name'] = sequence
        res = super(Quotation, self).create(vals)
        return res

    def action_confirm(self):
        self.state = 'confirm'


class QuotationLine(models.Model):
    _name = 'quotation.line'

    product_id = fields.Many2one('product.product', string='Product')
    embos = fields.Char(string='Embos')
    tip = fields.Char(string='Tip')
    size = fields.Char(string='Size')
    quantity = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Price Unit')
    tax_ids = fields.Many2many(comodel_name='account.tax', string='Tax')
    sub_total = fields.Float(string='Sub Total', compute='compute_sub_total')
    quotation_id = fields.Many2one('quotation', string='Quotation')
    treatment_id = fields.Many2one('treatment', string='Treatment')

    @api.depends('quantity','price_unit')
    def compute_sub_total(self):
        for a in self:
            exclude = a.quantity * a.price_unit
            a.sub_total = exclude