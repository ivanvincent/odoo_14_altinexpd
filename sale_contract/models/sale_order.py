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
import calendar


_logger = logging.getLogger(__name__)


class SrMultiProduct(models.TransientModel):
    _name = 'sales.all.multi.product'

    product_ids = fields.Many2many('product.product', string="Product")

    def add_product(self):
        order=self.env['sale.order'].browse(self._context.get('active_id'))
        order_lines = []
        for line in self.product_ids:
            order_lines.append((0, 0, {'product_id' : line.id}))
        self.env['sale.order'].browse(self._context.get('active_id')).order_line = order_lines
        return

    def sc_add_product(self):
        order=self.env['sale.contract'].browse(self._context.get('active_id'))
        order_lines = []
        for line in self.product_ids:
            order_lines.append((0, 0, {'product_id' : line.id}))
        self.env['sale.contract'].browse(self._context.get('active_id')).lines = order_lines
        return

class SaleForcastMultiProduct(models.TransientModel):
    _name = 'sales.forcast.multi.product'

    contract_line_ids = fields.Many2many('sale.contract.line', string="Forcast line",)
    contract_id = fields.Many2one('sale.contract', string='Sales Forcast',)

    # @api.model
    # def default_get(self, fields):
    #     res = super(SaleForcastMultiProduct, self).default_get(fields)
    #     if 'contract_id' in fields and self._context.get('active_id') and not res.get('contract_id'):
    #         res = {'contract_id': self._context['contract_id.id']}
    #     return res

    def add_product(self):
        # order = self._context.get('active_id')
        # order.contract_id = self.contract_id.id
        # order.update({'contract_id' : self.contract_id.id,})
        order=self.env['sale.order'].browse(self._context.get('active_id'))
        order_lines = []
        for line in self.contract_line_ids:
            # order_line = self.env['sale.order.line'].create({
            #     'order_id'          : self._context.get('active_id'),
            #     'product_id'        : line.product_id.id,
            #     'product_uom_qty'   : line.qty - line.qty_so,
            #     'price_unit'        : line.price_unit,
            #     'name'              : line.name_get()[0][1],
            #     'product_uom'       : line.product_id.uom_id.id,
            #     'state'             : 'draft',
            #     'contract_line_id'  : line.id,
            # })

            # order_line.order_id.write({
            #     'contract_id'       : self.contract_id.id,
            #     'partner_id'        : self.contract_id.partner_id.id,
            #     'pricelist_id'      : self.contract_id.pricelist_id.id,
            #     'client_order_ref'  : self.contract_id.no_bon,
            #     'payment_term_id'   : self.contract_id.term_of_payment.id,
            #     })


            order_lines.append((0, 0, {
                'product_id'        : line.product_id.id,
                'product_uom_qty'   : line.qty - line.qty_so,
                'price_unit'        : line.price_unit,
                'name'              : line.name_get()[0][1],
                'product_uom'       : line.product_id.uom_id.id,
                'state'             : 'draft',
                'contract_line_id'  : line.id,
            }))

        self.env['sale.order'].browse(self._context.get('active_id')).order_line = order_lines
        
        # self.env['sale.order'].create({
        #     # 'id'                : self._context.get('active_id'),
        #     'contract_id'       : self.contract_id.id,
        #     'partner_id'        : self.contract_id.partner_id.id,
        #     'pricelist_id'      : self.contract_id.pricelist_id.id,
        #     'client_order_ref'  : self.contract_id.no_bon,
        #     'payment_term_id'   : self.contract_id.term_of_payment.id,
        #     'order_line'        : order_lines,
        #     })

        return

