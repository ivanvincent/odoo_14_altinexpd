from datetime import datetime
import time
import logging


from collections import namedtuple
import json
import time

import numpy as np

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
# from odoo.addons.procurement.models import procurement
from odoo.exceptions import UserError, Warning
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import odoo.addons.decimal_precision as dp


_logger = logging.getLogger(__name__)
# STATES = [('draft', 'Draft'), ('open', 'Open'), ('posted', 'Posted'), ('close', 'Close'), ('reject', 'Reject')]
STATES = [('draft', 'Draft'), ('confirm', 'Confirm'), ('selling', 'Selling'), ('close', 'Close'), ('cancel', 'Cancelled'), ('reject', 'Reject')]


class RuteSale(models.Model):
    _name = 'rute.sale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Rute Sale'
            
    name                = fields.Char(string='Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    date_plan           = fields.Date('Date RuteSale', help='', ) #readonly=True, states={'draft': [('readonly', False)]}
    date_actual         = fields.Datetime('Actual Date', help='', readonly=True, default=fields.Datetime.now,states={'draft': [('readonly', False)]})
    date_pending        = fields.Datetime('Pending Date', help='', readonly=True, states={'posted': [('readonly', False)]}, copy=False)
    group_id            = fields.Many2one(comodel_name='rute.group', string='Group', copy=True)
    sales_id            = fields.Many2one(comodel_name='hr.employee', string='Sales', copy=True,required=True, )
    driver_id           = fields.Many2one(comodel_name='hr.employee', string='Driver', copy=True,required=True, )
    helper_id           = fields.Many2one(comodel_name='hr.employee', string='Helper', copy=True)    
    datetime_out        = fields.Datetime('Datetime Out', help='', readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    datetime_in         = fields.Datetime('Datetime In', help='', readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    rute_cust_ids       = fields.One2many('rute.sale.cust', 'rute_id' , copy=True , readonly=True, states={'draft': [('readonly', False)]})
    rute_new_cust_ids   = fields.One2many('rute.sale.new.cust', 'rute_id' , readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    rute_kontra_ids     = fields.One2many('rute.sale.kontra', 'rute_id' , readonly=True,states={'draft': [('readonly', False)]}, copy=False)
    category            = fields.Selection([('sales', 'Sales PO'),('expedisi', 'Expedisi'),('galon', 'Galon'),('rss', 'RSS')],"Category",required=True, default="sales", readonly=True, states={'draft': [('readonly', False)]})
    cust_type           = fields.Char('Customer Type', readonly=True, default="customer", states={'draft': [('readonly', False)]})
    state               = fields.Selection(string="State", selection=STATES, default=STATES[0][0], required=True)
    jumlah              = fields.Float(string="Jumlah",compute="get_amount_rute",store=True,default=0,)
    amount_rute         = fields.Float(string="Amount Order Rute",compute="get_amount_rute",store=True,default=0,)
    amount_pay          = fields.Float(string="Amount Payment Via",compute="get_amount_pay",store=True,default=0,)
    count_pay           = fields.Integer('Count Payment Via')
    kontrabon_id        = fields.Many2one('kontrabon.order', 'Kontrabon', copy=False)
    out_latitude        = fields.Char('Out Latitude', copy=False)
    out_longitude       = fields.Char('Out Longitude', copy=False)
    in_latitude         = fields.Char('In Latitude', copy=False)
    in_longitude        = fields.Char('In Longitude', copy=False)
    warehouse_id        = fields.Many2one('stock.warehouse', string='Warehouse',domain=[('is_stock_point','=',True)],required=True, )
    jalur_id            = fields.Many2one('res.partner.jalur', string='Jalur',required=True, )
    vehicle_id          = fields.Many2one('fleet.vehicle', string='Vehicle',required=True, )
    persen_tepat        = fields.Float('% Tepat', store=True, readonly=True, compute='_get_persen')
    persen_kunjungan    = fields.Float('% Kunjungan', store=True, readonly=True, compute='_get_persen_kunjungan')
    jumlah_kunjungan    = fields.Float('Jumlah Kunjungan', store=True, readonly=True, compute='_get_persen_kunjungan')
    jumlah_toko         = fields.Float('Jumlah Toko', store=True, readonly=True, compute='_get_persen_kunjungan')
    jumlah_so           = fields.Float('Jumlah SO', store=True, readonly=True, compute='get_amount_rute')

    jumlah_qty_target   = fields.Float('Qty Target', readonly=True)
    jumlah_qty_target_persen = fields.Float('Qty Target %', readonly=True)
    jumlah_new_cust_target = fields.Float('New Cust Target', readonly=True)
    jumlah_new_cust_target_persen = fields.Float('New Cust Target %', readonly=True)

    new_customer         = fields.Integer( string="New Customer", compute="compute_new_customer", store=True, default=0, )
    detail_new_cust      = fields.Char(string='Detail New Cust', compute="compute_new_customer")
    group_ids            = fields.One2many('rute.sale.line.group', 'rute_id', string='Summary',compute='_compute_all_product',)
    line_ids             = fields.One2many('rute.sale.line', 'rute_id', string='All Product')
    rute_lines           =  fields.Many2many(comodel_name='rute.sale.line',compute="_get_lines",string='Details' )
    line_fg_ids          = fields.One2many('rute.sale.line.fg', 'rute_id', string='All Product FG')
    line_siba_ids        = fields.One2many('rute.sale.line.siba', 'rute_id', string='All Product SIBA')
    line_return_ids      = fields.One2many('rute.sale.line.return', 'rute_id', string='All Product Return')
    expense_ids          = fields.One2many('rute.sale.line.expense', 'rute_id', string='Expense')
    config_id            = fields.Many2one('rute.sale.config', string='Config',compute="_get_compute_config")
    product_category_ids = fields.Many2many(related="config_id.product_category_ids",string='Product Category')
    picking_ids          = fields.Many2many(comodel_name='stock.picking', relation='rute_sale_stock_picking_rel',string='Transfer')
    picking_count        = fields.Integer(string='Total Transfer',compute="_get_picking_count")
    _sql_constraints     = [('name_uniq', 'unique(name)', _('Nomor Rute Sale tidak boleh sama'))]
    
    
    
    def create_picking(self):
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        if not self.rute_lines:
            raise UserError('Mohon maaf pastikan \nList product di isi terlebih dahulu')
        elif not self.rute_cust_ids:
            raise UserError('Mohon maaf pastikan \nList Customer di isi terlebih dahulu')
            
            
        for line in self.rute_lines:
            if float_is_zero(line.product_uom_qty,precision_digits=precision_digits):
                raise UserError('Mohon maaf pastikan %s \nquantity product yang akan dikirim tidak nol'%(line.product_id.name))
            
            elif float_is_zero(line.qty_onhand,precision_digits=precision_digits):
                type = 'Finish Good' if line.type == 'fg' else 'SIBA'
                raise UserError('Mohon maaf stock product %s di lokasi %s nol'%(line.product_id.name,type))
            
            
        if self.config_id and self.line_fg_ids:
            picking_fg = self.env['stock.picking'].create({
                'picking_type_id': self.config_id.default_picking_type_id.id,
                'date': self.date_actual,
                'rute_id': self.id,
                'scheduled_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'origin': self.name,   
                'procure_stock':'fg',
                'location_id': self.config_id.default_picking_type_id.default_location_src_id.id,
                'vehicle_id':self.vehicle_id.id,
                'location_dest_id': self.vehicle_id.fg_stock_location_id.id,
                'immediate_transfer': False,
                'move_ids_without_package': [(0,0,{ 'name': line.product_id.name,
                        'description_picking': line.rute_id.name,
                        'product_id'        : line.product_id.id,
                        'product_uom'       : line.product_uom_id.id,
                        'product_uom_qty'   : line.product_uom_qty,
                        'quantity_done'     : line.product_uom_qty if line.qty_onhand else 0,
                        'x_ket'             : line.rute_id.name,
                        'date'              : self.date_actual,
                        'location_id'       : self.config_id.default_picking_type_id.default_location_src_id.id, 
                        'location_dest_id'  : self.vehicle_id.fg_stock_location_id.id,
                        'state'             : 'draft',
                        'company_id'        : self.env.company.id,
                        'price_unit'        : line.product_id.standard_price,
                        'picking_type_id'   : self.config_id.default_picking_type_id.id,
                        'origin'            : self.name,
                        'warehouse_id'      : self.warehouse_id.id,
                    }) for line in self.line_fg_ids]
            })
            
            
            
            if picking_fg.id:
                self.picking_ids = [(4,picking_fg.id)]
        
        
        if self.config_id and self.line_siba_ids:
            picking_siba = self.env['stock.picking'].create({
                'picking_type_id': self.config_id.default_picking_type_id.id,
                'date': self.date_actual,
                'scheduled_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'origin': self.name,   
                'rute_id': self.id,
                'procure_stock':'siba',
                'location_id': self.config_id.default_picking_type_id.default_location_siba_id.id,
                'vehicle_id':self.vehicle_id.id,
                'location_dest_id': self.vehicle_id.siba_stock_location_id.id,
                'immediate_transfer': False,
                'move_ids_without_package': [(0,0,{ 'name': line.product_id.name,
                        'description_picking': line.rute_id.name,
                        'product_id'        : line.product_id.id,
                        'product_uom'       : line.product_uom_id.id,
                        'product_uom_qty'   : line.product_uom_qty,
                        'quantity_done'     : line.product_uom_qty if line.qty_onhand else 0,
                        'x_ket'             : line.rute_id.name,
                        'date'              : self.date_actual,
                        'location_id'       : self.config_id.default_picking_type_id.default_location_siba_id.id, 
                        'location_dest_id'  : self.vehicle_id.siba_stock_location_id.id,
                        'state'             : 'draft',
                        'company_id'        : self.env.company.id,
                        'price_unit'        : line.product_id.standard_price,
                        'picking_type_id'   : self.config_id.default_picking_type_id.id,
                        'origin'            : self.name,
                        'warehouse_id'      : self.warehouse_id.id,
                    }) for line in self.line_siba_ids]
            })
            
                    
            if picking_siba.id:
                self.picking_ids = [(4,picking_siba.id)]
                
        
        
        if self.picking_count > 0:
            for picking in self.picking_ids:
                picking.sudo().action_confirm()
                picking.sudo().action_assign()
                picking.sudo().button_validate()
                
                
            
    
    
    
    
    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        action['domain'] = [('id','in',self.picking_ids.ids)]
        action['context'] = {}
        return action
    
    def _get_picking_count(self):
        for rute in self:
            rute.picking_count = len(rute.picking_ids)
    
    
    
    @api.depends('line_ids', 'line_ids.product_id', 'line_ids.product_uom_qty')
    def _compute_all_product(self):
        for rute in self:
            group_ids = []
            line_ids = self.env['rute.sale.line'].read_group([('rute_id','=',rute.id)],['product_uom_qty'],'product_id',lazy=False)
            for line in line_ids:
                product_id = line.get('product_id')[0]
                product_uom_qty = line.get('product_uom_qty')
                group_ids.append((0,0,{"product_id":product_id,"product_uom_qty":product_uom_qty}))
            
            rute.group_ids = group_ids if group_ids else False
                
            
    
    def _get_lines(self):
        for rute in self:
            
            rute.rute_lines = [(6,0,rute.line_ids.ids)]

    
    def _get_compute_config(self):
        for rute in self:
            config_id = self.env['rute.sale.config'].search([('warehouse_id','=',rute.warehouse_id.id)])
            rute.config_id = config_id.id if config_id else False
    
    def _get_index_of_day(self,day):
        index = 0
        if day == 'Monday':
            index = 1
        elif day == 'Tuesday':
            index = 2
        elif day == 'Wednesday':
            index = 3
        elif day == 'Thursday':
            index = 4
        elif day == 'Friday':
            index = 5
        elif day == 'Saturday':
            index = 6
        elif day == 'Sunday':
            index = 7
        return str(index)
        
    
    
    def action_load_jwk(self):
        today = datetime.now().strftime("%A")
        today = self._get_index_of_day(today)
        jalur_line_ids = self.env['res.partner.jalur.line'].search([('jalur_id','=',self.jalur_id.id),('jwk','=',today)])
        line_ids = []
        for line in jalur_line_ids.filtered(lambda l:l.jalur_line_id.id not in [partner.id for partner in self.rute_cust_ids.mapped('partner_id')]):
            line_ids += [(0,0,{
                "jalur_line_id":line.id,
            })]
            
        self.rute_cust_ids =  line_ids

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('rute.sale') or _('New')
            vals['name'] = seq
            result = super(RuteSale, self).create(vals)
            return result

    
    @api.depends('rute_cust_ids.tepat_tidak')
    def _get_persen(self):
        for rute in self :
            persentase = 0
            if rute.rute_cust_ids :
                tepat_ids = rute.rute_cust_ids.filtered(lambda rute_cust: rute_cust.tepat_tidak)
                if tepat_ids :
                    tepat_data = len(tepat_ids)
                    all_data = len(rute.rute_cust_ids)
                    persentase = float(tepat_data) / float(all_data) * 100
            rute.persen_tepat = persentase

    @api.depends('rute_cust_ids.partner_id')
    def _get_persen_kunjungan(self):
        for rute in self :
            persentase_kunjungan = 0
            jum_kunjungan = 0
            rute.jumlah_toko = len(rute.rute_cust_ids)

            
            if rute.rute_cust_ids :
                kunjungan_ids = rute.rute_cust_ids.filtered(lambda rute_cust: rute_cust.partner_latitude != False)
                if kunjungan_ids :
                    jum_kunjungan = len(kunjungan_ids)
                    jum_toko = len(rute.rute_cust_ids)
                    persentase_kunjungan = float(jum_kunjungan) / float(jum_toko) * 100
            rute.persen_kunjungan = persentase_kunjungan
            rute.jumlah_kunjungan = jum_kunjungan
            

    
    @api.depends("rute_new_cust_ids")
    def compute_new_customer(self):
        for rute in self:
            total_new_customer = 0
            list_new_cust = []

            
            if rute.rute_new_cust_ids:
                total_new_customer += len(rute.rute_new_cust_ids)
                for i, a in enumerate(rute.rute_new_cust_ids):
                    list_new_cust.append(str(i+1) + ". " + str(a.partner_name))
            
            rute.new_customer = total_new_customer
            rute.detail_new_cust = '\n'.join(list_new_cust)

    
    @api.depends("rute_cust_ids")
    def get_amount_pay(self):
        for rute in self:
            total_payment = 0
            
            if rute.rute_cust_ids:
                r_line = rute.rute_cust_ids
                total_payment += sum(cust.amount_via_sales for cust in r_line)
            
            rute.amount_pay = total_payment

    
    @api.depends("rute_cust_ids.so_id")
    def get_jumlah(self):
        for rute in self:
            jumlah = 0
            
            if rute.check_so_line_rute():
                sale_order = rute.rute_cust_ids.mapped('so_id')
                so_line = sale_order.mapped('order_line')

                if so_line:
                    jumlah += sum(line.product_uom_qty for line in so_line)

            rute.jumlah = jumlah

    
    @api.depends("rute_cust_ids.so_id.order_line.price_subtotal","rute_cust_ids.so_id.order_line.product_uom_qty")
    def get_amount_rute(self):
        for rute in self:
            price_subtotal = 0
            total_so_line = 0
            jumlah_subtotal = 0
            jumlah_total = 0
            jum_so = 0
            
            if rute.check_so_line_rute():
                sale_order = rute.rute_cust_ids.mapped('so_id')
                so_line = sale_order.mapped('order_line')
                total_so_line = sum(line.price_subtotal for line in so_line)
                price_subtotal += total_so_line

                jumlah_subtotal = sum(line.product_uom_qty for line in so_line)
                jumlah_total += jumlah_subtotal

                jum_so = len(sale_order)

            
            rute.amount_rute = price_subtotal
            rute.jumlah = jumlah_total
            rute.jumlah_so = jum_so
            


    def action_cancel(self):
        self.state = 'cancel'
        
    def action_draft(self):
        if self.picking_count > 0:
            for picking in self.picking_ids:
                picking.sudo().do_unreserve()
        self.state = 'draft'
        

    
    def action_confirm(self):
        if not self.config_id:
            raise UserError('Mohon maaf Config untuk Stock point %s\nBelum Tersedia\nSegera Hubungi Administrator'%(self.warehouse_id.name))
        if not self.picking_ids:
            self.create_picking()
        if self.config_id and not self.expense_ids:
            self.expense_ids = [(0,0,{"expense_id":expense.id}) for expense in self.config_id.rute_sale_expense_ids] if self.config_id.rute_sale_expense_ids else False
        self.state = 'confirm'

    #posting langsung kurangi piutang here
    def action_post(self):
        rec = self[0]
        return self.write({'state': 'posted'})

    def check_so_line_rute(self):
        self.ensure_one()
        so_id = False

        if self.rute_cust_ids and self.rute_cust_ids.mapped('so_id'):
            so_id = self.rute_cust_ids.mapped('so_id')
            
            if so_id.mapped('order_line'):
                return True




    def action_reject(self):
        data = {'state': STATES[3][0]}
        self.write(data)
    

class RuteStateVisit(models.Model):
    _name = 'rute.state.visit'
    _description = 'Rute State Visit'
    
    name = fields.Char('State Visit', help='Code Status Visit')
    state = fields.Boolean(string="Status" , default=True)

class RuteSaleCust(models.Model):
    _name = 'rute.sale.cust'
    _description = 'Rute Sale Customer'
    
    
    rute_id       = fields.Many2one('rute.sale', 'Rute', help='')
    jalur_line_id = fields.Many2one('res.partner.jalur.line', string='Jalur Line')
    partner_id    = fields.Many2one('res.partner', 'Partner', help='Partner to be Sale',related="jalur_line_id.jalur_line_id")
    parent_id     = fields.Many2one('res.partner', 'Area',help='Area to be Sale',related="partner_id.parent_id")

    
    property_payment_term_id = fields.Many2one('account.payment.term', 'Payment Term',
                                  help='Partner Payment Term', related="partner_id.property_payment_term_id",
                                  )
    property_product_pricelist = fields.Many2one('product.pricelist', 'Price List',
                                  help='Partner Price List', related="partner_id.property_product_pricelist",
                                  )    

    state_visit_id = fields.Many2one('rute.state.visit', 'State Visit', help='', copy=False)

    pay_via_sales = fields.Boolean(string="Status Payment", copy=False)
    amount_via_sales = fields.Float('Amount Payment', copy=False)

    so_id = fields.Many2one('sale.order', 'Sale Order', help='', copy=False)
    
    move_id = fields.Many2one('account.move', string='Invoice')
    
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        related="move_id.currency_id",
        store=True,
    )

    # ORIGINAL CODE
    # so_amount = fields.Float('Amount Sale', copy=False)

    # CUSTOM CODE TO CHANGE THE ATTRIBUTE OF SO_AMOUNT FIELD
    move_amount = fields.Monetary(
        string="Amount Sale",
        copy=False,
        related="move_id.amount_total",
        store=True,
    )

    so_qty = fields.Float('Quantity Sale', copy=False)
    pinjaman_galon = fields.Float('Pinjaman Galon', copy=False)

    partner_latitude = fields.Char('Latitude', copy=False)
    partner_longitude = fields.Char('Longitude', copy=False)

    akurasi = fields.Char('Akurasi', compute='get_haversine', store=True, copy=False)

    # Haversine

    tepat_tidak = fields.Boolean(string="Tepat/Tidak", compute='get_haversine', store=True, copy=False)

    datetime_start = fields.Char('Datetime Start', copy=False)
    datetime_end = fields.Char('Datetime End', copy=False)

    def Haversine(lat1,lon1,lat2,lon2):
        R = 6371.0088
        lat1,lon1,lat2,lon2 = map(np.radians, [lat1,lon1,lat2,lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2) **2
        c = 2 * np.arctan2(a**0.5, (1-a)**0.5)
        d = R * c * 1000
        return round(d,4)

    def _Haversine(self, lat1,lon1,lat2,lon2):
        R = 6371.0088
        if lat1 and lon1 and lat2 and lon2 :
            if type(lat1) is not int and type(lat1) is not float :
                try :
                    lat1 = float(lat1)
                except :
                    raise Warning("Inputan latitude partner hanya boleh angka dan titik sebagai pemisah desimal.")
            if type(lon1) is not int and type(lon1) is not float :
                try :
                    lon1 = float(lon1)
                except :
                    raise Warning("Inputan longitude partner hanya boleh angka dan titik sebagai pemisah desimal.")
            if type(lat2) is not int and type(lat2) is not float :
                try :
                    lat2 = float(lat2)
                except :
                    raise Warning("Inputan latitude hanya boleh angka dan titik sebagai pemisah desimal.")
            if type(lon2) is not int and type(lon2) is not float :
                try :
                    lon2 = float(lon2)
                except :
                    raise Warning("Inputan longitude hanya boleh angka dan titik sebagai pemisah desimal.")
            lat1,lon1,lat2,lon2 = map(np.radians, [lat1,lon1,lat2,lon2])

            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2) **2
            c = 2 * np.arctan2(a**0.5, (1-a)**0.5)
            d = R * c * 1000
            return round(d,4)
        return ''


    @api.depends('partner_id.partner_latitude','partner_id.partner_longitude','partner_latitude','partner_longitude')
    def get_haversine(self):
        for visit in self :
            akurasi = visit._Haversine(visit.partner_id.partner_latitude,visit.partner_id.partner_longitude,visit.partner_latitude,visit.partner_longitude)
            visit.akurasi = akurasi
            visit.tepat_tidak = (akurasi < 100) if akurasi else False

    def check_so_currency_id(self):
        self.ensure_one()
        so_id = self.so_id
        if so_id and so_id.currency_id:
            return True



class RuteSaleKontra(models.Model):
    _name = 'rute.sale.kontra'
    _description = 'Rute Sale Kontrabon'
    
    rute_id = fields.Many2one('rute.sale', 'Rute', help='')
    partner_id = fields.Many2one('res.partner', 'Partner',
                                  help='Partner to be Sale',
                                  ) 
    inv_id = fields.Many2one('account.move', 'Invoice', help='', copy=False)
    
    pay_via_sales = fields.Boolean(string="Status Payment", copy=False)
    amount_via_sales = fields.Float('Amount Payment', copy=False)    
    
    partner_latitude = fields.Char('Latitude', copy=False)
    partner_longitude = fields.Char('Longitude', copy=False)

    datetime_start = fields.Char('Datetime Start', copy=False)
    datetime_end = fields.Char('Datetime End', copy=False)


class RuteSaleNewCust(models.Model):
    _name = 'rute.sale.new.cust'
    _description = 'Rute Sale New Customer'
    
    rute_id = fields.Many2one('rute.sale', 'Rute', help='')
    

    partner_name = fields.Char('Nama Toko', )
    partner_alamat = fields.Char('Alamat', )
    partner_telp = fields.Char('Telp', )
    partner_cp = fields.Char('Contact', )
    datetime_start = fields.Datetime('Datetime Start', )
    partner_latitude = fields.Char('Latitude', )
    partner_longitude = fields.Char('Longitude', )
    partner_image1 = fields.Binary('Image')
    sale_team_id = fields.Many2one('crm.team', string='Sales Team', related="rute_id.sales_id.user_id.sale_team_id", store=True,)
    date_plan_rute_sale = fields.Date(string='Date', related="rute_id.date_plan", store=True,)



class RutePartner(models.Model):
    _name = 'rute.partner'
    _description = 'Rute Partner'

    category    = fields.Selection([('sales', 'Sales PO'),('expedisi', 'Expedisi'),('galon', 'Galon'),('rss', 'RSS')],"Category",required=True, default="sales")
    partner_id  = fields.Many2one('res.partner', 'Partner',help='Partner to be Sale') 
    seminggu    = fields.Integer(string='X Seminggu', help="Jumlah kunjungan seminggu")
    qty_rata2   = fields.Integer(string='Rata2 Qty', help="Jumlah rata2 order seminggu")
    k_senin     = fields.Boolean(string="Kanvasing Senin")
    k_selasa    = fields.Boolean(string="Kanvasing Selasa")
    k_rabu      = fields.Boolean(string="Kanvasing Rabu")
    k_kamis     = fields.Boolean(string="Kanvasing Kamis")
    k_jumat     = fields.Boolean(string="Kanvasing Jumat")
    k_sabtu     = fields.Boolean(string="Kanvasing Sabtu")
    k_minggu    = fields.Boolean(string="Kanvasing Minggu")
    s_senin     = fields.Boolean(string="Sales Senin")
    s_selasa    = fields.Boolean(string="Sales Selasa")
    s_rabu      = fields.Boolean(string="Sales Rabu")
    s_kamis     = fields.Boolean(string="Sales Kamis")
    s_jumat     = fields.Boolean(string="Sales Jumat")
    s_sabtu     = fields.Boolean(string="Sales Sabtu")
    s_minggu    = fields.Boolean(string="Sales Minggu")
    g_senin     = fields.Many2one(comodel_name='rute.group', string='Group Senin')
    g_selasa    = fields.Many2one(comodel_name='rute.group', string='Group Selasa')
    g_rabu      = fields.Many2one(comodel_name='rute.group', string='Group Rabu')
    g_kamis     = fields.Many2one(comodel_name='rute.group', string='Group Kamis')
    g_jumat     = fields.Many2one(comodel_name='rute.group', string='Group Jumat')
    g_sabtu     = fields.Many2one(comodel_name='rute.group', string='Group Sabtu')
    g_minggu    = fields.Many2one(comodel_name='rute.group', string='Group Minggu')    


class RuteGroup(models.Model):
    _name = 'rute.group'
    _description = 'Rute Group'
    
    name     = fields.Char('Code Group', help='Code Group', readonly=True, states={'draft': [('readonly', False)]}) #
    sales_id = fields.Many2one(comodel_name='hr.employee', string='Sales')
    fleet_id = fields.Many2one(comodel_name="fleet.vehicle", string="Nama/No Mobil", required=True, store=True, track_visibility='onchange', )    
    state    = fields.Selection(string="State", selection=STATES, default=STATES[0][0], required=True, readonly=True)


class AbsensiQr(models.Model):
    _name = 'absensi.qr'
    _description = 'Absensi QR'
    
    name = fields.Char('Basensi QR', help='Absensi QR', readonly=True)
    rute_id = fields.Many2one('rute.sale', 'Rute', help='')
    datetime = fields.Datetime('Datetime', help='')
    key_qr = fields.Char('Key QR', )
    time_start = fields.Datetime('Time Start', help='', readonly=True)
    time_expired = fields.Datetime('Time Expired', help='', readonly=True)
    

    status_qr = fields.Char('Status QR', )


class AbsensiSale(models.Model):
    _name = 'absensi.sale'
    _description = 'Absensi Sale'
    
    name = fields.Char('Absen Sale', help='Absen Sale', readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date('Date', help='', )
    abs_qr_id = fields.Many2one('absensi.qr', 'QR', help='')
    sales_id = fields.Many2one(comodel_name='hr.employee', string='Sales')
    rute_id = fields.Many2one('rute.sale', 'Rute', help='')
    datetime_out = fields.Datetime('Datetime Out', help='', readonly=True)
    datetime_in = fields.Datetime('Datetime In', help='', readonly=True)
    session_key = fields.Char('Session Key', )
    imei_phone = fields.Char('Imei Phone', )
    uniq_phone_device = fields.Char('Uniq Phone Device', )
    account_phone_profile = fields.Char('Account Phone Profile', )

    out_latitude = fields.Char('Out Latitude', )
    out_longitude = fields.Char('Out Longitude', )

    in_latitude = fields.Char('In Latitude', )
    in_longitude = fields.Char('In Longitude', )

    

    token_key = fields.Char('Token Key', )

    
    state = fields.Selection(string="State", selection=STATES, default=STATES[0][0], readonly=True)

class AccountMove(models.Model):
    _inherit = 'account.move'


    amount_pay = fields.Float('Amount Payment Via')

class Followers(models.Model):
   _inherit = 'mail.followers'

   @api.model
   def create(self, vals):
        if 'res_model' in vals and 'res_id' in vals and 'partner_id' in vals:
            dups = self.env['mail.followers'].search([('res_model', '=',vals.get('res_model')),
                                           ('res_id', '=', vals.get('res_id')),
                                           ('partner_id', '=', vals.get('partner_id'))])
            if len(dups):
                for p in dups:
                    p.unlink()
        return super(Followers, self).create(vals)