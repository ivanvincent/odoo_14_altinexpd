from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
import requests
import logging
_logger = logging.getLogger(__name__)
import pytz
import json
from pytz import timezone
from dateutil.relativedelta import relativedelta
import datetime
from datetime import datetime, timedelta
import string
import xlrd
import base64
from odoo.exceptions import Warning


class SellingOut(models.Model):
    _name = 'sellingout'
    _description = 'Sellingout'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]
    _order = 'selling_date DESC, id DESC'
    _rec_name = "customer_nm"

    STATE = [('draft','Draft'),
             ('confirm','Confirm'),
             ('cancel','Cancelled')]

    state = fields.Selection(STATE, string="State", default="confirm", track_visibility="onchange")
    name = fields.Char(readonly="1")
    selling_date = fields.Date(string="Selling Date")
    week = fields.Char(string="Week")
    template = fields.Char(string="Template")
    cust_int_id = fields.Char(string="Cust.(Int)")
    customer_nm = fields.Char(string="Customer")
    cust_ext_id = fields.Char(string="Cust.(Ext)")
    group_nm = fields.Char(string="Group" )
    jalur_nm = fields.Char(string="Route" )
    cluster_nm = fields.Char(string="Cluster" )
    prod_int_id = fields.Char(string="Prod.(Int)")
    product_nm = fields.Char(string="Product")
    prod_ext_id = fields.Char(string="Prod.(Ext)")
    maximum_qty = fields.Float(string="Max.Stock")
    stock_qty = fields.Float(string="Stock")
    selling_qty = fields.Float(string="Selling", track_visibility="onchange")
    return_qty = fields.Float(string="Qty. Return")
    remark = fields.Text(string="Remark")
    on_generator = fields.Boolean(string="Process in SO Generator", default=False)
    user_id = fields.Many2one('res.users', string="Uploader", default=lambda self: self.env.uid )

    def get_sequence(self):
        pref = '%(y)s/SLS/%(month)s/'
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', 'SellingOut Data'),
            ('code', '=', 'sellingout'),
            ('prefix', '=', pref),
        ], limit=1)
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': 'SellingOut Data',
                'code': 'sellingout',
                'implementation': 'standard',
                'prefix': pref,
                'padding': 6,
            })
        return sequence_id.next_by_id() 

    #@api.model
    #def create(self, vals):
    #    vals['name'] = self.get_sequence()
    #    return super(SellingOut, self).create(vals)

    def unlink(self):
        for obj in self:
            if obj.state != 'draft':
                raise Warning('Delete not allowed !')
        return super(SellingOut, self).unlink()

    def action_confirm(self):
        for me in self:
            me.write({
                'state': 'confirm'
            })

    def action_todraft(self):
        for me in self:
            me.write({
                'state': 'draft'
            })

    def action_cancel(self):
        for me in self:
            me.write({
                'state': 'cancel'
            })

    
