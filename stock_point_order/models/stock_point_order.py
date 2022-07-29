from odoo import models, fields, api, _
from odoo.exceptions import UserError
from ast import literal_eval
import logging;
_logger = logging.getLogger(__name__)


class StockPointOrder(models.Model):
    _name = 'stock.point.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    

    name               = fields.Char(string='Order', default=_('New'),copy=False)
    company_id         = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    jalur_id           = fields.Many2one('res.partner.jalur', string='Jalur',required=True, )
    salesperson_id     = fields.Many2one( string='Supervisor',related="jalur_id.salesperson_id" )
    product_id         = fields.Many2one(related='line_ids.product_id', string='Product')
    # picking_type_id    = fields.Many2one('stock.picking.type', string='Operation Type',required=True, domain=[('is_stock_point','=',True),('code', '=', 'internal')])
    warehouse_id       = fields.Many2one('stock.warehouse', string='Stock Point',required=True,domain=[('is_stock_point', '=', True)])
    lead_days          = fields.Integer(string='Lead',related="warehouse_id.lead_days")
    location_id        = fields.Many2one('stock.location', string='Location',related="warehouse_id.lot_stock_id")
    user_id            = fields.Many2one('res.users', string='User',default=lambda self: self.env.user.id,readonly=True)
    date               = fields.Date(string='TGL Pesan', default=fields.Date.today())
    confirm_date       = fields.Date(string='Confirm Date', default=fields.Date.today())
    date_order         = fields.Datetime(string='TGL DO HO', default=fields.Datetime.now(),required=True, )
    date_rutesale      = fields.Datetime(string='TGL Rute Sale', default=fields.Datetime.now(),)
    pricelist_id       = fields.Many2one('product.pricelist', string='Pricelist',required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1, help="If you change the pricelist, only newly added lines will be affected.")
    currency_id        = fields.Many2one(related='pricelist_id.currency_id', depends=["pricelist_id"], store=True)
    note               = fields.Text(string='Note')
    state              = fields.Selection([('draft', 'Draft'),('confirm', 'Confirm'),('done', 'Done'),('cancel', 'Cancelled'),], string='Status', readonly=True,  index=True, tracking=3, default='draft')
    line_ids           = fields.One2many('stock.point.order.line', 'order_id', string='Details',copy=True)
    picking_ids        = fields.Many2many('stock.picking', relation='stock_point_order_transfer_rel',string='Transfer')
    amount_untaxed     = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', tracking=5)
    amount_tax         = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total       = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', tracking=4)  
    amount_quantity    = fields.Float(string='Total Quantity', store=True, readonly=True, compute='_amount_all', tracking=4)
    

    @api.depends('line_ids.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = amount_quantity = 0.0
            for line in order.line_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_quantity += line.quantity
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_quantity': amount_quantity,
                'amount_total': amount_untaxed + amount_tax,
            })
    
    def action_confirm(self):
        if self.name == 'New':
            seq = self.env['ir.sequence'].next_by_code('stock.point.order.sequence')
            self.name = seq
        self.state = 'confirm'
        self.confirm_date = fields.Date.today()
        
        
    def action_done(self):
        self.state = 'done'
        
    def action_draft(self):
        self.state = 'draft'
        
    def action_cancel(self):
        self.state = 'cancel'

class StockPointOrderLine(models.Model):
    _name = 'stock.point.order.line'
    
    order_id        = fields.Many2one('stock.point.order', string='Order')
    product_id      = fields.Many2one('product.product', string='Product',domain=lambda self:self._get_domain())
    lead_days       = fields.Integer(string='Lead Product',related="product_id.lead_days")
    name            = fields.Char(string='Stock Point Order Line',related='product_id.name')
    warehouse_id    = fields.Many2one(related='order_id.warehouse_id', string='Warehouse',store=True,)
    jalur_id        = fields.Many2one(related='order_id.jalur_id', string='Jalur',store=True,)
    price_unit      = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    date_production = fields.Date(string='Tgl Produksi',compute="_get_tgl_produksi",store=True,)
    default_code    = fields.Char(string='Code',related="product_id.default_code")
    price           = fields.Float('Price', required=True, related='price_unit', default=0.0, readonly=True)
    price_subtotal  = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax       = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total     = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    currency_id     = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True, string='Currency', readonly=True)
    price_reduce    = fields.Float(compute='_get_price_reduce', string='Price Reduce', digits='Product Price', readonly=True, store=True)
    quantity        = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True,default=1.0)
    discount        = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    tax_id          = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    product_uom_id  = fields.Many2one(related='product_id.uom_id', string='Satuan')
    # state           = fields.Selection(related="order_id.state",string='Status',store=True,)
    state = fields.Selection(
        compute="_compute_order_state",
        string="Status",
        selection=lambda self: self.env["stock.point.order"]._fields["state"].selection,
        store=True,
    )
    
    
    @api.depends('order_id.date_order')
    def _get_tgl_produksi(self):
        for line in self:
            lead_produce = line.lead_days or 0
            lead_delivery = line.order_id.lead_days or 0
            leads = lead_produce + lead_delivery
            if line.order_id.date_order:
                line.date_production = fields.Date.subtract(line.order_id.date_order,days=leads)
            else:
                line.date_production = False
            

    @api.depends('order_id.state')
    def _compute_order_state(self):
        for line in self:
            line.state = line.order_id.state
        
    
    @api.depends('quantity', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the Stock point order line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.quantity, product=line.product_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])
    
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        if self.product_id.taxes_id and not self.tax_id:
            self.tax_id = [(4,self.product_id.taxes_id.id)]
            
            
    @api.depends('price_unit', 'discount')
    def _get_price_reduce(self):
        for line in self:
            line.price_reduce = line.price_unit * (1.0 - line.discount / 100.0)

    
    @api.onchange('product_uom_id','quantity')
    def product_qty_change(self):
        if not self.product_uom_id or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id:
            product = self.product_id.with_context(
                # lang=self.order_id.partner_id.lang,
                # partner=self.order_id.partner_id,
                quantity=self.quantity,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom_id.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.order_id.company_id)

    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        # awa: don't know if it's still the case since we need the "product_no_variant_attribute_value_ids" field now
        # to be able to compute the full price

        # it is possible that a no_variant attribute is still in a variant if
        # the type of the attribute has been changed after creation.

        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.order_id.pricelist_id.id, uom=self.product_uom_id.id).price
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom.id)

        final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(product or self.product_id, self.quantity or 1.0)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.quantity, self.product_uom, self.order_id.pricelist_id.id)
        if currency != self.order_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.order_id.pricelist_id.currency_id,
                self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)
    
    def _get_domain(self):
        domain = []
        ir_config             = self.env['ir.config_parameter'].sudo()
        filter_product        = ir_config.get_param('filter_product')
        product_category_ids  = ir_config.get_param('product_category_ids')
        if filter_product and product_category_ids:
            domain += [('categ_id','in', literal_eval(product_category_ids))]
        return domain
            
            


