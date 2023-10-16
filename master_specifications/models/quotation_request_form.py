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
    attn_ids = fields.Many2many('attn', string='Attn', 
    # compute='compute_attn_ids'
    )
    
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
    pic_name = fields.Char(string='PIC Name')
    pic_email = fields.Char(string='PIC Email')
    pic_phone = fields.Char(string='PIC Mobile Phone (WA)')
    note = fields.Char('Notes')

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
        seq_id = self.env.ref('master_specifications.qrf_seq')
        vals['name'] = seq_id.next_by_id() if seq_id else '/'
        return super(QuotationRequestForm, self).create(vals)
    
    def action_confirm(self):
        self.state = 'confirm'

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
    price_unit = fields.Float(string='Price Unit', compute='_compute_price_unit')
    tax_ids = fields.Many2many(comodel_name='account.tax', string='Tax')
    sub_total = fields.Float(string='Sub Total', compute='_compute_sub_total')
    state = fields.Selection(
        [("draft", "Draft"), ("confirm", "Confirm")], string='State', default='draft')


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
    line_qty_ids = fields.One2many('quotation.request.form.line.quantity', 'qrf_line_id', 'Line Qty')
    
    # @api.depends('line_spec_ids', 'price_unit' , 'sub_total')
    @api.depends('price_unit')
    def _compute_price_unit(self):
        for rec in self:
            tot_price = 0
            for l in rec.line_spec_ids:
                tot_price += l.specifications_id.harga
            rec.price_unit = tot_price
                    
    #         exclude = self.quantity * tot_price
    #         self.sub_total = exclude


            # for t in l.tax_ids:
            #         total_tax += l.sub_total * (t.amount / 100)
            #     total_untax += l.sub_total

    @api.depends('sub_total')
    def _compute_sub_total(self):
        for a in self:
            _total = 0
            for l in a.line_spec_ids:
                _total += l.total
            a.sub_total = _total
            # exclude = a.quantity * a.price_unit
            # a.sub_total = exclude
            # a.price_unit = sum(a.line_spec_ids.specifications_id.harga)

    def _compute_qty_available(self):
        for rec in self:
            rec.qty_available = 0
    
    def create_specification_detail(self):
        self.ensure_one()
        # spec = self.env['master.require'].search([('jenis_ids', 'in', self.jenis_id.ids)])
        spec = self.env['master.require'].search([('active', '=', True)])
        data = []
        if not any(self.line_spec_ids):
            for line in spec:
                if self.jenis_id in line.jenis_ids: 
                    data.append((0, 0, {
                        'require_id': line.id
                    }))
            self.line_spec_ids = data 

        list_qty = []
        if not any(self.line_qty_ids):
            for line in self.jenis_id.qty_ids:
                list_qty.append((0, 0, {
                    'qty_id': line.id
                }))
            self.line_qty_ids = list_qty 
        action = self.env.ref('master_specifications.quotation_request_form_line_action').read()[0]
        action['res_id'] = self.id
        return action

    # @api.onchange('qty')
    def action_refresh_spec(self):
        self.ensure_one()
        spec = self.line_spec_ids.filtered(lambda x: x.require_id.id == 79)
        # for t in spec:
        if self.line_qty_ids.filtered(lambda x: x.qty_id.id == 3 )  and self.line_qty_ids.filtered(lambda x: x.qty_id.id == 3 ).qty == 1:
            spec.write({"specifications_id": 527})
            print("A")
        elif self.line_qty_ids.filtered(lambda x: x.qty_id.id == 3 )  and self.line_qty_ids.filtered(lambda x: x.qty_id.id == 3 ).qty >= 1:
            spec.write({"specifications_id": 528})
            print("B")
        action = self.env.ref('master_specifications.quotation_request_form_line_action').read()[0]
        action['res_id'] = self.id
        return action


