from email.policy import default
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
_log = logging.getLogger(__name__)
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_type            = fields.Selection([("jual","Jual"),("makloon","Makloon"), ("stock", "Stock")], string='Sale type',default="jual")
    total_mrp_production = fields.Integer(string='Manufacturing orders', compute="_compute_total_mrp_production")
    design_id            = fields.Many2one('master.design', string='Design Code')
    choose_color         = fields.Char(string='Choose Color')
    color_ids            = fields.Many2many('master.design.line', 'sale_order_color_rel',string='Color',copy=True)
    hanger_code          = fields.Many2one('test.development', String='Hanger Code',store=True,domain=[('state','=','done')])
    kontruksi            = fields.Char(string='Kontruksi' ,related='hanger_code.konstruksi_greige')
    gramasi              = fields.Float(string='Gramasi' ,related='hanger_code.gramasi_greige')
    lebar                = fields.Float(string='Lebar' ,related='hanger_code.lebar_greige')
    density              = fields.Float(string='Density' ,related='hanger_code.density')
    handling             = fields.Selection(string='Handling',related='hanger_code.handling')
    handling_id          = fields.Many2one('master.handling', string='Master Handling', related='hanger_code.handling_id')
    grade_id             = fields.Many2one('makloon.grade', string='Grade' ,default=1)
    greige_id            = fields.Many2one('product.template', string='Greige',required=True,domain=[('categ_id.name', '=', 'GREY')])
    product_id           = fields.Many2one('product.template', string='Product',required=True,domain=[('categ_id.name', '=', 'KAIN')])
    product_code         = fields.Char(string='Product Code', related='product_id.default_code')
    amount_qty           = fields.Float(compute='_compute_quantity', string='Quantity', store=True,)
    harga                = fields.Float(string='Harga')
    nama_dagang_id       = fields.Many2one('nama.dagang', string='Nama Dagang')
    handfeel             = fields.Selection([("soft","Soft"),("medium","Medium"),("hard","Hard")], string='Handfeel')
    employee_id          = fields.Many2one('hr.employee', string='Sales Person')
    
    @api.onchange('harga')
    def get_harga(self):
        for line in self.order_line:
            line.price_unit = self.harga
   
    
    @api.depends('order_line')
    def _compute_quantity(self):
        for order in self:
            amount_qty = sum(order.order_line.mapped('product_uom_qty'))
            order.amount_qty = amount_qty

    # Start Field custom from pro aplikasi
    # design = fields.Char(string='Design')
    motif = fields.Char(string='Motif')
    kategori = fields.Char(string='Kategori')
    pembayaran = fields.Char(string='Pembayaran')
    status = fields.Char(string='Status')
    pita = fields.Char(string='Pita')
    grade = fields.Char(string='Grade / Sablon')
    # gramasi = fields.Float(string='Gramasi / Sablon')
    lebar_finish = fields.Float(string='Price Total')
    merk = fields.Char(string='Merk')
    quality = fields.Char(string='Quality')
    keterangan = fields.Text(string='Keterangan')
    export_or_local = fields.Selection([("export","Export"),("local","Local")], string='Export / Local')
    uk = fields.Char(string='Uk')
    lf = fields.Char(string='Lf')
    # End Field custom from pro aplikasi
    
    def _default_delivery_date(self):
        return fields.Date.context_today(self)

    wo_date                 = fields.Date('WO Date', default=_default_delivery_date)
    delivery_date           = fields.Date(string='Delivery Date',)
    delivery                = fields.Datetime("Delivery")
    customer_code           = fields.Char('Customer Code',related="partner_id.ref",store=True)
    category_id             = fields.Char("Category")
    wo_no                   = fields.Char('Work Order No')
    m_j                     = fields.Char('M/J')
    w_k                     = fields.Char('W/K')
    batch_no                = fields.Char('BATCH NO.') #update dari KP
    fabric_code             = fields.Char(string='Fabric Code')
    request_width           = fields.Char('Req. Width')
    fabric_type             = fields.Char("Jenis kain")
    motif                   = fields.Char('Motif')
    construction            = fields.Char('Konstruksi')
    req_gramation           = fields.Char('Req Gramasi')
    no_wo                   = fields.Char('Nomor WO')
    no_po                   = fields.Char(string='No PO')
    # greige_code             = fields.Char(string='Greige Code', related="hanger_code.greige_code")
    fabric_base             = fields.Char('Fabric Base')
    wo_note                 = fields.Char('Note')
    lebar_finish            = fields.Float(string='Lebar Finish')
    gramasi_finish          = fields.Float(string='Gramasi Finish',)
    max_joint_pieces        = fields.Char('Max Join Pieces',)
    notulen                 = fields.Char(string='Notulen',)
    order_pertama           = fields.Char(string='Order Pertama', compute="_compute_order_pertama")
    color_code              = fields.Char(string='Color Code')
    status_so               = fields.Char(string='Status SO')
    qty_pesanan             = fields.Float(string='Qty')
    toleransi_grade_b       = fields.Float(string='Toleransi Grade B',)
    total_product_uom_qty   = fields.Float(compute='_compute_total', string='Total', store=False)
    qty_available           = fields.Float(string='Qty Available', compute="_compute_qty_available")
    qty_reserve             = fields.Float(string='Qty Reserve', compute="_compute_qty_available")
    req_width               = fields.Float('Req Lebar')
    piece_length            = fields.Integer('Piece Length', )
    hanger_variasi          = fields.Many2one('tj.stock.variasi')
    strike_off_id           = fields.Many2one('strikeoff', string='Strike Off')
    # product_id              = fields.Many2one('product.product', string='Product', store=True)
    sj_greige               = fields.Many2one('stock.picking', String='SJ Greige')
    labdip_id               = fields.Many2one('labdip', String='Labdip No')
    process_id              = fields.Many2one('sale.contract.process', string='Process',)
    packing                 = fields.Many2one('sale.contract.packing',string='Packing',)
    accessories_id          = fields.Many2one('accessories',string='Accessories',)
    hang_tag_id             = fields.Many2one('hang.tag',string='Hang Tag',)
    color_id                = fields.Many2one('labdip.warna', string='Color')
    uom_pesanan_id          = fields.Many2one('uom.uom', string='Uom')
    # design_id               = fields.Many2one('makloon.design', string="Design")
    sc_id                   = fields.Many2one('sale.contract', string='Sale Contract')
    piece_length_uom        = fields.Many2one('uom.uom',string='Piece Length Uom', default=3, domain="[('id', 'in', [106,77,3])]")
    uom_id                  = fields.Many2one('uom.uom', string='Uom')
    contract_id             = fields.Many2one('sale.contract', string='Sale Contract', copy=False)
    pricelist_id            = fields.Many2one('product.pricelist', string='Pricelist')
    template_id             = fields.Many2one('sale.quote.template', 'Quotation Template')
    kategori_sale_order_id  = fields.Many2one('kategori.sale.order', string='Kategori Sale Order')
    is_work_order           = fields.Boolean(string='Is Work Order')
    is_available_stock      = fields.Boolean(default=True)
    is_after_check          = fields.Boolean(default=False)
    is_notulen              = fields.Boolean(string='Is Notulen', default=False)
    is_repeat_order         = fields.Boolean("Repeat Order?")
    approved_rnd            = fields.Boolean(string='Approved Rnd',default=False)
    is_woven                = fields.Boolean('Woven?')
    is_selesai              = fields.Boolean(string='Is Selesai', default=False)
    note                    = fields.Text(string='Note')
    production              = fields.Selection([('printing', 'Printing'), ('dyeing', 'Dyeing')])
    priority                = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], string='Priority')
    states_greige           = fields.Selection([("ada","Ada"),("approve","Approve")], string='Status Order', readonly=True, compute="_compute_states_greige_")
    kategori_so             = fields.Selection([("kain","Kain"),("none_kain","Non Kain")], string='Kategori SO')
    sales_type              = fields.Selection(selection=[('makloon','Makloon'),('jual','Jual')], string='Sale Type',)
    type_sc_category        = fields.Selection(selection=[('dyeing', 'Work Order Dyeing'),('printing', 'Work Order Printing'),],string='Type',related="type")
    state                   = fields.Selection(selection_add=[("draft_wo", "Draft"),("confirm_wo","Confirm")])
    type_wo                 = fields.Selection([("stock","Re Stock"),("order","Fresh Order")], string='Type Wo', )
    potongan_pinggir        = fields.Selection(selection=[('yes', 'Yes'),('no', 'No'),],string='Potongan Pinggir',)
    type = fields.Selection(
        selection=[
            ('dyeing', 'Work Order Dyeing'),
            ('printing', 'Work Order Printing'),
            ],
        string='Type', default='dyeing', change_default=True,)
    check_states = fields.Selection([("no_mlot","No Mlot"),("isi_notulen","isi Notulen"),("approve_rnd","Approve Rnd"),
                                    ("approve_rnd","Approve Rnd"),("approve","Approve"),("ada","Ada"),
                                    ("approve","Approve"),("ada_mlot","Ada Mlot"),("mlot_draft","Mlot Draft"),("mlot_approve","Mlot Approve"),("done","done")], string='Status Order', readonly=True, copy=False)
    qty_unit = fields.Float(string='Qty / Product')
    is_force_price = fields.Boolean(string='is Force Price ?', default=False)

    # @api.onchange('sc_id')
    # def get_partner_from_sc(self):
    #     self.partner_id = self.sc_id.partner_id
        
    
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self.order_line:
            history = self.env['sale.product.history'].search([('product_id','=',order.product_id.id),('partner_id','=',order.order_id.partner_id.id)])
            if len(history) == 1:
                history.write({"line_ids":[(0,0,{"sale_id":order.order_id.id ,"so_date":order.order_id.date_order.date(),"sale_price":order.price_unit})]})
            else:
                order.product_id.write({
                    "sale_history_ids":[(0,0,{"product_id":order.product_id.id,"partner_id":order.order_id.partner_id.id ,"line_ids":[(0,0,{"sale_id":order.order_id.id ,"so_date":order.order_id.date_order.date(),"sale_price":order.price_unit})]})]
                })
            
        return res
    
    
    def _update_sale_price_history(self):
        _log.warning('='*40)
        _log.warning('on _update_sale_price_history')
        _log.warning('='*40)

    
    
    def create_variant(self):
        color_attr = self.env['product.template.attribute.line'].sudo().search([('product_tmpl_id','=',self.product_id.id),('attribute_id.name','=','WARNA')],limit=1)
        if color_attr:
            for line in self.color_ids:
                color_attr.sudo().write({
                    "value_ids":[(4,line.color_id.id)],
                })
        else:
            color_attr.sudo().create({
                'product_tmpl_id': self.product_id.id,
                'attribute_id': 24, #attribute warna 
                'value_ids': [(6, 0, [line.color_id.id for line in self.color_ids])]
            })
            
            # comment attribute kode design tidak di masukan di product template attribute value ids
            # design_attr = self.env['product.attribute.value'].sudo().search([('name','=',self.design_id.name)],limit=1)
            # if not design_attr:
            #     design_attr = design_attr.sudo().create({
            #         "attribute_id":31,
            #         "name":self.design_id.name,
            #     })
            # color_attr.sudo().create({
            #     'product_tmpl_id': self.product_id.id,
            #     'attribute_id': 31, #attribute kode design 
            #     'value_ids': [(6, 0, [design_attr.id])]
            # })
        
        product_ids = self.env['product.product'].sudo().search([('product_tmpl_id','=',self.product_id.id)])
        if self.order_line:
            product_ids = product_ids.filtered(lambda x:x.id not in [ product.id for  product in self.order_line.mapped('product_id')])
        color_filtered = self.color_ids.mapped('color_id')
        value_ids = [color.id for color in color_filtered]
        # value_ids.append(self.design_id.id)
        for variant in product_ids.filtered(lambda x: x.product_template_attribute_value_ids.filtered(lambda x:x.product_attribute_value_id.id in value_ids)):
            history = self.env['sale.product.history'].search([('product_id','=',variant.id),('partner_id','=',self.partner_id.id)],limit=1)
                
                
            
            for value in (variant.product_template_attribute_value_ids.filtered(lambda x:x.product_attribute_value_id.id in value_ids)):
                if not self.is_force_price:
                    self.check_pricelist(variant.id, history.last_price if history else self.harga, self.qty_unit) #check pricelist

                [color.sudo().write({"variant_id":variant.id}) for color in self.design_id.line_ids.filtered(lambda x:x.color_id.id == value.product_attribute_value_id.id)]
                variant.sudo().write({
                    "design_id":self.design_id.id
                })
                self.order_line = [(0,0,{"product_id":variant.id,"price_unit": history.last_price if history else self.harga ,"product_uom":variant.uom_id.id,"name":variant.name, 'product_uom_qty': self.qty_unit})]
    
    def _compute_total_mrp_production(self):
        self.ensure_one()
        mrp_production_obj = self.env['mrp.production'].search([('sale_id', '=', self.id)])
        self.total_mrp_production = len(mrp_production_obj)

    def action_open_mrp_production(self):
        self.ensure_one()
        mrp_production_ids = self.env['mrp.production'].search([('sale_id', '=', self.id)]).ids
        action = {
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
        }
        if len(mrp_production_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': mrp_production_ids[0],
            })
        else:
            action.update({
                'name': _("Manufacturing Orders Generated by %s", self.name),
                'domain': [('id', 'in', mrp_production_ids)],
                'view_mode': 'tree,form',
            })
        return action

    def check_pricelist(self, variant, price, qty):
        pricelist = self.pricelist_id
        if pricelist.id:
            for item in pricelist.item_ids.filtered(lambda x: x.product_id.id == variant and x.min_quantity <= qty and x.min_quantity >= qty):
                if price < item.fixed_price:
                    raise ValidationError("Mohon maaf anda tidak dapat memasukan harga dibawah standar")
    
    def force_price(self):
        self.is_force_price = True

    @api.onchange('contract_id')
    def onchange_contract_id_change_warehouse(self):
        self.warehouse_id = 3 # Change warehouse To GD Jadi
        self.payment_term_id = self.contract_id.term_of_payment.id

    @api.model
    def name_get(self):
        result = []
        ctx = self.env.context
        for sale in self:
            if ctx.get('with_reff', False) and sale.keterangan:
                result.append((sale.id, str(sale.name) + ' - ' + str(sale.keterangan)))
            else:
                result.append((sale.id, str(sale.name)))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        ctx = self.env.context
        if ctx.get('with_reff', False):
            res_search = False
            res = self.search([ '|',('name',operator,name),('keterangan',operator,name)] + args, limit=limit)
            res_search = res.name_get()
            return res_search