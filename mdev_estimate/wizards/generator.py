from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
import requests
import logging
_logger = logging.getLogger(__name__)
import pytz
from pytz import timezone
from dateutil.relativedelta import relativedelta
import datetime
from datetime import datetime
import itertools
import math

class EstimateGeneratorWizard(models.TransientModel):
    _name = 'estimate.generator.wizard'
    _description = 'Estimate Generator Wizard'

    @api.depends('target_delivered_date')
    def _compute_date(self):
        for me in self:
            if me.target_delivered_date:
                year, week_num, day_of_week = me.target_delivered_date.isocalendar()
                if day_of_week == 1:
                    me.write({
                        'jwk': 'Senin'
                    })
                elif day_of_week == 2:
                    me.write({
                        'jwk': 'Selasa'
                    })
                elif day_of_week == 3:
                    me.write({
                        'jwk': 'Rabu'
                    })
                elif day_of_week == 4:
                    me.write({
                        'jwk': 'Kamis'
                    })
                elif day_of_week == 5:
                    me.write({
                        'jwk': "Jumat"
                    })
                elif day_of_week == 6:
                    me.write({
                        'jwk': 'Sabtu'
                    })
                elif day_of_week == 7:
                    me.write({
                        'jwk': 'Minggu'
                    })

    @api.onchange('cust_div_id')
    def onchange_cust_div_id(self):

        if self.cust_div_id:

            #select custom_group_id from Customer
            sql = """ 
                SELECT DISTINCT custom_group_id
                FROM    res_partner
                WHERE   active 
                        AND custom_div_id = %s 
                """ % (str(self.cust_div_id.id))

            self._cr.execute(sql)
            fall = self._cr.fetchall()

            grp_ids = []
            for item in fall:
                grp_ids.append(item[0])        
            #_logger.info("Group Ids result => %s " % (grp_ids))

            self.cust_group_id = 0
            self.cust_jalur_id = 0

            return {'domain': {'cust_group_id': [('id', 'in', grp_ids)]}}        

    #@api.onchange('cust_group_id')
    #def onchange_cust_group_id(self):

    #    if self.cust_group_id:
    #        #select custom_group_id from Customer
    #        sql = """ 
    #            SELECT DISTINCT custom_jalur_id
    #            FROM res_partner
    #            WHERE active 
    #                AND custom_div_id = %s 
    #                AND custom_group_id = %s 
    #            """ % (str(self.cust_div_id.id),str(self.cust_group_id.id))
    #        self._cr.execute(sql)
    #        fall = self._cr.fetchall()

    #        jlr_ids = []
    #        for item in fall:
    #            jlr_ids.append(item[0])        
            #_logger.info("Jalur Ids result => %s " % (jlr_ids))

    #        self.cust_jalur_id = 0

    #        return {'domain': {'cust_jalur_id': [('id', 'in', jlr_ids)]}}        


    transaction_date = fields.Date(string="Date", required="1", default=fields.Date.today)
    transaction_type = fields.Selection([('mt','MT'),('gt','GT'),('po','PO'),('ro','RO'),('to','TO')], default="mt", required="1", string="Type")
    cust_acc_id = fields.Selection([('indomaret','Indomaret'),
									('alfagroup','Alfa Group'),
									('lainnya','Lainnya')
                                ], string="Account", required="1")
    cust_div_id = fields.Many2one('res.partner.divisi', string="Division" )
    cust_group_id = fields.Many2one('res.partner.group', string="Group" )
    cust_jalur_id = fields.Many2one('res.partner.jalur', string="Route" )
    cust_cluster_id = fields.Many2one('res.partner.cluster', string="Cluster" )
    target_delivered_date = fields.Date(string="Delivery", required="1", default=fields.Date.today )
    jwk = fields.Char(string="JWK", compute="_compute_date", store="1" )
    estimate_template = fields.Selection([('indomaret','Indomaret'),('alfamart','Alfamart'),('lainnya','Lainnya')], string="Template", required="1")
    default_ord_qty = fields.Boolean(string="Compute to Qty Default", default=False )

    def generate(self):
        for me in self:

            vupdate_estimate = 0
            start_time = datetime.now()

            if me.target_delivered_date <= me.transaction_date:
                raise ValidationError("ValidationError: Target Delivary Date")

            #select from Customer
            if me.cust_acc_id == 'lainnya':
                sql = """ 
                        SELECT  id,kode_customer,kext_customer,city,custom_div_id,custom_group_id,cluster_id
                        FROM    res_partner
                        WHERE   active
                    """
            else:
                sql = """ 
                        SELECT  id,kode_customer,kext_customer,city,custom_div_id,custom_group_id,cluster_id
                        FROM    res_partner
                        WHERE   active
                                AND custom_acc_id = '%s'
                    """ % (str(me.cust_acc_id))

            if me.cust_div_id:
                sql = sql + "AND custom_div_id = %s " % (str(me.cust_div_id.id))

            if me.cust_group_id:
                sql = sql + "AND custom_group_id = %s " % (str(me.cust_group_id.id))

            if me.cust_cluster_id:
                sql = sql + "AND cluster_id = %s " % (str(me.cust_cluster_id.id))

            sql = sql + "ORDER BY custom_div_id,custom_group_id"
            #_logger.info("Customer query = %s " % (sql))

            me._cr.execute(sql)
            list_customers = me._cr.fetchall()
            #_logger.info("Customer result => %s " % (list_customers))

            if not list_customers:
                raise ValidationError("No Data Match with Partner Filter")

            year, week_num, day_of_week = me.target_delivered_date.isocalendar()

            for cust in list_customers:

                cust[0]
                cust[1]
                cust[2]
                cust[3]

                vcust_div     = 0
                vcust_group   = 0
                vcust_cluster = 0

                if cust[4]:
                    vcust_div       = cust[4]

                if cust[5]:
                    vcust_group     = cust[5]

                if cust[6]:
                    vcust_cluster   = cust[6]

                #delete Old Estimate
                sql = """ 
                    DELETE FROM estimate
                    WHERE   template = '%s'
                            AND estimate_date = '%s'
                            AND estimate_type = '%s'
                            AND customer_id = '%s'
                            AND commitment_date = '%s'
                    """ % (str(me.estimate_template.upper()),str(me.transaction_date.strftime('%Y-%m-%d')),str(me.transaction_type),str(cust[0]),str(me.target_delivered_date.strftime('%Y-%m-%d')))
                me._cr.execute(sql)
                #_logger.info("delete Old Estimate = %s " % (sql))

                #check JWK
                #if cust[2]:

                if me.cust_jalur_id:
                    sql = """ 
                        SELECT  id,jalur_id
                        FROM    res_partner_jalur_line
                        WHERE   active
                                AND jwk='%s'
                                AND jalur_line_id=%s
                                AND jalur_id=%s
                        """ % (str(day_of_week),str(cust[0]),str(me.cust_jalur_id.id))
                else:
                    sql = """ 
                        SELECT  id,jalur_id
                        FROM    res_partner_jalur_line
                        WHERE   active
                                AND jwk='%s'
                                AND jalur_line_id=%s
                        """ % (str(day_of_week),str(cust[0]))

                #_logger.info("JWK query = %s " % (sql))
                me._cr.execute(sql)
                result = me._cr.fetchall()

                #else:
                #    result = False
                    
                if result:

                    #_logger.info("JWK Result = %s " % (result))
                    if me.cust_jalur_id:
                        vcust_jalur_id = me.cust_jalur_id.id
                    else:
                        vcust_jalur_id = result[0][1]

                    #_logger.info("JWK result => %s " % (result))

                    #check Registered Product
                    sql = """ 
                        SELECT  id,cust_int_code,prod_int_code,ext_code,ord_qty,min_qty,max_qty
                        FROM    res_partner_product
                        WHERE   product_active
                                AND customer_id=%s
                        """ % (str(cust[0]))
                    #_logger.info("res_partner_product query = %s " % (sql))

                    me._cr.execute(sql)
                    partner_product = me._cr.fetchall()
                    #_logger.info("res_partner_product result => %s " % (partner_product))

                    for pprd in partner_product:

                        pprd[0]
                        pprd[2]

                        vres_partner_product_ord_qty = pprd[4] if pprd[4] else 0
                        vres_partner_product_min_qty = pprd[5] if pprd[5] else 0
                        vres_partner_product_max_qty = pprd[6] if pprd[6] else 0

                        sql = """ 
                            SELECT  id,cust_int_id,prod_int_id,template
                            FROM    sellingout
                            WHERE   state IN ('confirm')
                                    AND selling_date <= '%s'
                                    AND UPPER(cust_int_id) = '%s'
                                    AND UPPER(prod_int_id) = '%s'
                            """ % (str(me.transaction_date.strftime('%Y-%m-%d')),str(pprd[1]).upper(),str(pprd[2]).upper())
                        sql = sql + "ORDER BY cust_int_id,prod_int_id,selling_date"
                        #_logger.info("Sellingout query = %s " % (sql))

                        me._cr.execute(sql)
                        result = me._cr.fetchall()

                        if result:
                            #_logger.info("Sellingout result => %s " % (result))

                            vcust_prod_id = 'anantari'
                            for item in result:

                                vcust_int_id = item[1]
                                vprod_int_id = item[2]

                                vhistory_w01 = 0
                                vhistory_w02 = 0
                                vhistory_w03 = 0
                                vhistory_w04 = 0

                                vtemplate    = item[3].upper()
                                vesttemplate = me.estimate_template.upper()
                                if vesttemplate == 'LAINNYA':
                                    if vtemplate not in ['INDOMARET','ALFAMART']:
                                        vtemplate = 'LAINNYA'
                                #_logger.info("template ==> %s " % (vtemplate))

                                if (vcust_prod_id != vcust_int_id+vprod_int_id):

                                    vmaximum_stock = 0
                                    vlast_stock    = 0
                                    vlast_ord_qty  = 0 

                                    vcust_prod_id = vcust_int_id+vprod_int_id
                                    #_logger.info("item ==> %s " % (vcust_prod_id))

                                    customer = me.env['res.partner'].search([
                                        ('kode_customer','=', vcust_int_id)
                                    ], limit=1)
                                    if customer:

                                        #_logger.info("customer ==> %s " % (customer.id))

                                        prod_template = me.env['product.template'].search([
                                            ('default_code','=', vprod_int_id)
                                        ], limit=1)
                                        if prod_template:

                                            #_logger.info("customer ==> %s " % (prod_template.id))

                                            product = me.env['product.product'].search([
                                                ('product_tmpl_id','=', prod_template.id)
                                            ], limit=1)

                                            if me.cust_cluster_id:
                                                me.cust_cluster_id.id
                                            else:
                                                customer.cluster_id.id or False

                                            #check last order qty
                                            if me.estimate_template == 'indomaret':
                                                sql = """ 
                                                    SELECT  id,selling_date,maximum_qty,stock_qty,selling_qty
                                                    FROM    sellingout
                                                    WHERE   state IN ('confirm')
                                                            AND template = 'INDOMARET'
                                                            AND selling_date <= '%s'
                                                            AND cust_int_id = '%s'
                                                            AND prod_int_id = '%s'
                                                    ORDER BY selling_date DESC
                                                    LIMIT 1
                                                    """ % (str(me.transaction_date.strftime('%Y-%m-%d')),str(vcust_int_id),str(vprod_int_id))
                                            else:
                                                sql = """ 
                                                    SELECT  id,selling_date,maximum_qty,stock_qty,selling_qty
                                                    FROM    sellingout
                                                    WHERE   state IN ('confirm')
                                                            AND selling_date <= '%s'
                                                            AND cust_int_id = '%s'
                                                            AND prod_int_id = '%s'
                                                    ORDER BY selling_date DESC
                                                    LIMIT 1
                                                    """ % (str(me.transaction_date.strftime('%Y-%m-%d')),str(vcust_int_id),str(vprod_int_id))

                                            #_logger.info("last_order_qty ==> %s " % (sql))
                                            me._cr.execute(sql)
                                            rslt = me._cr.fetchall()
                                            if rslt:

                                                _logger.info("last_order_qty ===> %s " % (rslt))
                                                rslt[0][1]
                                                if rslt[0][2] is None:
                                                    vmaximum_stock  = 0
                                                else:
                                                    vmaximum_stock  = max(0,rslt[0][2])

                                                if rslt[0][3] is None:
                                                    vlast_stock     = 0
                                                else:
                                                    vlast_stock     = max(0,rslt[0][3])

                                                if rslt[0][4] is None:
                                                    vlast_ord_qty   = 0
                                                else:
                                                    vlast_ord_qty   = max(0,rslt[0][4]) 

                                            else:

                                                me.transaction_date
                                                vmaximum_stock = 0
                                                vlast_stock    = 0
                                                vlast_ord_qty  = 0 

                                            if me.default_ord_qty:

                                                #default order qty
                                                if vres_partner_product_ord_qty:
                                                    vhistory_qty = vres_partner_product_ord_qty
                                                else:
                                                    if vres_partner_product_max_qty:
                                                        vhistory_qty = vres_partner_product_max_qty
                                                    else:
                                                        if vres_partner_product_min_qty:
                                                            vhistory_qty = vres_partner_product_min_qty
                                                        else:
                                                            vhistory_qty = 0

                                            else:

                                                #history order qty
                                                vhistory_qty = 0
                                                if me.estimate_template == 'indomaret':

                                                    #Request Pak Theo - 2020-06-13
                                                    #bila stok 0 dan sales 0, jangan dihitung -> order = 0
                                                    if (vlast_stock == 0) and (vlast_ord_qty == 0):
                                                        vhistory_qty = 0
                                                        vres_partner_product_min_qty = 0
                                                        
                                                    else:

                                                        #Request Pak Theo - 2020-05-18
                                                        #SELLING - STOCK
                                                        #6 - 4
                                                        vhistory_qty = vlast_ord_qty-vlast_stock

                                                        #JIKA HASIL ESTIMASINYA MINUS SAMPAI 4 pcs, SALES YANG ADA DI BAGI 2
                                                        if vhistory_qty <= 4:
                                                            vhistory_qty = vlast_ord_qty /2

                                                        else:

                                                            #DARI HASIL AKHIR ESTIMASI, TIDAK BOLEH MELEBIHI PKM (MAKSIMUM STOCK), SEHINGGA OTOMATIS AKAN DI SESUAIKAN, ESTIMASI + STOCK HARUS DIBAWAH ATAU SAMA DENGAN PKM
                                                            if (vhistory_qty +vlast_stock) > vmaximum_stock:
                                                                vhistory_qty = vmaximum_stock -vlast_stock

                                                        #DI SETIAP ESTIMASI FINAL MINIMUM ESTIMASI 4 PCS
                                                        vhistory_qty = max(4,math.ceil(vhistory_qty))
                                                        vhistory_qty = min(vmaximum_stock,vhistory_qty)

                                                else:
                                                    #penjualan rata-2 dalam 4 minggu

                                                    #minggu -1
                                                    sql = """ 
                                                        SELECT id,to_char(selling_date, 'IYYY-IW') week,maximum_qty,stock_qty,selling_qty
                                                        FROM sellingout
                                                        WHERE state IN ('confirm')
                                                                AND to_char(selling_date, 'IYYY-IW') = to_char(date_trunc('week', to_date('%s','YYYY-MM-DD'))::date -14, 'IYYY-IW')
                                                                AND UPPER(cust_int_id) = '%s'
                                                                AND UPPER(prod_int_id) = '%s'
                                                        """ % (str(me.transaction_date.strftime('%Y-%m-%d')),str(vcust_int_id),str(vprod_int_id))

                                                    #_logger.info("LAINNYA history_order_qty W-1 ==> %s " % (sql))
                                                    me._cr.execute(sql)
                                                    rslt = me._cr.fetchall()
                                                    if rslt:

                                                        #_logger.info("LAINNYA history_order_qty W-1 ===> %s " % (rslt))
                                                        vtotal = 0
                                                        for data in rslt:
                                                            vtotal += data[4]

                                                        vweek01 = vtotal
                                                    else: 
                                                        vweek01 = 0

                                                    #minggu -2
                                                    sql = """ 
                                                        SELECT id,to_char(selling_date, 'IYYY-IW') week,maximum_qty,stock_qty,selling_qty
                                                        FROM sellingout
                                                        WHERE state IN ('confirm')
                                                                AND to_char(selling_date, 'IYYY-IW') = to_char(date_trunc('week', to_date('%s','YYYY-MM-DD'))::date -21, 'IYYY-IW')
                                                                AND UPPER(cust_int_id) = '%s'
                                                                AND UPPER(prod_int_id) = '%s'
                                                        """ % (str(me.transaction_date.strftime('%Y-%m-%d')),str(vcust_int_id),str(vprod_int_id))

                                                    #_logger.info("LAINNYA history_order_qty W-2 ==> %s " % (sql))
                                                    me._cr.execute(sql)
                                                    rslt = me._cr.fetchall()
                                                    if rslt:

                                                        #_logger.info("LAINNYA history_order_qty W-2 ===> %s " % (rslt))
                                                        vtotal = 0
                                                        for data in rslt:
                                                            vtotal += data[4]

                                                        vweek02 = vtotal
                                                    else: 
                                                        vweek02 = 0

                                                    #minggu -3
                                                    sql = """ 
                                                        SELECT id,to_char(selling_date, 'IYYY-IW') week,maximum_qty,stock_qty,selling_qty
                                                        FROM sellingout
                                                        WHERE state IN ('confirm')
                                                                AND to_char(selling_date, 'IYYY-IW') = to_char(date_trunc('week', to_date('%s','YYYY-MM-DD'))::date -28, 'IYYY-IW')
                                                                AND UPPER(cust_int_id) = '%s'
                                                                AND UPPER(prod_int_id) = '%s'
                                                        """ % (str(me.transaction_date.strftime('%Y-%m-%d')),str(vcust_int_id),str(vprod_int_id))

                                                    #_logger.info("LAINNYA history_order_qty W-3 ==> %s " % (sql))
                                                    me._cr.execute(sql)
                                                    rslt = me._cr.fetchall()
                                                    if rslt:

                                                        #_logger.info("LAINNYA history_order_qty W-3 ===> %s " % (rslt))
                                                        vtotal = 0
                                                        for data in rslt:
                                                            vtotal += data[4]

                                                        vweek03 = vtotal
                                                    else: 
                                                        vweek03 = 0

                                                    #minggu -4
                                                    sql = """ 
                                                        SELECT id,to_char(selling_date, 'IYYY-IW') week,maximum_qty,stock_qty,selling_qty
                                                        FROM sellingout
                                                        WHERE state IN ('confirm')
                                                                AND to_char(selling_date, 'IYYY-IW') = to_char(date_trunc('week', to_date('%s','YYYY-MM-DD'))::date -35, 'IYYY-IW')
                                                                AND UPPER(cust_int_id) = '%s'
                                                                AND UPPER(prod_int_id) = '%s'
                                                        """ % (str(me.transaction_date.strftime('%Y-%m-%d')),str(vcust_int_id),str(vprod_int_id))

                                                    #_logger.info("LAINNYA history_order_qty W-4 ==> %s " % (sql))
                                                    me._cr.execute(sql)
                                                    rslt = me._cr.fetchall()
                                                    if rslt:

                                                        #_logger.info("LAINNYA history_order_qty W-4 ===> %s " % (rslt))
                                                        vtotal = 0
                                                        for data in rslt:
                                                            vtotal += data[4]

                                                        vweek04 = vtotal
                                                    else: 
                                                        vweek04 = 0

                                                    #hitung rata-rata penjualan perminggu
                                                    vdivision = 0
                                                    if vweek01 > 0:
                                                        vhistory_w01 = vweek01
                                                        vdivision += 1
                                                    if vweek02 > 0:
                                                        vhistory_w02 = vweek02
                                                        vdivision += 1
                                                    if vweek03 > 0:
                                                        vhistory_w03 = vweek03
                                                        vdivision += 1
                                                    if vweek04 > 0:
                                                        vhistory_w04 = vweek04
                                                        vdivision += 1

                                                    if vdivision > 0:
                                                        vhistory_qty = (vweek01+vweek02+vweek03+vweek04)/vdivision
                                                        vhistory_qty = max(vres_partner_product_min_qty,vhistory_qty)
                                                        vhistory_qty = min(vres_partner_product_max_qty,vhistory_qty)

                                                    else:
                                                        vhistory_qty = 0


                                            vhistory_qty = math.ceil(vhistory_qty)
                                            vproduct_qty = vhistory_qty
                                            vlist_price  = product.list_price

                                            estimate_vals = {
                                                            'estimate_type': me.transaction_type,
                                                            'estimate_date': me.transaction_date,
                                                            'template': me.estimate_template.upper(),
                                                            'commitment_date': me.target_delivered_date,
                                                            'customer_id': customer.id or False,
                                                            'cust_int_cd': customer.kode_customer or '',
                                                            'cust_ext_cd': customer.kext_customer or '',
                                                            'city': customer.city or '',
                                                            'account_id': me.cust_acc_id,
                                                            'divisi_id': vcust_div or False,
                                                            'group_id': vcust_group or False,
                                                            'route_id': vcust_jalur_id or False,
                                                            'route_jwk': me.jwk,
                                                            'cluster_id': vcust_cluster or False,
                                                            'product_id': product.id or False,
                                                            'prod_int_cd': product.default_code or '',
                                                            #'prod_ext_cd': product.external_reference or '',
                                                            'last_order_qty': vlast_ord_qty,
                                                            'history_qty': vhistory_qty,
                                                            'product_qty': vproduct_qty,
                                                            'product_uom_id': product.uom_id.id or False,
                                                            'price': vlist_price,
                                                            'subtotal': vproduct_qty*vlist_price,
                                                            'user_id': self.env.uid,
                                                            'sellingout_qty': vlast_ord_qty,
                                                            'sellingout_stock': vlast_stock,
                                                            'sellingout_pkm': vmaximum_stock,
                                                            'history_w01': vhistory_w01,
                                                            'history_w02': vhistory_w02,
                                                            'history_w03': vhistory_w03,
                                                            'history_w04': vhistory_w04,
                                            }

                                            estimate = me.env['estimate'].search([  '&','&',
                                                                                    ('commitment_date','=', me.target_delivered_date),
                                                                                    ('customer_id','=', customer.id),
                                                                                    ('product_id','=', product.id)
                                                                                ], limit=1)
                                            if estimate:
                                                vupdate_estimate = vupdate_estimate +1
                                                estimate.write(estimate_vals)
                                            else:

                                                _logger.info("Vals ==> %s " % (estimate_vals))
                                                self.env['estimate'].create(estimate_vals)

                                            #vBatch_Counter += 1
                                            #if vBatch_Counter > vBatch_Limit:
                                            #    vBatch_Counter = 0
                                            #    self.env.cr.commit()


            finish_time = datetime.now()
            _logger.info("Generate -> %s (updated: %s)" % ((finish_time-start_time),vupdate_estimate))
