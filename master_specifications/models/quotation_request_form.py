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
        [("draft", "Draft"), ("confirm", "Approval Requested"), ("approved", "Approved"), ("order_processed", "Order Processed")], string='State', default='draft')
    amount_tax = fields.Monetary(
        string='Taxes', currency_field='currency_id', compute='_compute_amount')
    amount_untaxed = fields.Monetary(
        string='Amount Untaxed', currency_field='currency_id', compute='_compute_amount')
    amount_total = fields.Monetary(
        string='Total', currency_field='currency_id', compute='_compute_amount')
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
                                ("Penawaran Harga","Penawaran Harga")], string='Perihal',)
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
    note = fields.Text('Notes')
    payment_terms = fields.Char('Payment Terms')
    delivery_terms = fields.Char('Delivery Terms')
    sales_condition = fields.Char('Sales Condition')
    valid_date = fields.Date('Valid To')
    reference = fields.Char('Reference')
    processed = fields.Boolean(string='Processed ?', default=False)
    amount_tax_11 = fields.Monetary(
        string='Taxes (PPN 11%)', currency_field='currency_id', compute='_compute_amount')
    amount_tax_pph23 = fields.Monetary(
        string='Taxes (PPh 23)', currency_field='currency_id', compute='_compute_amount' )
    amount_subtotal = fields.Monetary(
        string='Subtotal', currency_field='currency_id', compute='_compute_amount')
    tax_id = fields.Many2one('account.tax', string='Tax Type')
    notes_to_customer = fields.Text(string='Notes to customer')
    type = fields.Selection([("1","1"),("2","2"),("3","3")], string='Type')
    end_user_name = fields.Many2one('res.partner', string='End User Name')
    end_user_machine_serial = fields.Char(string='End User Machine Serial No.')
    amount_untaxed_2 = fields.Monetary(
        string='Amount Untaxed', currency_field='currency_id', compute='_compute_amount')
    amount_total_2 = fields.Monetary(
        string='Total', currency_field='currency_id', compute='_compute_amount')
    amount_tax_2 = fields.Monetary(
        string='Taxes', currency_field='currency_id', compute='_compute_amount')
    amount_price_discount = fields.Float(string='Price After Discount', compute='_compute_amount')
    station_no = fields.Char(string='Station Number')
    drawing_attachment_line_ids = fields.One2many('drawing.attachment', 'qrf_id', 'Drawing')
    qrf_attachment_line_ids = fields.One2many('qrf.attachment', 'qrf_id', 'QRF')
    user_id = fields.Many2one('res.users',string='Responsible Sales'
    ,related='partner_id.user_id'
    )
    so_count = fields.Integer(string='Sale Order Count',compute="_compute_so")
    billing_address = fields.Char(related='partner_id.street', string='Billing Address', required=True)
    shipping_address = fields.Many2one('res.partner', string='Shipping Address', required=True)
    po_attachment_line_ids = fields.One2many('po.attachment', 'qrf_id', 'QRF')
    child_ids = fields.One2many(related='end_user_name.child_ids', string='Contact')

    @api.depends('line_ids.sub_total', 'line_ids.price_discount', 'line_ids.tax_ids', 'discount_rate', 'discount_type')
    def _compute_amount(self):
        for rec in self:
            total_tax = 0
            total_untax = 0
            total_ppn11 = 0
            total_pph23 = 0
            total_untax_2 = 0
            total_tax_2 = 0
            for l in rec.line_ids:
                # for t in l.tax_ids:
                #     total_tax += l.sub_total * (t.amount / 100)

                total_untax += l.sub_total
                total_ppn11 += l.total_tax_11
                total_pph23 += l.total_tax_pph23
                total_untax_2 += l.price_discount
            amount_discount = total_untax * rec.discount_rate / 100 if rec.discount_type == 'percent' else rec.discount_rate

            total_price_discount = total_untax - amount_discount
            total_tax = total_untax * (rec.tax_id.amount / 100)
            total_tax_2 = total_price_discount * (rec.tax_id.amount / 100)
            rec.amount_tax = total_tax
            rec.amount_untaxed = total_untax
            rec.amount_total = total_untax + total_tax
            rec.amount_discount = amount_discount
            rec.amount_tax_11 = total_ppn11
            rec.amount_tax_pph23 = total_pph23
            rec.amount_subtotal = total_untax - amount_discount
            rec.amount_untaxed_2 = total_untax_2
            rec.amount_total_2 = total_price_discount + total_tax_2
            rec.amount_tax_2 = total_tax_2
            rec.amount_price_discount = total_price_discount



    @api.model
    def create(self, vals):
        seq_id = self.env.ref('master_specifications.qrf_seq')
        vals['name'] = seq_id.next_by_id() if seq_id else '/'
        return super(QuotationRequestForm, self).create(vals)
    
    def action_confirm(self):
        self.state = 'confirm'

    def action_create_so(self):
        # self.state = 'order_processed'
        data = []
        for line in self.line_ids:
            product = self.env['product.product'].search([('name','=',line.name)],limit=1)
            if not product :
                product = self.env['product.product'].create({
                    "name":line.name,
                    "type":"product",
                    # "product_tmpl_id":line.name,
                    "categ_id": 27,
                })
            data.append((0,0,{
                    'product_id':product.id,
                    # 'name':line.name,
                    'price_unit':line.price_unit,
                    'product_uom_qty':line.quantity,
                    'tax_id':[(6, 0, self.tax_id.ids)],
                    'price_subtotal':line.sub_total,
                    }))
        sale_order_id = self.env['sale.order'].create({
                    'dqups_id':self.id,
                    'name':self.name,
                    'partner_id':self.partner_id.id,
                    'date_order':self.date,
                    'payment_term_id': self.payment_terms,
                    'amount_untaxed': self.amount_untaxed,
                    'partner_invoice_id':self.partner_id.id,
                    'partner_shipping_id':self.partner_id.id,
                    # 'option_vip':'HIGH RISK',
                    # 'payment_term_id': self.payment_terms,
                    # 'term_of_payment': self.payment_terms,
                    # 'up_kpd': self.pic_name,
                    # 'amount_tax':self.amount_tax_2,
                    # 'amount_total':self.amount_total_2,
                    # 'term_of_payment': self.payment_terms,
                    'order_line': data
                })

    def action_view_so(self):
        action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
        action['domain'] = [('dqups_id','=',self.id)]
        action['context'] = {}
        return action

    def _compute_so(self):
        for sale in self:
            sale.so_count = len(sale.line_ids)


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

    def action_approve(self):
        self.state = 'approved'

    def action_process(self):
        self.processed = True
        self.state = 'order_processed'


    def action_print(self):
        return {
            'type'      : 'ir.actions.act_window',
            'name'      : "Print",
            'res_model' : 'print.qrf.wizard',
            'target'    : 'new',
            'view_id'   : self.env.ref('master_specifications.print_qrf_wizard_form').id,
            'view_mode' : 'form',
            'context'   : {'default_qrf_id': self.id,},
        }
    
    def action_print_dqups2(self):
        return {
            'type'      : 'ir.actions.act_window',
            'name'      : "Print",
            'res_model' : 'print.qrf.wizard',
            'target'    : 'new',
            'view_id'   : self.env.ref('master_specifications.print_qrf_dqups2_form').id,
            'view_mode' : 'form',
            'context'   : {'default_qrf_id': self.id,},
        }

    def action_print_dqups3(self):
        return {
            'type'      : 'ir.actions.act_window',
            'name'      : "Print",
            'res_model' : 'print.qrf.wizard',
            'target'    : 'new',
            'view_id'   : self.env.ref('master_specifications.print_qrf_dqups3_form').id,
            'view_mode' : 'form',
            'context'   : {'default_qrf_id': self.id,},
        }


