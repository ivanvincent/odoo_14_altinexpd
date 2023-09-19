from email.policy import default
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import odoo.addons.decimal_precision as dp

class QuotationRequestForm(models.Model):
    _name = 'quotation.request.form'

    name = fields.Char(string='Name', default='New')
    partner_id = fields.Many2one('res.partner', string='Customer')
    date = fields.Date(string='Date')
    design_code_id = fields.Many2one('makloon.design', string='Design')
    image_binary = fields.Binary(string='Drawing', store=False,)
    line_ids = fields.One2many('quotation.request.form.line', 'qrf_id', 'Line')
    state = fields.Selection(
        [("draft", "Draft"), ("confirm", "Confirm")], string='State', default='draft')
    amount_tax = fields.Monetary(
        string='Taxes', currency_field='currency_id', compute='_compute_amount')
    amount_untaxed = fields.Monetary(
        string='Amount Untaxed', currency_field='currency_id', compute='_compute_amount')
    amount_total = fields.Monetary(
        string='Amount Total', currency_field='currency_id', compute='_compute_amount')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', store=True,)
    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency',
                                          readonly=True, store=True, help='Utility field to express amount currency')
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Term', force_save=True)
    
    machine_id = fields.Many2one('machine', string='Machine')
    
    no_sample = fields.Char(string='No Sample')
    
    up_kpd = fields.Many2one('attn', string='Attn')
    attn_ids = fields.Many2many('attn', string='Attn', compute='compute_attn_ids')



    # alamat  = fields.Text(string='Alamat', related='up_kpd.alamat')
    # kota    = fields.Char(string='Kota', related='up_kpd.kota')
    # phone   = fields.Char(string='Phone', related='up_kpd.phone')
    # mobile  = fields.Char(string='Mobile', related='up_kpd.mobile')
    # fax     = fields.Char(string='Fax', related='up_kpd.fax')
    # email   = fields.Char(string='Email', related='up_kpd.email')
    
    note_so = fields.Char(string='Note')
    perihal = fields.Selection([("Penawaran Harga Punch & Dies","Penawaran Harga Punch & Dies"),
                                ("Penawaran Harga","Penawaran Harga")], string='Perihal', required=True, )
    tanggal_berlaku = fields.Date(string='Tanggal Berlaku', compute="compute_tanggal_berlaku")
    no_quotation_accurate = fields.Char(string='No Quotation Accurate')
    kode_mkt_id = fields.Many2one('kode.mkt', string='Kode Mkt')
    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                 default='percent')
    discount_rate = fields.Float('Discount Rate', digits=dp.get_precision('Account'), )
    amount_discount = fields.Monetary(string='Discount', store=True, compute='_compute_amount',
                                      digits=dp.get_precision('Account'), track_visibility='always')
    # payment_term_ids = fields.Many2many('account.payment.term', string='Payment Term Ids', related='partner_id.payment_term_ids')
    # kode_mkt_ids = fields.Many2many('kode.mkt', string='Kode Mkt Ids', related='partner_id.kode_mkt_ids')
    
    # @api.onchange('partner_id')
    # def get_kode_mkt(self):
        # if self.partner_id:
            # self.kode_mkt = self.partner_id.kode_mkt
            # self.payment_term_id = self.partner_id.property_payment_term_id.id

    @api.depends('line_ids.sub_total', 'line_ids.tax_ids', 'discount_rate', 'discount_type')
    def _compute_amount(self):
        for rec in self:
            total_tax = 0
            total_untax = 0
            for l in rec.line_ids:
                for t in l.tax_ids:
                    total_tax += l.sub_total * (t.amount / 100)
                total_untax += l.sub_total
            amount_discount = total_untax * rec.discount_rate / 100 if rec.discount_type == 'percent' else rec.discount_rate
            rec.amount_tax = total_tax
            rec.amount_untaxed = total_untax
            rec.amount_total = total_tax + total_untax - amount_discount
            rec.amount_discount = amount_discount

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('QuotationRequestForm')
        vals['name'] = sequence
        res = super(QuotationRequestForm, self).create(vals)
        return res
    
    def action_confirm(self):
        self.state = 'confirm'

    

    # def action_confirm(self):
    #     seq = self.env['ir.sequence'].next_by_code('request.engineering')
    #     'No Drawing', 'Ukuran Bahan'
    #     material = ['Hob', 'Baut', 'Tonase', 'Sepi']
    #     engineering = self.env['request.engineering'].create({
    #         'name': seq,
    #         # 'type': 'from_quotation',
    #         'type_id': self.env['request.engineering.type'].search([('name', '=', 'Quotation')], limit=1).id,
    #         'quotation_id': self.id,
    #         'line_ids': [(0, 0, {'product_id': d.product_id.id}) for d in self.line_ids]
    #     })
    #     self.request_engineering_id = engineering.id
    #     self.state = 'confirm'

    # def action_generate(self):
    #     for product_tmpl in self.product_tmpl_ids:
    #         machine_attr = self.env['product.template.attribute.line'].sudo().search(
    #             [('product_tmpl_id', '=', product_tmpl.id), ('attribute_id.name', '=', 'MACHINE')], limit=1)
    #         size_attr = self.env['product.template.attribute.line'].sudo().search(
    #             [('product_tmpl_id', '=', product_tmpl.id), ('attribute_id.name', '=', 'SIZE')], limit=1)
    #         shape_attr = self.env['product.template.attribute.line'].sudo().search(
    #             [('product_tmpl_id', '=', product_tmpl.id), ('attribute_id.name', '=', 'SHAPE')], limit=1)

    #         attribute_obj = self.env['product.attribute']
    #         value_obj = self.env['product.attribute.value']
    #         attr_machine = attribute_obj.search(
    #             [('name', '=', 'MACHINE')], limit=1).id
    #         attr_size = attribute_obj.search(
    #             [('name', '=', 'SIZE')], limit=1).id
    #         attr_shape = attribute_obj.search(
    #             [('name', '=', 'SHAPE')], limit=1).id

    #         machine_vals = value_obj.sudo().search(
    #             [('name', '=', self.machine_id.name), ('attribute_id', '=', attr_machine)], limit=1)
    #         if not machine_vals:
    #             machine_vals = self.env['product.attribute.value'].create({
    #                 "attribute_id": attr_machine,
    #                 "name": self.machine_id.name,
    #             })
    #         if machine_attr:
    #             machine_attr.sudo().write({
    #                 "attribute_id": attr_machine,
    #                 "value_ids": [(4, machine_vals.id)],
    #             })
    #         else:
    #             a = machine_attr.sudo().create({
    #                 'product_tmpl_id': product_tmpl.id,
    #                 'attribute_id': attr_machine,
    #                 'value_ids': [(6, 0, machine_vals.ids)]
    #             })

    #         size_vals = value_obj.sudo().search(
    #             [('name', '=', self.size.name), ('attribute_id', '=', attr_size)], limit=1)
    #         if not size_vals:
    #             size_vals = self.env['product.attribute.value'].create({
    #                 "attribute_id": attr_size,
    #                 "name": self.size.name,
    #             })

    #         if size_attr:
    #             size_attr.sudo().write({
    #                 "attribute_id": attr_size,
    #                 "value_ids": [(4, size_vals.id)],
    #             })
    #         else:
    #             b = size_attr.sudo().create({
    #                 'product_tmpl_id': product_tmpl.id,
    #                 'attribute_id': attr_size,  # attribute design
    #                 'value_ids': [(6, 0, [size_vals.id])]
    #             })

    #         shape_vals = value_obj.sudo().search(
    #             [('name', '=', self.shape), ('attribute_id', '=', attr_shape)], limit=1)
    #         if not shape_vals:
    #             shape_vals = self.env['product.attribute.value'].create({
    #                 "attribute_id": attr_shape,
    #                 "name": self.shape,
    #             })

    #         if shape_attr:
    #             shape_attr.sudo().write({
    #                 "attribute_id": attr_shape,
    #                 "value_ids": [(4, shape_vals.id)],
    #             })
    #         else:
    #             b = shape_attr.sudo().create({
    #                 'product_tmpl_id': product_tmpl.id,
    #                 'attribute_id': attr_shape,  # attribute design
    #                 'value_ids': [(6, 0, [shape_vals.id])]
    #             })


        # # for color in self.color_ids:
        #     combination = self.env['product.template.attribute.value'].search(
        #         [('product_tmpl_id', '=', product_tmpl.id), ('product_attribute_value_id', 'in', [machine_vals.id, size_vals.id, shape_vals.id])])
        #     # if not combination:
        #     variant = product_tmpl._get_variant_for_combination(combination)
        #     if not variant:
        #         variant = product_tmpl._create_product_variant(
        #             combination, True)
        #     # variant = self.product_id._get_variant_id_for_combination(combination)
        #     # if self.product_id._is_combination_possible(combination):
        #     #     print('s')

        #     # [color.sudo().write({"variant_id":variant.id}) for color in self.design_id.line_ids.filtered(lambda x:x.color_id.id == color.id)]
        #     # variant.sudo().write({
        #     #         "design_id":self.design_id.id
        #     #     })
        #     # history = self.env['sale.product.history'].search([('product_id','=',variant.id),('partner_id','=',self.partner_id.id)],limit=1)
        #     if variant not in self.line_ids.mapped('product_id'):
        #         self.line_ids = [
        #             (0, 0, {"product_id": variant.id, "quantity": 1, "price_unit": 1, })]

    @api.depends('date')
    def compute_tanggal_berlaku(self):
        for rec in self:
            if rec.date:
                rec.tanggal_berlaku = rec.date + relativedelta(days=30)
            else:
                rec.tanggal_berlaku = False

    

    def action_set_to_draft(self):
        self.state = 'draft'

    @api.depends('partner_id')
    def compute_attn_ids(self):
        for rec in self:
            if rec.partner_id:
                rec.attn_ids = [(6, 0, rec.partner_id.attn_ids.ids)]
            else:
                rec.attn_ids = False

    

