from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
import pytz
from pytz import timezone
from dateutil.relativedelta import relativedelta

import datetime
from datetime import datetime

import itertools

import base64
import xlrd

import logging
_logger = logging.getLogger(__name__)

class EstimateUploaderWizard(models.TransientModel):
    _name = 'estimate.uploader.wizard'
    _description = 'Estimate Uploader Wizard'

    state_type = fields.Selection([('draft','Draft'),('confirm','Confirm')], default="draft", string="State Type")
    xls_file = fields.Binary("Upload File (*.XLS)", required=True, filter='*.xls' )
    batch_limit = fields.Integer("Batch Limit", default=2048, required=True )

    def upload_xls_file(self):

        start_time = datetime.now()

        vState  = self.state_type
        wbook   = xlrd.open_workbook(file_contents=base64.decodestring(self.xls_file))

        vSheet  = ""
        for sheet in wbook.sheets():
            if sheet.name.lower() == "estimate":
                vSheet = sheet.name

        if vSheet == "":
            raise ValidationError("Template Sheet not found")
 
        sheet1 = wbook.sheet_by_name(vSheet)
        sheet2 = wbook.sheet_by_name(vSheet)

        #Check Customer, Division, Group, Route, Product 
        oPartner_Cd  = "@"
        oDivision_Cd = "@"
        oGroup_Cd    = "@"
        oRoute_Cd    = "@"
        
        i = 0
        for i in range(sheet1.nrows):
            row = sheet1.row(i)
            if i > 6:

                vPartner_Cd  = str(row[0].value)
                if ".0" in vPartner_Cd:
                    vPartner_Cd = vPartner_Cd.split('.')[0]
               
                vDivision_Cd = str(row[3].value).strip()
                vGroup_Cd    = str(row[4].value).strip()
                vRoute_Cd    = str(row[5].value).strip()

                if oPartner_Cd != vPartner_Cd:
                    oPartner_Cd = vPartner_Cd

                    #Search Partner
                    sql = """ 
                        SELECT  id,kext_customer,street,city
                        FROM    res_partner
                        WHERE   active AND kode_customer='%s'
                        """ % (oPartner_Cd)
                    self._cr.execute(sql)
                    rslt = self._cr.fetchall()
                    if not rslt:
                        raise ValidationError("Customer [%s] not found" % (oPartner_Cd) )

                if oDivision_Cd != vDivision_Cd:
                    oDivision_Cd = vDivision_Cd

                    #Search Division
                    sql = """ 
                        SELECT  id
                        FROM    res_partner_divisi
                        WHERE   TRIM(code)='%s'
                        """ % (oDivision_Cd)
                    self._cr.execute(sql)
                    rslt = self._cr.fetchall()
                    if not rslt:

                        sql = """ 
                            SELECT  id
                            FROM    res_partner_divisi
                            WHERE   LOWER(TRIM(name))='%s'
                            """ % (oDivision_Cd.lower())
                        self._cr.execute(sql)
                        rslt = self._cr.fetchall()
                        if not rslt:
                            raise ValidationError("Division [%s] not found" % (oDivision_Cd) )

                if oGroup_Cd != vGroup_Cd:
                    oGroup_Cd = vGroup_Cd

                    #Search Group
                    sql = """ 
                        SELECT  id
                        FROM    res_partner_group
                        WHERE   TRIM(code)='%s'
                        """ % (oGroup_Cd)
                    self._cr.execute(sql)
                    rslt = self._cr.fetchall()
                    if not rslt:

                        sql = """ 
                            SELECT  id
                            FROM    res_partner_group
                            WHERE   LOWER(TRIM(name))='%s'
                            """ % (oGroup_Cd.lower())
                        self._cr.execute(sql)
                        rslt = self._cr.fetchall()
                        if not rslt:
                            raise ValidationError("Group [%s] not found" % (oGroup_Cd) )

                if oRoute_Cd != vRoute_Cd:
                    oRoute_Cd = vRoute_Cd

                    #Search Group
                    sql = """ 
                        SELECT  id
                        FROM    res_partner_jalur
                        WHERE   TRIM(code)='%s'
                        """ % (oRoute_Cd)
                    self._cr.execute(sql)
                    rslt = self._cr.fetchall()
                    if not rslt:

                        sql = """ 
                            SELECT  id
                            FROM    res_partner_jalur
                            WHERE   LOWER(TRIM(name))='%s'
                            """ % (oRoute_Cd.lower())
                        self._cr.execute(sql)
                        rslt = self._cr.fetchall()
                        if not rslt:
                            raise ValidationError("Route [%s] not found" % (oRoute_Cd) )


        oPartner_Cd  = "@"
        oDivision_Cd = "@"
        oGroup_Cd    = "@"
        oRoute_Cd    = "@"
        oProduct_Cd  = "@"

        vEst_Date    = ""
        vEst_Type    = ""
        vDlv_Date    = ""
        vAcc_Cust    = ""
        vEstimator   = ""
        vPartner_ID  = 0
        vDivision_ID = 0
        vGroup_ID    = 0
        vRoute_ID    = 0
        vProduct_ID  = 0
        vProduct_Uom = 0

        vAddress     = ""
        vCity        = ""
        vRoute_JWK   = ""

        i = 0
        for i in range(sheet2.nrows):

            row = sheet2.row(i)
            if i == 1:

                vEst_Date  = str(row[1].value)
                try:
                    #_logger.info(vEst_Date)
                    datetime.strptime(vEst_Date, '%Y-%m-%d')
                except ValueError:
                    raise ValueError("Incorrect Estimate Date format, should be YYYY-MM-DD")                

            elif i == 2:

                vEst_Type  = str(row[1].value).upper()
                #_logger.info(vEst_Type)
                if not vEst_Type in ['MT','GT','PO','RO','TO']:
                    raise ValidationError("Estimate Type [%s] not accepted" % (vEst_Type))

            elif i == 3:

                vDlv_Date  = str(row[1].value)
                try:
                    #_logger.info(vDlv_Date)
                    xDlv_Date = datetime.strptime(vDlv_Date, '%Y-%m-%d')

                    year, week_num, day_of_week = xDlv_Date.isocalendar()
                    if day_of_week == 1:
                        vRoute_JWK = "Senin"
                    elif day_of_week == 2:
                        vRoute_JWK = "Selasa"
                    elif day_of_week == 3:
                        vRoute_JWK = "Rabu"
                    elif day_of_week == 4:
                        vRoute_JWK = "Kamis"
                    elif day_of_week == 5:
                        vRoute_JWK = "Jumat"
                    elif day_of_week == 6:
                        vRoute_JWK = "Sabtu"
                    elif day_of_week == 7:
                        vRoute_JWK = "Minggu"

                except ValueError:
                    raise ValueError("Incorrect Delivery Date format, should be YYYY-MM-DD")                

            elif i == 4:

                vAcc_Cust  = str(row[1].value.lower())
                #_logger.info(vAcc_Cust)
                if not vAcc_Cust in ['indomaret','alfagroup','lainnya']:
                    raise ValidationError("Customer Account [%s] not found" % (vEst_Type.upper()))

            elif i == 5:

                vEstimator = str(row[1].value).upper()
                sql = """ 
                    SELECT  user_id
                    FROM    hr_employee
                    WHERE   active
                            AND employee_id='%s'
                    """ % (vEstimator)
                self._cr.execute(sql)
                rslt = self._cr.fetchall()
                
                if rslt:
                    vEstimator = rslt[0][0]
                    #_logger.info(vEstimator)
                else:
                    raise ValidationError("Employee ID [%s] not found" % (vEstimator))

            elif i == 6:

                #delete Old Estimate
                sql = """ 
                    DELETE  FROM estimate
                    WHERE   (state != 'done')
                            AND estimate_date='%s'
                            AND estimate_type='%s' 
                            AND commitment_date='%s'
                            AND account_id='%s'
                            AND user_id=%s
                    """ % (vEst_Date,vEst_Type.lower(),vDlv_Date,vAcc_Cust,vEstimator)
                #_logger.info(sql)
                self._cr.execute(sql)

            elif i > 6:

                vPartner_Cd  = str(row[0].value)
                if ".0" in vPartner_Cd:
                    vPartner_Cd = vPartner_Cd.split('.')[0]
               
                vPartner_Ext = str(row[1].value).strip()
                vDivision_Cd = str(row[3].value).strip()
                vGroup_Cd    = str(row[4].value).strip()
                vRoute_Cd    = str(row[5].value).strip()
                vProduct_Cd  = str(row[6].value).strip()
                vProduct_Ext = str(row[7].value).strip()
                vQuantity    = int(row[9].value) if row[9].value else 0

                if oPartner_Cd != vPartner_Cd:
                    oPartner_Cd = vPartner_Cd

                    #Search Partner
                    sql = """ 
                        SELECT  id,kext_customer,street,city
                        FROM    res_partner
                        WHERE   active AND kode_customer='%s'
                        """ % (oPartner_Cd)
                    self._cr.execute(sql)
                    rslt = self._cr.fetchall()
                    if rslt:

                        vPartner_ID = rslt[0][0]
                        vKext_Cust  = rslt[0][1]
                        vAddress    = rslt[0][2]
                        vAddress = vAddress.replace("'"," ")
                        if vAddress is None:
                            vAddress = ""
                        vCity       = rslt[0][3]
                        if vCity is None:
                            vCity = ""

                        if vPartner_Ext != "" and vKext_Cust != "" and vKext_Cust != vPartner_Ext:
                            sql = """ 
                                UPDATE  res_partner
                                SET     kext_customer='%s'
                                WHERE   active AND kode_customer='%s'
                                """ % (vPartner_Ext,oPartner_Cd)
                            self._cr.execute(sql)

                    else:
                        raise ValidationError("Customer [%s] not found" % (oPartner_Cd) )

                if oDivision_Cd != vDivision_Cd:
                    oDivision_Cd = vDivision_Cd

                    #Search Division
                    sql = """ 
                        SELECT  id
                        FROM    res_partner_divisi
                        WHERE   TRIM(code)='%s'
                        """ % (oDivision_Cd)
                    self._cr.execute(sql)
                    rslt = self._cr.fetchall()
                    if rslt:
                        vDivision_ID = rslt[0][0]
                    else:

                        sql = """ 
                            SELECT  id
                            FROM    res_partner_divisi
                            WHERE   LOWER(TRIM(name))='%s'
                            """ % (oDivision_Cd.lower())
                        self._cr.execute(sql)
                        rslt = self._cr.fetchall()
                        if rslt:
                            vDivision_ID = rslt[0][0]
                        else:
                            raise ValidationError("Division [%s] not found" % (oDivision_Cd) )

                if oGroup_Cd != vGroup_Cd:
                    oGroup_Cd = vGroup_Cd

                    #Search Group
                    sql = """ 
                        SELECT  id
                        FROM    res_partner_group
                        WHERE   TRIM(code)='%s'
                        """ % (oGroup_Cd)
                    self._cr.execute(sql)
                    rslt = self._cr.fetchall()
                    if rslt:
                        vGroup_ID = rslt[0][0]
                    else:

                        sql = """ 
                            SELECT  id
                            FROM    res_partner_group
                            WHERE   LOWER(TRIM(name))='%s'
                            """ % (oGroup_Cd.lower())
                        self._cr.execute(sql)
                        rslt = self._cr.fetchall()
                        if rslt:
                            vGroup_ID = rslt[0][0]
                        else:
                            raise ValidationError("Group [%s] not found" % (oGroup_Cd) )

                if oRoute_Cd != vRoute_Cd:
                    oRoute_Cd = vRoute_Cd

                    #Search Group
                    sql = """ 
                        SELECT  id
                        FROM    res_partner_jalur
                        WHERE   TRIM(code)='%s'
                        """ % (oRoute_Cd)
                    self._cr.execute(sql)
                    rslt = self._cr.fetchall()
                    if rslt:
                        vRoute_ID = rslt[0][0]
                    else:

                        sql = """ 
                            SELECT  id
                            FROM    res_partner_jalur
                            WHERE   LOWER(TRIM(name))='%s'
                            """ % (oRoute_Cd.lower())
                        self._cr.execute(sql)
                        rslt = self._cr.fetchall()
                        if rslt:
                            vRoute_ID = rslt[0][0]
                        else:
                            raise ValidationError("Route [%s] not found" % (oRoute_Cd) )

                if oProduct_Cd != vProduct_Cd:
                    oProduct_Cd = vProduct_Cd

                    #Search Product
                    sql = """ 
                        SELECT  id,product_tmpl_id
                        FROM    product_product
                        WHERE   active AND default_code='%s'
                        """ % (oProduct_Cd)
                    self._cr.execute(sql)
                    rslt = self._cr.fetchall()
                    if rslt:

                        vProduct_ID  = rslt[0][0]
                        if rslt[0][1]:

                            vProduct_Tmpl = rslt[0][1]
                            sql = """ 
                                SELECT  uom_id
                                FROM    product_template
                                WHERE   active AND id=%s
                                """ % (vProduct_Tmpl)
                            self._cr.execute(sql)
                            rslt = self._cr.fetchall()
                            if rslt:
                                vProduct_Uom = rslt[0][0]
                            else:
                                vProduct_Uom = False

                        else:
                            vProduct_Uom = False

                    else:
                        raise ValidationError("Product [%s] not found" % (oProduct_Cd) )

                #Insert Estimate
                sql = """ 
                    INSERT INTO estimate( 
                            template,
                            estimate_date,
                            estimate_type,
                            commitment_date,
                            customer_id,
                            cust_int_cd,
                            cust_ext_cd,
                            address,
                            city,
                            account_id,
                            divisi_id,
                            group_id,
                            route_id,
                            route_jwk,
                            product_id,
                            prod_int_cd,
                            prod_ext_cd,
                            product_qty,
                            product_uom_id,
                            user_id,
                            state)
                    VALUES('%s','%s','%s','%s',%s,'%s','%s','%s','%s','%s',%s,%s,%s,'%s',%s,'%s','%s',%s,%s,%s,'%s')
                    """ % (vAcc_Cust.upper(),vEst_Date,vEst_Type.lower(),vDlv_Date,vPartner_ID,vPartner_Cd,vPartner_Ext,vAddress,vCity,vAcc_Cust,vDivision_ID,vGroup_ID,vRoute_ID,vRoute_JWK,vProduct_ID,vProduct_Cd,vProduct_Ext,vQuantity,vProduct_Uom,vEstimator,vState)
                #_logger.info(sql)
                self._cr.execute(sql)
 
        finish_time = datetime.now()
        _logger.info("Estimate Upload -> Complete [%s]" % ((finish_time-start_time)))