class QuotationRequestFormLine(models.Model):
    _name = 'quotation.request.form.line'
    
    qrf_id = fields.Many2one('quotation.request.form', string='QRF')
    jenis_id = fields.Many2one('master.jenis', string='Jenis')
    line_spec_ids = fields.One2many('quotation.request.form.line.specification', 'qrf_line_id', 'Line Spec')
    name = fields.Char(string='Description')
    quantity = fields.Integer(string='Quantity', compute='compute_quantity')
    price_unit = fields.Float(string='Price Unit', compute='_compute_price_unit')
    tax_ids = fields.Many2many(comodel_name='account.tax', string='Tax')
    sub_total = fields.Float(string='Sub Total', compute='_compute_amount')
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
    amount_tax = fields.Monetary(
        string='Taxes', currency_field='currency_id', compute='_compute_amount')
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', store=True,)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    total_tax_11 = fields.Monetary(
        string='Taxes (PPN 11%)', currency_field='currency_id', compute='_compute_tax')
    total_tax_pph23 = fields.Monetary(
        string='Taxes (PPh 23)', currency_field='currency_id', compute='_compute_tax_pph'
        )
    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                 default='percent')
    discount_rate = fields.Float('Discount Rate', digits=dp.get_precision('Account'), )
    amount_discount = fields.Monetary(string='Discount', store=False,
                                        compute='_compute_amount',
                                        digits=dp.get_precision('Account'))
    price_discount = fields.Float(string='Price After Discount', compute='_compute_amount')

    @api.depends('sub_total', 'tax_ids', 'qrf_id.type')
    def _compute_amount(self):
        for rec in self:
            total_tax = 0
            total_untax = 0
            # for l in rec.line_ids:
            for t in rec.tax_ids:
                total_tax += rec.sub_total * (t.amount / 100)
            total_untax += rec.sub_total
            amount_discount = rec.price_unit * rec.discount_rate / 100 if rec.discount_type == 'percent' else rec.discount_rate
            tot_price_disc = rec.price_unit - amount_discount
            tot_subtotal = tot_price_disc * rec.quantity
            rec.amount_tax = total_tax
            # rec.amount_untaxed = total_untax
            # rec.amount_total = total_tax + total_untax - amount_discount
            rec.amount_discount = amount_discount
            rec.price_discount = tot_price_disc

            if rec.qrf_id.type == '1':
                rec.sub_total = rec.quantity * rec.price_unit
            elif rec.qrf_id.type == '2':
                rec.sub_total = rec.quantity * rec.price_discount
            elif rec.qrf_id.type == '3':
                rec.sub_total = sum(rec.line_spec_ids.mapped('total'))
            # rec.sub_total = tot_subtotal
    
    @api.depends('sub_total', 'tax_ids')
    def _compute_tax(self):
        for rec in self:
            rec.total_tax_11 = 0
            if any(rec.tax_ids):
                for t in rec.tax_ids.filtered(lambda x:x.id == 2):
                    if t:
                        rec.total_tax_11 = rec.sub_total * (11/100)
                    else:
                        rec.total_tax_11 = 0
            else:
                rec.total_tax_11 = 0

    @api.depends('sub_total', 'tax_ids')
    def _compute_tax_pph(self):
        for rec in self:
            rec.total_tax_pph23 = 0
            if any(rec.tax_ids):
                for t in rec.tax_ids.filtered(lambda x:x.id == 6):
                    if t:
                        rec.total_tax_pph23 = rec.sub_total * (2/100)
                    else:
                        rec.total_tax_pph23 = 0
            else:
                rec.total_tax_pph23 = 0

    # @api.depends('line_spec_ids', 'price_unit' , 'sub_total')
    @api.depends('price_unit')
    def _compute_price_unit(self):
        for rec in self:
            tot_price = 0
            for l in rec.line_spec_ids:
                tot_price += l.subtotal if l.subtotal else l.total
            rec.price_unit = tot_price

    # @api.depends('qrf_id.type')
    # def _compute_sub_total(self):
    #     for a in self:
    #         if a.qrf_id.type == '1':
    #             a.sub_total = a.quantity * a.price_unit
    #         elif a.qrf_id.type == '2':
    #             a.sub_total = a.price_unit - a.amount_discount
    #         elif a.qrf_id.type == '3':
    #             a.sub_total = sum(a.line_spec_ids.mapped('total'))
            # exclude = a.quantity * a.price_unit
            # a.sub_total = exclude
            # a.price_unit = sum(a.line_spec_ids.specifications_id.harga)
    
    # @api.depends('price_discount')
    # def _compute_price_discount(self):
    #     for a in self:
    #         a.price_discount = a.price_unit - a.amount_discount

    def _compute_qty_available(self):
        for rec in self:
            rec.qty_available = 0
    
    def create_specification_detail(self):
        self.ensure_one()
        # spec = self.env['master.require'].search([('jenis_ids', 'in', self.jenis_id.ids)])
        spec = self.env['master.require'].search([('active', '=', True)])
        data = []
        if self.qrf_id.type != '3':
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
        else : 
            action = self.env.ref('master_specifications.dqups3_line_action').read()[0]
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

    def compute_quantity(self):
        for rec in self:
            # if self.qrf_id.type != '3':
            if any(rec.line_qty_ids):
                if len(rec.line_qty_ids) > 1:
                    rec.quantity = sum(rec.line_qty_ids.filtered(lambda x: x.set).mapped('qty'))
                elif len(rec.line_qty_ids) == 1:
                    rec.quantity = sum(rec.line_qty_ids.mapped('qty'))
            else:
                rec.quantity = 0
            # else :
            #     rec.quantity = sum(rec.line_spec_ids.mapped('qty'))

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
    qty = fields.Integer(string='QTY')
    unit = fields.Many2one(string='Unit', related='specifications_id.unit')

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
                            # elif s in ['*', '/', '+', '-', '%']:
                            #     final.append(str(s))
                            # else:
                            #     final.append(str('(1 * 0)'))
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
            if rec.qrf_line_id.qrf_id.type != '3':
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
                                # else:
                                #     final.append(str(s))
                                # elif s in ['*', '/', '+', '-', '%']:
                                #     final.append(str(s))
                                # else:
                                #     final.append(str('(1 * 0)'))
                                else:
                                        final.append(str(s))
                            rec.total = eval(' '.join(final))
                            # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++",final)
                        else:
                            rec.total = rec.subtotal
                else:
                    rec.total = rec.subtotal
            else :
                rec.total = rec.qty * rec.subtotal 

    # @api.onchange('qrf_line_id.line_qty_ids.qty')
    # def onchange_qty(self):
    #     if self.jenis_id.id == 1:
    #         spec = self.qrf_line_id.line_qty_ids.filtered(lambda x: x.qty_id.id == 3)
    #         for t in spec:
    #             if t.qty == 1:
    #                 self.specifications_id == 527
    #             elif t.qty >= 1:
    #                 self.specifications_id == 528

    @api.onchange('unit')
    def onchange_qty(self):
        for rec in self:
            if rec.unit.id == 73:
                rec.qty = rec.qrf_line_id.line_qty_ids.qty
            else :
                rec.qty = 0

