from email.policy import default
from odoo import models, fields, api

class Quotation(models.Model):
    _name = 'quotation'

    name = fields.Char(string='Name', default='New')
    partner_id = fields.Many2one('res.partner', string='Customer')
    date = fields.Date(string='Date')
    # design_code_id = fields.Char(string='Design Code') #sementara
    design_code_id = fields.Many2one('makloon.design', string='Design')
    image_binary = fields.Binary(string='Drawing', store=False,)
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
    shape = fields.Selection([("caplet","Caplet"),("round","Round")], string='Shape')
    size = fields.Many2one('size', string='Size')
    machine_id = fields.Many2one('machine', string='Machine')
    product_tmpl_ids = fields.Many2many('product.template',
        string='Product Template'
        )

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
    
    def action_generate(self):
        print("action_generate hihi")
        for product_tmpl in self.product_tmpl_ids:
            machine_attr = self.env['product.template.attribute.line'].sudo().search([('product_tmpl_id','=',product_tmpl.id),('attribute_id.name','=', 'MACHINE')],limit=1)
            size_attr = self.env['product.template.attribute.line'].sudo().search([('product_tmpl_id','=',product_tmpl.id),('attribute_id.name','=', 'SIZE')],limit=1)
            attribute_obj = self.env['product.attribute']
            value_obj = self.env['product.attribute.value']
            attr_machine = attribute_obj.search([('name', '=', 'MACHINE')], limit=1).id
            attr_size = attribute_obj.search([('name', '=', 'SIZE')], limit=1).id

            print("attr_machine", attr_machine)
            print("attr_size", attr_size)
            machine_vals = value_obj.sudo().search([('name','=',self.machine_id.name), ('attribute_id', '=', attr_machine)],limit=1)
            if not machine_vals:
                machine_vals = self.env['product.attribute.value'].create({
                    "attribute_id": attr_machine,
                    "name": self.machine_id.name,
                })
            if machine_attr:
                machine_attr.sudo().write({
                    "attribute_id": attr_machine,
                    "value_ids":[(4, machine_vals.id)],
                })
            else:
                a = machine_attr.sudo().create({
                    'product_tmpl_id': product_tmpl.id,
                    'attribute_id': attr_machine,
                    'value_ids': [(6, 0, machine_vals.ids)]
                })
                print("aaaaaaaaa", a)

            size_vals = value_obj.sudo().search([('name','=',self.size.name), ('attribute_id', '=', attr_size)],limit=1)
            if not size_vals:
                size_vals = self.env['product.attribute.value'].create({
                    "attribute_id": attr_size,
                    "name": self.size.name,
                })
            
            if size_attr:
                size_attr.sudo().write({
                    "attribute_id": attr_size,
                    "value_ids":[(4,size_vals.id)],
                })
            else:
                b = size_attr.sudo().create({
                    'product_tmpl_id': product_tmpl.id,
                    'attribute_id': attr_size, #attribute design 
                    'value_ids': [(6, 0, [size_vals.id])]
                })
                print("bbbbbbbbbb", b)

        # for color in self.color_ids:
            combination = self.env['product.template.attribute.value'].search([('product_tmpl_id','=',product_tmpl.id),('product_attribute_value_id','in',[machine_vals.id, size_vals.id])])
            # if not combination:
            variant = product_tmpl._get_variant_for_combination(combination)
            if not variant:
                variant = product_tmpl._create_product_variant(combination, True)
            # variant = self.product_id._get_variant_id_for_combination(combination)
            # if self.product_id._is_combination_possible(combination):
            #     print('s')
            
            # [color.sudo().write({"variant_id":variant.id}) for color in self.design_id.line_ids.filtered(lambda x:x.color_id.id == color.id)]
            # variant.sudo().write({
            #         "design_id":self.design_id.id
            #     })
            # history = self.env['sale.product.history'].search([('product_id','=',variant.id),('partner_id','=',self.partner_id.id)],limit=1)
            if variant not in self.line_ids.mapped('product_id'):
                self.line_ids = [(0,0,{"product_id":variant.id,"quantity": 1, "price_unit": 1, })]


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