class QuotationRequestFormLine(models.Model):
    _name = 'quotation.request.form.line'
    
    qrf_id = fields.Many2one('quotation.request.form', string='QRF')
    jenis_id = fields.Many2one('master.jenis', string='Jenis')
    line_spec_ids = fields.One2many('quotation.request.form.line.specification', 'qrf_line_id', 'Line Spec')
    name = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Price Unit')
    tax_ids = fields.Many2many(comodel_name='account.tax', string='Tax')
    sub_total = fields.Float(string='Sub Total', compute='compute_sub_total')


    product_id = fields.Many2one('product.product', string='Product')
    embos = fields.Char(string='Embos')
    tip = fields.Char(string='Tip')
    size = fields.Char(string='Size')            
    treatment_id = fields.Many2one('treatment', string='Heat Treatment')
    product_ingredient_id = fields.Many2one(
        'product.product', string='Material')
    shape = fields.Char(string='Shape')
    qty_available = fields.Float(
        string='Qty Available', compute='_compute_qty_available')
    kd_bahan = fields.Char(string='Kode Bahan')
    lapisan = fields.Selection(
        [("Coat", "Coat"), ("Plat", "Plat")], string='Surface Finish')


    @api.depends('quantity', 'price_unit')
    def compute_sub_total(self):
        for a in self:
            exclude = a.quantity * a.price_unit
            a.sub_total = exclude

    def _compute_qty_available(self):
        for rec in self:
            rec.qty_available = 0
    
    def create_specification_detail(self):
        self.ensure_one()
        mak_order = self.env['quotation.request.form.line.specification']


class QuotationRequestFormLineSpecification(models.Model):
    _name = 'quotation.request.form.line.specification'

    qrf_line_id = fields.Many2one('quotation.request.form.line', string='QRF')
    specifications_id = fields.Many2one('specifications', string='Specifications')
    spect_name = fields.Char(string='Nama Spefisikasi')
    desc = fields.Char(string='Desc')
    harga = fields.Float(string='Harga')
    