class QuotationRequestFormLineQuantity(models.Model):
    _name = 'quotation.request.form.line.quantity'
    _order = "urutan asc"

    qrf_line_id = fields.Many2one('quotation.request.form.line', string='QRF')
    jenis_id    = fields.Many2one('master.jenis', string='Jenis', related='qrf_line_id.jenis_id')
    qty_id      = fields.Many2one('master.qty', string='Quantity')
    urutan      = fields.Integer(string='Urutan', related='qty_id.urutan')
    qty         = fields.Integer(string='Qty')
    set         = fields.Boolean(string='Set ?')

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

class DrawingAttachment(models.Model):
    _name = 'drawing.attachment'

    qrf_id = fields.Many2one('quotation.request.form', string='QRF')
    drawing_attachment_ids = fields.Binary('Drawing', required=True)
    attachment_name = fields.Char('Name')

class QrfAttachment(models.Model):
    _name = 'qrf.attachment'

    qrf_id = fields.Many2one('quotation.request.form', string='QRF')
    qrf_attachment_ids = fields.Binary('QRF', required=True)
    file_name = fields.Char('Name')
    reference = fields.Selection([("standard","Standard"),("sample","Sample/Drawing"),("custom","Custom")])
    notes = fields.Text(string='Notes')
    new_product = fields.Selection(
        [("yes", "Yes"), ("no", "No")], string='New Product', default='yes')
    comp_partial = fields.Selection(
        [("complete", "Complete"), ("partial", "Partial")], string='Complete/Partial', default='complete')
    turret = fields.Selection(
        [("yes", "Yes"), ("no", "No")], string='Reference Turret <= 5 years?', default='yes')
    tooling = fields.Selection(
        [("eu_tsm", "EU / TSM"), ("other", "Other")], string='Tooling Type', default='eu_tsm')
    tooling_qc = fields.Selection(
        [("altinex", "Altinex"), ("other", "Other")], string='Current Tools producing qc-pass tablets', default='altinex')
    con_ids = fields.One2many('qrf.attachment.conclusion', 'qrf_attachment_id', 'Detail')
    download_inform_consent_ids = fields.Binary('Download Inform Consent')
    prev_wo_no = fields.Char(string='Previos WO No.')
    upload_inform_consent_ids = fields.Binary('Upload Inform Consent')
    con_id = fields.Many2one('conclusion', string='Conclusion',)
    # con1_id = fields.Many2one('conclusion', string='Conclusion 1',)
    # con2_id = fields.Many2one('conclusion', string='Conclusion 2',)
    # con3_id = fields.Many2one('conclusion', string='Conclusion 3',)
    # con4_id = fields.Many2one('conclusion', string='Conclusion 4',)
    # con5_id = fields.Many2one('conclusion', string='Conclusion 5',)

    def create_qrf_attch_conclusion(self):
        self.ensure_one()
        temp_con = self.env['qrf.template.con'].search([
            ('new_product', '=', self.new_product),
            ('comp_partial', '=', self.comp_partial),
            ('turret', '=', self.turret),
            ('tooling', '=', self.tooling),
            ('tooling_qc', '=', self.tooling_qc)
        ]) 
        data = []
        if not any(self.con_ids):
            for line in temp_con:
                data.append((0, 0, {
                    "con_id": line.con_id.id
                }))
                    # 'con_id': [(6, 0, line.con_ids.con_id.ids)]
            self.con_ids = data 


        
        # data = []
        # for line in temp_con:
        #     qrf_attc_id = self.env['qrf.attachment'].write({
        #     if not any(self.con_ids):
        #     for line in temp_con:
        #         data.append((0, 0, {
        #             "con1_id": line.con1_id.id,
        #             "con2_id": line.con2_id.id,
        #             "con3_id": line.con3_id.id,
        #             "con4_id": line.con4_id.id,
        #             "con5_id": line.con5_id.id
        #         }))
        #             'con_id': [(6, 0, line.con_ids.con_id.ids)]
        #     })
        #     return data
        # self.con_ids = data 
        

        action = self.env.ref('master_specifications.qrf_att_con_action').read()[0]
        action['res_id'] = self.id
        return action

class QrfAttachmentConclusion(models.Model):
    _name = 'qrf.attachment.conclusion'

    qrf_attachment_id = fields.Many2one('qrf.attachment', string='QRF Attch')
    urutan = fields.Integer(string='Urutan')
    con_id = fields.Many2one('conclusion', string='Conclusion',)
    # con1_id = fields.Many2one('conclusion', string='Conclusion 1',)
    # con2_id = fields.Many2one('conclusion', string='Conclusion 2',)
    # con3_id = fields.Many2one('conclusion', string='Conclusion 3',)
    # con4_id = fields.Many2one('conclusion', string='Conclusion 4',)
    # con5_id = fields.Many2one('conclusion', string='Conclusion 5',)
    check = fields.Boolean(string='Check ?', default=False)
    state = fields.Selection(
        [("draft", "Draft"), ("confirm", "Approval Requested")], string='State', default='draft')

    


class PoAttachment(models.Model):
    _name = 'po.attachment'

    qrf_id = fields.Many2one('quotation.request.form', string='QRF')
    po_attachment_ids = fields.Binary('PO', required=True)
    attachment_name = fields.Char('Name')