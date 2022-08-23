from email.policy import default
from odoo import models, fields, api

class Quotation(models.Model):
    _name = 'quotation'

    name = fields.Char(string='Name', default='New')
    partner_id = fields.Many2one('res.partner', string='Customer')
    date = fields.Date(string='Date')
    design_code_id = fields.Char(string='Design Code') #sementara
    image_binary = fields.Binary(string='Image', store=False,)
    line_ids = fields.One2many('quotation.line', 'quotation_id', 'Line')
    state = fields.Selection([("draft","Draft"),("confirm","Confirm")], string='State', default='draft')

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