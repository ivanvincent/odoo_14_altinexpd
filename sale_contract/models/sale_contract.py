# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import psycopg2
from functools import partial
from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError, UserError, Warning
import odoo.addons.decimal_precision as dp
from odoo.tools import float_is_zero
import requests
import urllib
import base64
from werkzeug import FileStorage
from io import BytesIO
import os

_logger = logging.getLogger(__name__)


class SaleContractCategory(models.Model):
    _name = 'sale.contract.category'
    
    name = fields.Char(string='Name', copy=False)
    code = fields.Char(string='Code', copy=False)
    sequence_id = fields.Many2one('ir.sequence', 'Reference Sequence')


class SaleContract(models.Model):
    _name = 'sale.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    @api.model
    def _amount_line_tax(self, line, fiscal_position_id):
        taxes = line.tax_ids.filtered(lambda t: t.company_id.id == line.order_id.company_id.id)
        if fiscal_position_id:
            taxes = fiscal_position_id.map_tax(taxes, line.product_id, line.order_id.partner_id)
        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        taxes = taxes.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id,
                                  partner=line.order_id.partner_id or False)['taxes']
        return sum(tax.get('amount', 0.0) for tax in taxes)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.term_of_payment = self.partner_id.property_payment_term_id.id
            self.kode_mkt = self.partner_id.kode_mkt
    #         pricelist = self.env['product.pricelist'].search([('partner_id', '=', self.partner_id.id)])

    #         if len(pricelist) == 0:
    #             raise UserError(_('Customer Belum Punya Pricelist (Data Pricelist salah Customer) !'))
    #         else:
    #             if len(pricelist) == 1:
    #                 self.pricelist_id = pricelist.id
    #             else:
    #                 # jika pricelist lebih dari satu maka di ambil yg paling atas
    #                 self.pricelist_id = pricelist[0].id

    @api.depends('lines.price_subtotal_incl', 'lines.discount', 'discount', 'lines.qty', 'lines.qty_do')
    def _compute_amount_all(self):
        for order in self:
            amount = amount_inc = discount = 0.0
            qty_total = qty_do =0.0
            total_tax = 0
            total_untax = 0
            # currency = order.pricelist_id.currency_id
            for line in order.lines:
                amount += line.price_subtotal
                total_untax += line.price_subtotal
                amount_inc += line.price_subtotal_incl
                discount += line.discount
                qty_total += line.qty
                qty_do += line.qty_do                
                for t in line.tax_ids:
                    total_tax += line.price_subtotal * (t.amount / 100)
            order.update({
                'amount_untaxed': total_untax,
                'amount_tax': total_tax,
                'discount': discount,
                'amount_total': amount + total_tax,
                'qty_total': qty_total,
                # 'qty_do': qty_do,
                'residue_total':qty_total - qty_do,
            })

            # order.amount_tax = currency.round(sum(self._amount_line_tax(line, order.fiscal_position_id) for line in order.lines))
            # amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
            # order.amount_total = order.amount_tax + amount_untaxed - order.discount
            # order.qty_total = currency.round(sum(line.qty for line in order.lines))
            # order.residue_total = currency.round(sum(line.qty for line in order.lines)) - currency.round(sum(line.qty_do for line in order.lines))

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True,)
    date_order = fields.Date(string='Order Date', index=True, default=fields.Datetime.now)
    name = fields.Char(string='Sales Forcast', copy=False, default='New')
    amount_tax = fields.Monetary(string='Taxes', currency_field='currency_id', compute='_compute_amount_all')
    amount_untaxed = fields.Monetary(string='Amount Untaxed', currency_field='currency_id', compute='_compute_amount_all')
    amount_total = fields.Float(compute='_compute_amount_all', string='Total', digits=0)
    qty_total = fields.Float(compute='_compute_amount_all', string='Qty Total', digits=0)
    residue_total = fields.Float(compute='_compute_amount_all', string='Qty Residue', digits=0)
    lines = fields.One2many('sale.contract.line', 'order_id', string='Order Lines', copy=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist',) 
    # default=_default_pricelist
    partner_code = fields.Char(string='Partner Code', related="partner_id.ref")
    # sales_id = fields.Many2one('hr.employee', required=True, string="MKT", domain=[('is_mkt', '=', True)])
    state = fields.Selection([('draft', 'New'), ('confirmed', 'Confirmed'), ('invoiced', 'Invoiced'), ('cancel', 'Cancelled')], 'Status',  default='draft')
     # readonly=True, copy=False,
    note = fields.Text(string='Internal Notes')
    no_bon                = fields.Char('PO Customer')
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position')    
    user_id = fields.Many2one('res.users', string='Marketing', default=lambda self: self.env.user.id)    
    discount = fields.Float(string='Discount', digits=0, default=0.0)
    sale_order_ids = fields.One2many('sale.order', 'contract_id', string='Sale Order')
    category_id = fields.Many2one('sale.contract.category', string='Category',)
    # sales_type                  = fields.Selection([('makloon','Subcon'),('jual','Jual')],'Sales Type',default='jual')
    qty_order                   = fields.Float('Qty Order',defaults=0.0)
    qty_order_uom               = fields.Many2one('product.uom',string='UoM')
    delivery_date               = fields.Date(string='Delivery Date', index=True, default=fields.Datetime.now)
    payment_type                = fields.Selection([('brutto','Brutto'),('netto','Netto')],'Payment By',default='brutto')
    term_of_payment             = fields.Many2one('account.payment.term', string='Payment Terms', readonly=True)
    # term_of_payment             = fields.Char(string='Term of Payment')
    term_of_payment_information = fields.Char(string='Term of Payment Information')
    partner_id = fields.Many2one('res.partner', string='Customer',)
    set_duplicate_product =  fields.Boolean(string="Allow Duplicate Product", default=False)
    process                     = fields.Many2one('sale.contract.process',string='Process')
    image_binary = fields.Binary(string='Image', compute='_compute_img')
    format_file = fields.Char(string='Format File')
    design_code = fields.Char(string='Design Code') #sementara
    design_code_id = fields.Many2one('makloon.design', string='Design')
    quotation_id = fields.Many2one('quotation', string='Quotation')
    kode_mkt  = fields.Selection([("L","L"),("K","K"),("G","G")],string='Kode MKT')




    @api.constrains('lines','set_duplicate_product')
    def _check_exist_product_in_line(self):
        # if self.set_duplicate_product == False:
        for order in self:
            if order.set_duplicate_product == False:
                exist_product_list = []
                for line in order.lines:
                    if line.product_id.id in exist_product_list:
                        msg = 'Product must be one per line. Please Remove These Product : - (%s).' % (line.product_id.name)
                        raise ValidationError(_(msg))
                    exist_product_list.append(line.product_id.id)

    def action_select_product(self):
        view_id = self.env.ref('sale_contract.sc_all_form_view_select_multi_product_wizard')
        wiz = self._context.get('active_id')
        return {
            'name': _('Select Product'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sales.all.multi.product',
            'target': 'new',
            'views': [(view_id.id, 'form')],
            'view_id': view_id.id,
            # 'res_id': wiz.id,
            'context': self.env.context,
            }


    # def set_pack_operation_lot(self, picking=None):
    #     """Set Serial/Lot number in pack operations to mark the pack operation done."""

    #     StockProductionLot = self.env['stock.production.lot']
    #     PosPackOperationLot = self.env['pos.pack.operation.lot']

    #     for order in self:
    #         for pack_operation in (picking or self.picking_id).pack_operation_ids:
    #             qty = 0
    #             qty_done = 0
    #             pack_lots = []
    #             pos_pack_lots = PosPackOperationLot.search([('order_id', '=', order.id), ('product_id', '=', pack_operation.product_id.id)])

    #             if pos_pack_lots :
    #                 for pos_pack_lot in pos_pack_lots :
    #                     stock_production_lot = StockProductionLot.search([('name', '=', pos_pack_lot.lot_name), ('product_id', '=', pack_operation.product_id.id)])
    #                     if stock_production_lot :
    #                         qty_done += pos_pack_lot.qty
    #                         pack_lots.append({'lot_id': stock_production_lot.id, 'qty': pos_pack_lot.qty})
    #             else:
    #                 qty_done = pack_operation.product_qty
    #             pack_operation.write({'pack_lot_ids': map(lambda x: (0, 0, x), pack_lots), 'qty_done': qty_done})

    def action_confirm(self):
        for me_id in self :
            seq = self.env['ir.sequence'].next_by_code('sale.contract')
            me_id.state = 'confirmed'
            me_id.name = seq


    def action_cancel(self):
        for me_id in self :
            if me_id.state == 'cancel' :
                continue            
            me_id.state = 'cancel'

    def action_set_to_draft(self):
        for me_id in self :
            if me_id.state != 'cancel' :
                continue
            me_id.state = 'draft'

    def is_invoiced(self):
        for contract in self :
            if contract.state == 'invoiced' :
                continue
            if any(line.qty_inv for line in contract.lines):
                contract.state = 'invoiced'

    def _compute_img(self):
        for rec in self:
            url = self.env.ref('sale_contract.url_image_sc').read()[0]['value']
            path_url = "%s%s%s" % (url, rec.id, rec.format_file)
            rec.image_binary = False
            # rec.image_binary = self.load_image_from_url(path_url)
    
    def load_image_from_url(self, url):
        localhost = self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')]).value
        data = False
        if self.exists(url):
            data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
        else:
            data = base64.b64encode(requests.get(localhost+'/web/static/src/img/placeholder.png'.strip()).content).replace(b'\n', b'')
        return data

    def exists(self, url):  
        return requests.head(url).status_code < 400

    @api.model
    def create(self, values):
        path   = self.env.ref('sale_contract.path_image_sc').read()[0]['value']
        result = super(SaleContract, self).create(values)
        if values.get('image_binary', False):
            file_name    = result.id
            binary       = values['image_binary']
            file_data    = BytesIO(base64.b64decode(binary))
            content_type = 'image/png' if binary[0] == 'i' else 'image/jpeg'
            file         = FileStorage(file_data, filename=file_name, content_type=content_type)
            format_file  = '.png' if content_type == 'image/png' else '.jpeg'
            file.save(os.path.join(path, str(file_name) + format_file))
            self.browse(file_name).write({'format_file' : format_file})
        return result

    def write(self, values):
        if values.get('image_binary', False):
            path   = self.env.ref('sale_contract.path_image_sc').read()[0]['value']
            file_name    = self.id
            binary       = values['image_binary']
            file_data    = BytesIO(base64.b64decode(binary))
            content_type = 'image/png' if binary[0] == 'i' else 'image/jpeg'
            file         = FileStorage(file_data, filename=file_name, content_type=content_type)
            format_file  = '.png' if content_type == 'image/png' else '.jpeg'
            file.save(os.path.join(path, str(file_name) + format_file))
        return super(SaleContract, self).write(values)
    

    def unlink(self):
        path   = self.env.ref('sale_contract.path_image_sc').read()[0]['value']
        for rec in self:
            file = "%s%s%s" % (path, rec.id, rec.format_file)
            os.remove(file)
        return super(SaleContract, self).unlink()

    @api.onchange('quotation_id')
    def _onchange_quotation(self):
        quotation = self.quotation_id
        self.lines = False
        if self.quotation_id:
            self.partner_id = quotation.partner_id.id
            self.design_code_id = quotation.design_code_id.id
            self.term_of_payment = quotation.payment_term_id.id
            self.lines = [(0, 0, {
                'product_id': q.product_id.id,
                'embos'     : q.embos,
                'tip'       : q.tip,
                'size'      : q.size,
                'qty'       : q.quantity,
                'price_unit': q.price_unit,
                'tax_ids'   : [(6, 0, q.tax_ids.ids)]
            }) for q in quotation.line_ids]
            


class SaleContractLine(models.Model):
    _name = "sale.contract.line"
    _description = "Lines of Contract"
    _rec_name = "product_id"

    # def _order_line_fields(self, line):
    #     if line and 'tax_ids' not in line[2]:
    #         product = self.env['product.product'].browse(line[2]['product_id'])
    #         line[2]['tax_ids'] = [(6, 0, [x.id for x in product.taxes_id])]
    #     return line

    # @api.depends('so_line_ids')
    # def _get_qty(self):
    #     for line in self :
    #         qty_so = 0
    #         qty_do = 0
    #         qty_inv = 0

    #         for so_line in line.so_line_ids :
    #             qty_so += so_line.product_uom_qty
    #             qty_inv += so_line.qty_invoiced
    #             qty_do += so_line.qty_delivered

    #         line.qty_so = qty_so
    #         line.qty_do = qty_do
    #         line.qty_inv = qty_inv


    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    name = fields.Char(string='Forcast Line')
    notice = fields.Char(string='Discount Notice')
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True)
    default_code = fields.Char(related='product_id.default_code', string='Item Code',)
    part_no = fields.Char(string='Part Number',)
    item_no = fields.Char(string='Item Number',)
    price_unit = fields.Float(string='Unit Price', digits=0)
    qty = fields.Float('Quantity', default=1)
    qty_so = fields.Float('Sale Order', compute='_get_qty')
    qty_do = fields.Float('Delivery', compute='_get_qty')
    qty_toinv = fields.Float('To Invoice', compute='_get_qty')
    qty_inv = fields.Float('Invoice', compute='_get_qty')
    price_subtotal = fields.Float(compute='_compute_amount_line_all', digits=0, string='Subtotal')
    price_subtotal_incl = fields.Float(compute='_compute_amount_line_all', digits=0, string='Subtotal Inc')
    discount = fields.Float(string='Discount (%)', digits=0, default=0.0)
    order_id = fields.Many2one('sale.contract', string='Order Ref', ondelete='cascade')
    create_date = fields.Datetime(string='Creation Date', readonly=True)
    # tax_ids = fields.Many2many('account.tax', string='Taxes',)
    tax_ids = fields.Many2many('account.tax', string='Taxes',)
    # tax_ids_after_fiscal_position = fields.Many2many('account.tax',string='Taxes')
    so_line_ids = fields.One2many('sale.order.line', 'contract_line_id', string='Sale Order Line')
    embos = fields.Char(string='Embos')
    tip = fields.Char(string='Tip')
    product_ingredient_id = fields.Many2one('product.product', string='Material')
    size = fields.Char(string='Size')
    department_id = fields.Many2one('hr.department', string='Dept')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')
    image_binary = fields.Binary(string='Image', store=False, compute='_compute_img')
    treatment_id = fields.Many2one('treatment', string='Heat Treatment')
    # pack_lot_ids = fields.One2many('pos.pack.operation.lot', 'pos_order_line_id', string='Lot/serial Number')
    # warna = fields.Char(string='Warna')
    # barcode = fields.Char(string='Barcode')
    #barcode = fields.Many2one('makloon.barcode.line', string='Barcode')
    #, ondelete='cascade'
    # rol = fields.Float(string='Rol (Items)') #, digits=dp.get_precision('Product Unit of Measure')
    # eceran = fields.Float(string='Eceran (Items)') #, digits=dp.get_precision('Product Unit of Measure')

    @api.depends('so_line_ids')
    def _get_qty(self):
        for rec in self:
            rec.qty_so =sum(line.product_uom_qty for line in rec.so_line_ids)
            rec.qty_do =sum(line.qty_delivered for line in rec.so_line_ids)
            rec.qty_toinv =sum(line.qty_to_invoice for line in rec.so_line_ids)
            rec.qty_inv =sum(line.qty_invoiced for line in rec.so_line_ids)

    @api.depends('price_unit', 'tax_ids', 'qty', 'discount', 'product_id')
    def _compute_amount_line_all(self):
        for line in self:
            currency = line.order_id.pricelist_id.currency_id
            taxes = line.tax_ids.filtered(lambda tax: tax.company_id.id == line.order_id.company_id.id)
            fiscal_position_id = line.order_id.fiscal_position_id
            if fiscal_position_id:
                taxes = fiscal_position_id.map_tax(taxes, line.product_id, line.order_id.partner_id)
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            line.price_subtotal = line.price_subtotal_incl = price * line.qty
            if taxes:
                taxes = taxes.compute_all(price, currency, line.qty, product=line.product_id,
                                          partner=line.order_id.partner_id or False)
                line.price_subtotal = taxes['total_excluded']
                line.price_subtotal_incl = taxes['total_included']

            # line.price_subtotal = currency.round(line.price_subtotal)
            # line.price_subtotal_incl = currency.round(line.price_subtotal_incl)

    # @api.onchange('product_id')
    # def _onchange_product_id(self):
    #     if self.product_id:
    #         if not self.order_id.pricelist_id:
    #             raise UserError(
    #                 _('You have to select a pricelist in the sale form !\n'
    #                   'Please set one before choosing a product.'))
    #         price = self.order_id.pricelist_id.get_product_price(
    #             self.product_id, self.qty or 1.0, self.order_id.partner_id)
    #         self._onchange_qty()
    #         self.price_unit = price
    #         # self.tax_ids = self.product_id.taxes_id

    @api.onchange('qty', 'discount', 'price_unit', 'tax_ids')
    def _onchange_qty(self):
        if self.product_id:
            # if not self.order_id.pricelist_id:
            #     raise UserError(_('You have to select a pricelist in the sale form !'))
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            self.price_subtotal = self.price_subtotal_incl = price * self.qty
            if self.product_id.taxes_id:
                taxes = self.product_id.taxes_id.compute_all(price, self.order_id.pricelist_id.currency_id, self.qty,
                                                             product=self.product_id, partner=False)
                self.price_subtotal = taxes['total_excluded']
                self.price_subtotal_incl = taxes['total_included']

    def action_view_so(self):            
        action = self.env.ref('sale_contract.angkring_sale_order_line_action').read()[0]
        orders = self.mapped('so_line_ids')
        if orders:
            action['domain'] = [('id', 'in', orders.ids)]
        # elif orders:
        #     action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        #     action['res_id'] = orders.order_id
        return action

    def action_view_do(self):            
        action = self.env.ref('stock.stock_move_action').read()[0]    
        orders = self.mapped('so_line_ids')
        moves = self.env['stock.move'].search([('sale_line_id', 'in', orders.ids)])
        if orders:
            action['domain'] = [('id', 'in', moves.ids)]
        return action

    def action_view_inv(self):
        for order in self:
            inv_lines = order.so_line_ids.invoice_lines.move_id.filtered(lambda r: r.type in ('out_invoice', 'out_refund'))
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if inv_lines:
            action['domain'] = [('id', 'in', inv_lines.ids)]
        return action


    # Start Function ALl About Image
    # def _compute_img(self):
    #     print('====================_compute_img========================')
    #     for rec in self:
    #         url = self.env.ref('sale_contract.url_image_sc').read()[0]['value']
    #         path_url = "%s%s" % (url, rec.filename)
    #         rec.image_binary = self.load_image_from_url(path_url)
    
    # def load_image_from_url(self, url):
    #     localhost = self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')]).value
    #     data = False
    #     if self.exists(url):
    #         data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
    #     else:
    #         data = base64.b64encode(requests.get(localhost+'/web/static/src/img/placeholder.png'.strip()).content).replace(b'\n', b'')
    #     return data

    # def exists(self, url):  
    #     a=urllib.request.urlopen(url)
    #     return a.getcode() == 200

    # @api.model
    # def create(self, values):
    #     path   = self.env.ref('sale_contract.path_image_sc').read()[0]['value']
    #     result = super(SaleContractLine, self).create(values)
    #     file_name    = result.id
    #     binary       = values['image_binary']
    #     file_data    = BytesIO(base64.b64decode(binary))
    #     content_type = 'image/png' if binary[0] == 'i' else 'image/jpeg'
    #     file         = FileStorage(file_data, filename=file_name, content_type=content_type)
    #     format_file  = '.png' if content_type == 'image/png' else '.jpeg'
    #     file.save(os.path.join(path, str(file_name) + format_file))
    #     self.browse(file_name).write({'format_file' : format_file})
    #     return result

    # def write(self, values):
    #     if values.get('image_binary', False):
    #         path   = self.env.ref('sale_contract.path_image_sc').read()[0]['value']
    #         file_name    = self.id
    #         binary       = values['image_binary']
    #         file_data    = BytesIO(base64.b64decode(binary))
    #         content_type = 'image/png' if binary[0] == 'i' else 'image/jpeg'
    #         file         = FileStorage(file_data, filename=file_name, content_type=content_type)
    #         format_file  = '.png' if content_type == 'image/png' else '.jpeg'
    #         file.save(os.path.join(path, str(file_name) + format_file))
    #     return super(SaleContractLine, self).write(values)
    

    # def unlink(self):
    #     path   = self.env.ref('sale_contract.path_image_sc').read()[0]['value']
    #     for rec in self:
    #         file = "%s%s%s" % (path, rec.id, rec.format_file)
    #         os.remove(file)
    #     return super(SaleContractLine, self).unlink()
    # End Function ALl About Image