class SellingoutXLS(models.TransientModel):
    _name = 'sellingout.xls'
    _description = 'Sellingout Import'

    template = fields.Selection([('indomaret','Indomaret'),('alfamart','Alfamart'),('lainnya','Lainnya')], default="indomaret", string="Template")
    xls_file = fields.Binary("Upload File (*.XLS)", required=True, filter='*.xls' )
    batch_limit = fields.Integer("Batch Limit", default=2000, required=True )

    def upload_xls_file(self):

        vTemplate   = self.template.upper()
        wbook       = xlrd.open_workbook(file_contents=base64.decodestring(self.xls_file))

        vSheet  = ""
        for sheet in wbook.sheets():
            if sheet.name.lower() == "sharon":
                vSheet = sheet.name

        if vSheet == "":
            raise ValidationError("Template Sheet not found")
 
        sheet = wbook.sheet_by_name(vSheet)

        start_time = datetime.now()
        _logger.info('upload_xls_file')

        if vTemplate == "INDOMARET":
            sql = "DELETE FROM sellingout WHERE template = 'INDOMARET'"
            self._cr.execute(sql)

        oldCust_Code = "zanit"
        oldProd_Code = "naren"

        xbatch_limit = self.batch_limit

        vListValues = []
        vbatch_limit = 1

        xsheet_rows = sheet.nrows-1
        for i in range(sheet.nrows):
            rows = sheet.row(i)

            if i > 0:

                vDate	        = str(rows[0].value)
                vWeek           = datetime.strptime(vDate, '%Y-%m-%d').date().strftime("%V")

                vPartner_Code	= str(rows[1].value)
                if ".0" in vPartner_Code:
                    vPartner_Code = vPartner_Code.split('.')[0]

                vPartner_Ext	= str(rows[2].value)
                vPartner_Name	= str(rows[3].value).strip()
                vProduct_Code	= str(rows[4].value)
                vProduct_Ext    = str(rows[5].value)
                vProduct_Name   = str(rows[6].value).strip()
                if not rows[7].value:
                    vStock = 0
                else:
                    vStock      = int(rows[7].value)
                if not rows[8].value:
                    vQuantity = 0
                else:
                    vQuantity   = int(rows[8].value)

                if not rows[9].value:
                    vMax_Stock = 0
                else:
                    vMax_Stock  = int(rows[9].value)

                vbatch_limit += 1
                if oldCust_Code != vPartner_Code:
                    oldCust_Code = vPartner_Code

                    #Search Partner
                    sql = """ 
                        SELECT  id,kext_customer
                        FROM    res_partner
                        WHERE   active AND kode_customer='%s'
                        """ % (vPartner_Code)
                    self._cr.execute(sql)
                    rslt = self._cr.fetchall()

                    if not rslt:
                        _logger.info('Customer Not Found: %s', vPartner_Code )
                        #raise ValidationError("Customer [%s] not found" % (vPartner_Code) )

                    else:

                        if (vPartner_Ext != "") and (rslt[0][1] != vPartner_Ext):
                            sql = """ 
                                UPDATE  res_partner
                                SET     kext_customer='%s'
                                WHERE   active AND kode_customer='%s'
                                """ % (vPartner_Ext,vPartner_Code)
                            self._cr.execute(sql)

                if oldProd_Code != vProduct_Code:
                    oldProd_Code = vProduct_Code

                    #Search Product
                    sql = """ 
                        SELECT  id
                        FROM    product_template
                        WHERE   active AND default_code='%s'
                        """ % (vProduct_Code)
                    self._cr.execute(sql)
                    rslt = self._cr.fetchall()
                    
                    if not rslt:
                        _logger.info('Product Not Found: %s', vProduct_Code )
                        #raise ValidationError("Product [%s] not found" % (vProduct_Code) )

                    #Search Product
                    #vProduct_ID = self.env['product.product'].search([('default_code', '=', vProduct_Code)], limit=1)
                    #if not vProduct_ID:

                        #_logger.info('create Product: %s', vProduct_Name )
                        #vals = {    'name'          : vProduct_Name,
                        #            'default_code'  : vProduct_Code,
                        #            'sale_ok'       : 1,
                        #        }
                        #self.env['res.partner'].create(vals)
                        #vProduct_ID = self.env['product.product'].search([('default_code', '=', vProduct_Code)], limit=1)

                vListValues.append((
                                    vDate,
                                    'W' + vWeek,
                                    vTemplate,
                                    vPartner_Code,
                                    vPartner_Name,
                                    vPartner_Ext,
                                    vProduct_Code,
                                    vProduct_Name,
                                    vProduct_Ext,
                                    vMax_Stock,
                                    vStock,
                                    vQuantity,
                                    'confirm'))

                if (vbatch_limit > xbatch_limit) or (i == xsheet_rows):

                    sql = """ 
                        INSERT INTO sellingout( selling_date,
                                                week,
                                                template,
                                                cust_int_id,
                                                customer_nm,
                                                cust_ext_id,
                                                prod_int_id,
                                                product_nm,
                                                prod_ext_id,
                                                maximum_qty,
                                                stock_qty,
                                                selling_qty,
                                                state)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """ 
                    self._cr.executemany(sql,vListValues)

                    vListValues = []
                    vbatch_limit = 1


        if vListValues:
            sql = """ 
                INSERT INTO sellingout( selling_date,
                                        week,
                                        template,
                                        cust_int_id,
                                        customer_nm,
                                        cust_ext_id,
                                        prod_int_id,
                                        product_nm,
                                        prod_ext_id,
                                        maximum_qty,
                                        stock_qty,
                                        selling_qty,
                                        state)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """ 
            #self._cr.executemany(sql,vListValues)

        finish_time = datetime.now()
        _logger.info("upload_xls_file Selesai [%s]" % ((finish_time-start_time)))
