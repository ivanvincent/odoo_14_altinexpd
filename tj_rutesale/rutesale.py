import time
import logging
from collections import namedtuple
import json
import time

import numpy as np

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, Warning
import odoo.addons.decimal_precision as dp


_logger = logging.getLogger(__name__)
STATES = [('draft', 'Draft'), ('confirm', 'Confirm'), ('selling', 'Selling'), ('close', 'Close'), ('cancel', 'Cancelled'), ('reject', 'Reject')]
# STATES = [('draft', 'Draft'), ('open', 'Open'), ('confirm', 'Confirm'), ('posted', 'Posted'), ('close', 'Close'), ('reject', 'Reject')]


class RuteSale(models.Model):
    _name = 'rute.sale'
    _rec_name = 'name'
    _description = 'Rute Sale'


    name              = fields.Char(string='Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    date_plan         = fields.Date('Date RuteSale', help='', )
    date_actual       = fields.Datetime('Actual Date', help='', readonly=True, default=fields.Datetime.now,states={'draft': [('readonly', False)]})
    date_pending      = fields.Datetime('Pending Date', help='', readonly=True,states={'posted': [('readonly', False)]}, copy=False)
    group_id          = fields.Many2one(comodel_name='rute.group', string='Group', copy=True)
    sales_id          = fields.Many2one(comodel_name='hr.employee', string='Sales', copy=True)
    driver_id         = fields.Many2one(comodel_name='hr.employee', string='Driver', copy=True)
    helper_id         = fields.Many2one(comodel_name='hr.employee', string='Helper', copy=True)    
    datetime_in       = fields.Datetime('Datetime In', help='', readonly=True,states={'draft': [('readonly', False)]}, copy=False)
    datetime_out      = fields.Datetime('Datetime Out', help='', readonly=True,states={'draft': [('readonly', False)]}, copy=False)
    rute_cust_ids     = fields.One2many('rute.sale.cust', 'rute_id' , copy=True , readonly=True,states={'draft': [('readonly', False)]})
    rute_new_cust_ids = fields.One2many('rute.sale.new.cust', 'rute_id' , readonly=True,states={'draft': [('readonly', False)]}, copy=False)
    rute_kontra_ids   = fields.One2many('rute.sale.kontra', 'rute_id' , readonly=True,states={'draft': [('readonly', False)]}, copy=False)
    category          = fields.Selection([('sales', 'Sales PO'),('expedisi', 'Expedisi'),('galon', 'Galon')],"Category",required=True, default="sales", readonly=True, states={'draft': [('readonly', False)]})
    cust_type         = fields.Char('Customer Type', readonly=True, default="customer", states={'draft': [('readonly', False)]})
    state             = fields.Selection(string="State", selection=STATES, default=STATES[0][0], required=True)
    jumlah            = fields.Float(string="Jumlah",compute="get_amount_rute",store=True,default=0,)
    amount_rute       = fields.Float(string="Amount Order Rute",compute="get_amount_rute",store=True,default=0,)
    amount_pay        = fields.Float(string="Amount Payment Via",compute="get_amount_pay",store=True,default=0,)
    count_pay         = fields.Integer('Count Payment Via')
    kontrabon_id      = fields.Many2one('kontrabon.order', 'Kontrabon', copy=False)
    out_latitude      = fields.Char('Out Latitude', copy=False)
    out_longitude     = fields.Char('Out Longitude', copy=False)
    in_latitude       = fields.Char('In Latitude', copy=False)
    in_longitude      = fields.Char('In Longitude', copy=False)
    picking_ids       = fields.Many2many(comodel_name='stock.picking', relation='rute_sale_stock_picking_rel',string='Transfer')
    picking_count     = fields.Integer(string='Total Transfer',compute="_get_picking_count")
    persen_tepat      = fields.Float('% Tepat', store=True, readonly=True, compute='_get_persen')
    persen_kunjungan  = fields.Float('% Kunjungan', store=True, readonly=True, compute='_get_persen_kunjungan')
    jumlah_kunjungan  = fields.Float('Jumlah Kunjungan', store=True, readonly=True, compute='_get_persen_kunjungan')
    jumlah_toko       = fields.Float('Jumlah Toko', store=True, readonly=True, compute='_get_persen_kunjungan')
    jumlah_qty_target = fields.Float('Qty Target', readonly=True)
    jumlah_qty_target_persen = fields.Float('Qty Target %', readonly=True)
    jumlah_new_cust_target        = fields.Float('New Cust Target', readonly=True)
    jumlah_new_cust_target_persen = fields.Float('New Cust Target %', readonly=True)
    new_customer = fields.Integer(string="New Customer",compute="compute_new_customer",store=True,default=0,)

    _sql_constraints = [('name_uniq', 'unique(name)', _('Nomor Rute Sale tidak boleh sama'))]
    
    
    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        action['domain'] = [('id','in',self.picking_ids.ids)]
        action['context'] = {}
        return action
    
    def _get_picking_count(self):
        for rute in self:
            rute.picking_count = len(rute.picking_ids)
    
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

    
    @api.depends('rute_cust_ids.partner_latitude')
    def _get_persen_kunjungan(self):
        for rute in self :
            persentase_kunjungan = 0
            jum_kunjungan = 0
            jum_toko = 1
            if rute.rute_cust_ids :
                kunjungan_ids = rute.rute_cust_ids.filtered(lambda rute_cust: rute_cust.partner_latitude != False)
                if kunjungan_ids :
                    jum_kunjungan = len(kunjungan_ids)
                    # jum_toko = len(rute.rute_cust_ids)
                    jum_toko = len(rute_cust_ids.so_id)
                    persentase_kunjungan = float(jum_kunjungan) / float(jum_toko) * 100
            rute.persen_kunjungan = persentase_kunjungan
            rute.jumlah_kunjungan = jum_kunjungan
            rute.jumlah_toko = jum_toko

    
    @api.depends("rute_new_cust_ids")
    def compute_new_customer(self):
        for rute in self:
            total_new_customer = 0
            
            if rute.rute_new_cust_ids:
                total_new_customer += len(rute.rute_new_cust_ids)
            
            rute.new_customer = total_new_customer

    
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
            
            if rute.check_so_line_rute():
                sale_order = rute.rute_cust_ids.mapped('so_id')
                so_line = sale_order.mapped('order_line')
                total_so_line = sum(line.price_subtotal for line in so_line)
                price_subtotal += total_so_line

                jumlah_subtotal = sum(line.product_uom_qty for line in so_line)
                jumlah_total += jumlah_subtotal
            
            rute.amount_rute = price_subtotal
            rute.jumlah = jumlah_total
    
    
    def action_view_customer(self):
        import logging;
        _logger = logging.getLogger(__name__)
        _logger.warning('='*40)
        _logger.warning(self._context)
        _logger.warning('='*40)

    
    def action_cancel(self):
        data = {'state': STATES[0][0]}
        self.write(data)

    
    def action_confirm(self):
        data = {'state': STATES[1][0]}
        self.write(data)

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
    
    rute_id           = fields.Many2one('rute.sale', 'Rute', help='')
    partner_id        = fields.Many2one('res.partner', 'Partner',help='Partner to be Sale',) 
    state_visit_id    = fields.Many2one('rute.state.visit', 'State Visit', help='', copy=False)
    pay_via_sales     = fields.Boolean(string="Status Payment", copy=False)
    amount_via_sales  = fields.Float('Amount Payment', copy=False)
    so_id             = fields.Many2one('sale.order', 'Sale Order', help='', copy=False)
    currency_id       = fields.Many2one(comodel_name="res.currency",string="Currency",related="so_id.currency_id",store=True,)
    so_amount         = fields.Monetary(string="Amount Sale",copy=False,related="so_id.amount_total",store=True,)
    so_qty            = fields.Float('Quantity Sale', copy=False)
    partner_latitude  = fields.Char('Latitude', copy=False)
    partner_longitude = fields.Char('Longitude', copy=False)
    akurasi           = fields.Char('Akurasi', compute='get_haversine', store=True, copy=False)
    tepat_tidak       = fields.Boolean(string="Tepat/Tidak", compute='get_haversine', store=True, copy=False)     # Haversine
    datetime_start    = fields.Char('Datetime Start', copy=False)
    datetime_end      = fields.Char('Datetime End', copy=False)
        
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
            visit.tepat_tidak = (akurasi < 100)

    
    def check_so_currency_id(self):
        self.ensure_one()
        so_id = self.so_id
        if so_id and so_id.currency_id:
            return True


class RuteSaleKontra(models.Model):
    _name = 'rute.sale.kontra'
    _description = 'Rute Sale Kontrabon'
    
    rute_id           = fields.Many2one('rute.sale', 'Rute', help='')
    partner_id        = fields.Many2one('res.partner', 'Partner',help='Partner to be Sale') 
    inv_id            = fields.Many2one('account.invoice', 'Invoice', help='', copy=False)
    pay_via_sales     = fields.Boolean(string="Status Payment", copy=False)
    amount_via_sales  = fields.Float('Amount Payment', copy=False)    
    partner_latitude  = fields.Char('Latitude', copy=False)
    partner_longitude = fields.Char('Longitude', copy=False)
    datetime_start    = fields.Char('Datetime Start', copy=False)
    datetime_end      = fields.Char('Datetime End', copy=False)


class RuteSaleNewCust(models.Model):
    _name = 'rute.sale.new.cust'
    _description = 'Rute Sale New Customer'
    
    rute_id           = fields.Many2one('rute.sale', 'Rute', help='')
    partner_name      = fields.Char('Nama Toko', )
    partner_alamat    = fields.Char('Alamat', )
    partner_telp      = fields.Char('Telp', )
    partner_cp        = fields.Char('Contact', )
    datetime_start    = fields.Datetime('Datetime Start', )
    partner_latitude  = fields.Char('Latitude', )
    partner_longitude = fields.Char('Longitude', )
    partner_image1    = fields.Binary('Image')


class RutePartner(models.Model):
    _name = 'rute.partner'
    _description = 'Rute Partner'
    
    
    category   = fields.Selection([('sales', 'Sales PO'),('expedisi', 'Expedisi'),('galon', 'Galon')],"Category",required=True, default="sales")
    partner_id = fields.Many2one('res.partner', 'Partner',help='Partner to be Sale') 
    seminggu   = fields.Integer(string='X Seminggu', help="Jumlah kunjungan seminggu")
    qty_rata2  = fields.Integer(string='Rata2 Qty', help="Jumlah rata2 order seminggu")
    k_senin    = fields.Boolean(string="Kanvasing Senin")
    k_selasa   = fields.Boolean(string="Kanvasing Selasa")
    k_rabu     = fields.Boolean(string="Kanvasing Rabu")
    k_kamis    = fields.Boolean(string="Kanvasing Kamis")
    k_jumat    = fields.Boolean(string="Kanvasing Jumat")
    k_sabtu    = fields.Boolean(string="Kanvasing Sabtu")
    k_minggu   = fields.Boolean(string="Kanvasing Minggu")

    s_senin    = fields.Boolean(string="Sales Senin")
    s_selasa   = fields.Boolean(string="Sales Selasa")
    s_rabu     = fields.Boolean(string="Sales Rabu")
    s_kamis    = fields.Boolean(string="Sales Kamis")
    s_jumat    = fields.Boolean(string="Sales Jumat")
    s_sabtu     = fields.Boolean(string="Sales Sabtu")
    s_minggu = fields.Boolean(string="Sales Minggu")

    g_senin = fields.Many2one(comodel_name='rute.group', string='Group Senin')
    g_selasa = fields.Many2one(comodel_name='rute.group', string='Group Selasa')
    g_rabu = fields.Many2one(comodel_name='rute.group', string='Group Rabu')
    g_kamis = fields.Many2one(comodel_name='rute.group', string='Group Kamis')
    g_jumat = fields.Many2one(comodel_name='rute.group', string='Group Jumat')
    g_sabtu = fields.Many2one(comodel_name='rute.group', string='Group Sabtu')
    g_minggu = fields.Many2one(comodel_name='rute.group', string='Group Minggu')    


class RuteGroup(models.Model):
    _name = 'rute.group'
    _description = 'Rute Group'
    
    name    = fields.Char('Code Group', help='Code Group', readonly=True, states={'draft': [('readonly', False)]}) #
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

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    amount_pay = fields.Float('Amount Payment Via')