class SaleOrderContract(models.Model):
    _inherit = 'sale.order'

    contract_id = fields.Many2one('sale.contract', string='Sales Forecast', copy=False)
    # no_wo       = fields.Char('Work Order')
    # design_code = fields.Char(string='Design Code')
    design_id = fields.Many2one('makloon.design', string='design')
    delivery_date_desc = fields.Char(string='Delivery Date Desc', store=False, compute='compute_delivery_date_desc')

    def action_select_product(self):
        view_id = self.env.ref('sale_contract.sales_forcast_form_view_select_multi_product_wizard')
        wiz = self.env['sales.forcast.multi.product'].create({'contract_id': self.contract_id.id})
        return {
            'name': _('Select Product'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sales.forcast.multi.product',
            'target': 'new',
            'views': [(view_id.id, 'form')],
            'view_id': view_id.id,
            'res_id': wiz.id,
            'context': self.env.context,
            }

<<<<<<< HEAD
    # @api.onchange('date_order')
    @api.depends('delivery_date')
    def compute_delivery_date_desc(self):
        if self.delivery_date:

            tahun = int(self.delivery_date.strftime("%Y"))
            bulan = int(self.delivery_date.strftime("%m"))
            tgl = int(self.delivery_date.strftime("%d"))
            
            tmp_desc = self.get_current_week(tahun,bulan,str(tgl))
            tmp_out = []
            tmp_out.append("Week ")
            tmp_out.append(str(tmp_desc))
            if bulan == 1:
                tmp_out.append(" Januari")
            elif bulan == 2:
                tmp_out.append(" Februari")
            elif bulan == 3:
                tmp_out.append(" Maret")
            elif bulan == 4:
                tmp_out.append(" April")
            elif bulan == 5:
                tmp_out.append(" Mei")
            elif bulan == 6:
                tmp_out.append(" Juni")
            elif bulan == 7:
                tmp_out.append(" Juli")
            elif bulan == 8:
                tmp_out.append(" Agustus")
            elif bulan == 9:
                tmp_out.append(" September")
            elif bulan == 10:
                tmp_out.append(" Oktober")
            elif bulan == 11:
                tmp_out.append(" November")
            else:
                tmp_out.append(" Desember")

            tmp_out = ''.join(tmp_out)
            self.delivery_date_desc = tmp_out
=======
    @api.onchange('date_order')
    def onchange_date_order_date(self):

        tahun = int(self.date_order.strftime("%Y"))
        bulan = int(self.date_order.strftime("%m"))
        tgl = int(self.date_order.strftime("%d"))
    # @api.onchange('delivery_date')
    # def onchange_date_delivery_date(self):

    #     tahun = int(self.delivery_date.strftime("%Y"))
    #     bulan = int(self.delivery_date.strftime("%m"))
    #     tgl = int(self.delivery_date.strftime("%d"))
        
        tmp_desc = self.get_current_week(tahun,bulan,str(tgl))
        tmp_out = []
        tmp_out.append("Week ")
        tmp_out.append(str(tmp_desc))
        if bulan == 1:
            tmp_out.append(" Januari")
        elif bulan == 2:
            tmp_out.append(" Februari")
        elif bulan == 3:
            tmp_out.append(" Maret")
        elif bulan == 4:
            tmp_out.append(" April")
        elif bulan == 5:
            tmp_out.append(" Mei")
        elif bulan == 6:
            tmp_out.append(" Juni")
        elif bulan == 7:
            tmp_out.append(" Juli")
        elif bulan == 8:
            tmp_out.append(" Agustus")
        elif bulan == 9:
            tmp_out.append(" September")
        elif bulan == 10:
            tmp_out.append(" Oktober")
        elif bulan == 11:
            tmp_out.append(" November")
>>>>>>> 6883d51d115a5bcfc4b61d5b5afb62269fcab825
        else:
            self.delivery_date_desc = False

    def get_current_week(self, tahun, bulan, tgl):
        tmp_cal = calendar.month(tahun, bulan).split('\n')[2:]
        tmp_list = []
        index = 1
        tmp_out = None
        kondisi = False
        for val in tmp_cal:

            tmp_string = val.replace(" ", ",").replace(",,", ",").lstrip(",")
            tmp_list.append(tmp_string)

            for val_hari in tmp_list:
                if str(tgl) in val_hari:
                    tmp_out = index
                    kondisi = True

                if kondisi:
                    break

            if kondisi:
                break

            index += 1
            tmp_list.clear()

        return tmp_out

    # @api.onchange('contract_id')
    # def contract_change(self):
    #     if self.contract_id :
    #         for rec in self:
    #             rec.partner_id = rec.contract_id.partner_id.id
    #             rec.pricelist_id = rec.contract_id.pricelist_id.id
    #             rec.client_order_ref = rec.contract_id.no_bon
    #             rec.payment_term_id = rec.contract_id.term_of_payment.id


    @api.onchange('contract_id')
    def _contract_change(self):
        if self.contract_id :
            self.order_line = False
            for rec in self:
                rec.partner_id = rec.contract_id.partner_id.id
                rec.pricelist_id = rec.contract_id.pricelist_id.id
                rec.client_order_ref = rec.contract_id.no_bon
                rec.payment_term_id = rec.contract_id.term_of_payment.id
                rec.design_id = rec.contract_id.design_code_id.id
                
                # rec.write({
                #     'partner_id' : rec.contract_id.partner_id.id,
                #     'pricelist_id' : rec.contract_id.pricelist_id.id,
                #     'client_order_ref': rec.contract_id.no_bon,
                #     'payment_term_id': rec.contract_id.term_of_payment.id,
                #     })

            # so_line_vals = []
            order_lines = []
            # order_lines = [(5, 0, 0)]
            for line in self.contract_id.lines :
                qty_sisa = line.qty - line.qty_so
                no_id = int(line.id)
                # so_line_vals.append({
                #     'product_id': line.product_id.id,
                #     'product_uom_qty': qty_sisa,
                #     'price_unit': line.price_unit,
                #     'name': line.name_get()[0][1],
                #     'product_uom': line.product_id.uom_id.id,
                #     'state': 'draft',
                #     'contract_line_id': line.id,
                # })
                # order_lines.append((0, 0, data))

                order_lines.append((0, 0, {
                    'product_id'        : line.product_id.id,
                    'product_uom_qty'   : qty_sisa,
                    'price_unit'        : line.price_unit,
                    'name'              : line.name_get()[0][1],
                    'product_uom'       : line.product_id.uom_id.id,
                    'state'             : 'draft',
                    'contract_line_id'  : line.id,
                }))
            self.order_line = order_lines

                # raw_data = {
                #     'product_id'        : line.product_id.id,
                #     'product_uom_qty'   : qty_sisa,
                #     'price_unit'        : line.price_unit,
                #     'name'              : line.name_get()[0][1],
                #     'product_uom'       : line.product_id.uom_id.id,
                #     'state'             : 'draft',
                #     'contract_line_id'  : line.id,
                # }                
                # self.order_line.create(raw_data)
            
    # @api.multi
    # def action_confirm(self):
    #     res=super(SaleOrderContract,self).action_confirm()
    #     for wo_id in self :
    #         wo_id.name = "WO%s%s"%(self.contract_id.name[-10:], self.name)
    #     return res

class SaleOrderLineContract(models.Model):
    _inherit = 'sale.order.line'

    contract_line_id = fields.Many2one('sale.contract.line', string='Sales Forecast Line', copy=False)
    client_order_ref = fields.Char(string='DN No', related="order_id.client_order_ref")