class QuotationRequestFormLineSpecification(models.Model):
    _name = 'quotation.request.form.line.specification'
    # _order = "urutan asc"

    qrf_line_id = fields.Many2one('quotation.request.form.line', string='QRF')
    jenis_id = fields.Many2one('master.jenis', string='Jenis', related='qrf_line_id.jenis_id')
    require_id = fields.Many2one('master.require', string='Category')
    urutan = fields.Integer(string='Urutan', related='require_id.urutan')
    specifications_id = fields.Many2one('specifications', string='Items', domain="[('jenis_id', '=',jenis_id)]")
    # spec_id = fields.Many2one('master.require',string='Spefisikasi', related='specifications_id.spec_id')
    # spect_name = fields.Char(string='Kode', related='specifications_id.spect_name')
    spect_name = fields.Char(string='Kode', related='specifications_id.spect_name')
    desc_detail = fields.Text(string='Description Detail', related='specifications_id.desc_detail')
    harga = fields.Float(string='Unit Price', related='specifications_id.harga')
    urutan = fields.Integer(string='Urutan', related='specifications_id.urutan')
    state = fields.Selection(
        [("draft", "Draft"), ("confirm", "Confirm")], string='State', default='draft')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal')
    total = fields.Float(string='TOTAL', compute='_compute_total')

    # @api.depends('harga', 'qrf_line_id.line_qty_ids.qty', 'require_id', 'specifications_id')
    @api.depends('harga', 'require_id', 'specifications_id')
    def _compute_subtotal(self):
        for rec in self:
            spec = rec.specifications_id
            if spec:
                if spec.rumus_subtotal == 'HARGA' or not spec.rumus_subtotal:
                    rec.subtotal = rec.harga
                else:
                    rumus = spec.rumus_subtotal.replace("(", "( ").replace(")", " )")
                    if rumus:
                        splited = rumus.split(" ")
                        final = []
                        for s in splited:
                            master_quantity = rec.qrf_line_id.line_qty_ids.filtered(lambda x: x.qty_id.name == s)
                            if s == master_quantity.qty_id.name:
                                final.append(str(master_quantity.qty))
                            elif s == 'HARGA':
                                final.append(str(rec.harga))
                            else:
                                final.append(str(s))
                        rec.subtotal = eval(' '.join(final))
                        # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++",final)
                    else:
                        rec.subtotal = rec.harga
            else:
                rec.subtotal = rec.harga

    # @api.depends('harga', 'qrf_line_id.line_qty_ids.qty', 'require_id', 'specifications_id')
    @api.depends('harga', 'require_id', 'specifications_id')
    def _compute_total(self):
        for rec in self:
            spec = rec.specifications_id
            if spec:
                if spec.rumus_total == 'SUBTOTAL' or not spec.rumus_total:
                    rec.total = rec.subtotal
                else:
                    rumus = spec.rumus_total.replace("(", "( ").replace(")", " )")
                    if rumus:
                        splited = rumus.split(" ")
                        final = []
                        for s in splited:
                            master_quantity = rec.qrf_line_id.line_qty_ids.filtered(lambda x: x.qty_id.name == s)
                            if s == master_quantity.qty_id.name:
                                final.append(str(master_quantity.qty))
                            elif s == 'SUBTOTAL':
                                final.append(str(rec.subtotal))
                            elif s == 'HARGA':
                                final.append(str(spec.harga))
                            else:
                                final.append(str(s))
                        rec.total = eval(' '.join(final))
                        # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++",final)
                    else:
                        rec.total = rec.subtotal
            else:
                rec.total = rec.subtotal

    # @api.onchange('qrf_line_id.line_qty_ids.qty')
    # def onchange_qty(self):
    #     if self.jenis_id.id == 1:
    #         spec = self.qrf_line_id.line_qty_ids.filtered(lambda x: x.qty_id.id == 3)
    #         for t in spec:
    #             if t.qty == 1:
    #                 self.specifications_id == 527
    #             elif t.qty >= 1:
    #                 self.specifications_id == 528

class QuotationRequestFormLineQuantity(models.Model):
    _name = 'quotation.request.form.line.quantity'
    _order = "urutan asc"

    qrf_line_id = fields.Many2one('quotation.request.form.line', string='QRF')
    jenis_id    = fields.Many2one('master.jenis', string='Jenis', related='qrf_line_id.jenis_id')
    qty_id      = fields.Many2one('master.qty', string='Quantity')
    urutan      = fields.Integer(string='Urutan', related='qty_id.urutan')
    qty         = fields.Float(string='Qty')

    # @api.onchange('qty')
    def action_refresh_spec(self):
        # print("onchange_qty===============")
        # if self.jenis_id.id == 1:
        spec = self.qrf_line_id.line_spec_ids.filtered(lambda x: x.require_id.id == 79)
        # for t in spec:
        if self.qty_id.id == 3 and self.qty == 1:
            spec.sudo().write({"specifications_id": 527})
            print("A")
        elif self.qty_id.id == 3 and self.qty >= 1:
            spec.sudo().write({"specifications_id": 528})
            print("B")

