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
import xlrd
import base64
from odoo.exceptions import Warning

class PartnerProductXLS(models.TransientModel):
    _name = 'res.partner.product.xls'
    _description = 'Customer Products Upload'

    action_type = fields.Selection([('update','Update'),('replace','Replace')], default="update", string="Action Type")
    xls_file = fields.Binary("Upload File (*.XLS)", required=True, filter='*.xls' )
    batch_limit = fields.Integer("Batch Limit", default=2000, required=True )

    def upload_xls_file(self):

        vAction = self.action_type.upper()
        wbook   = xlrd.open_workbook(file_contents=base64.decodestring(self.xls_file))
        vSheet  = ""
        for sheet in wbook.sheets():
            if sheet.name.lower() == "customer_products":
                vSheet = sheet.name

        if vSheet == "":
            raise ValidationError("Template Sheet not found")
 
        sheet = wbook.sheet_by_name(vSheet)

        start_time = datetime.now()
        _logger.info('upload_xls_file')

        oldCust_Code = "zanit"
        oldProd_Code = "naren"

        vPartner_ID = 0
        vProduct_ID = 0

        vCreate = 0
        vDelete = 0
        vWrite = 0

        vBatch_Counter = 0
        vBatch_Sequence = 0
        vBatch_Limit = self.batch_limit
        for i in range(sheet.nrows):

            row = sheet.row(i)
            if i > 0:

                vPartner_Code = str(row[0].value)
                if ".0" in vPartner_Code:
                    vPartner_Code = vPartner_Code.split('.')[0]

                if vPartner_Code > "":

                    vPartner_Kext = str(row[1].value)
                    vProduct_Code = str(row[3].value)
                    vSchedule     = str(row[5].value)
                    vActive       = int(row[6].value)
                    if vActive == 0:
                        vActive = False
                    else:
                        vActive = True
                    vOrderQty     = int(row[7].value)
                    vMinQuantity  = int(row[8].value)
                    vMaxQuantity  = int(row[9].value)

                    vSchedule = vSchedule.upper()[:3]
                    if vSchedule == "SEN":
                        vSchedule = "1"
                    elif vSchedule == "SEL":
                        vSchedule = "2"
                    elif vSchedule == "RAB":
                        vSchedule = "3"
                    elif vSchedule == "KAM":
                        vSchedule = "4"
                    elif vSchedule == "JUM":
                        vSchedule = "5"
                    elif vSchedule == "SAB":
                        vSchedule = "6"
                    elif vSchedule == "MIN":
                        vSchedule = "7"
                    else:
                        vSchedule = "0"

                    if oldProd_Code != vProduct_Code:
                        oldProd_Code = vProduct_Code

                        #Search Product
                        sql = """ 
                            SELECT  id
                            FROM    product_product
                            WHERE   active AND default_code='%s'
                            """ % (vProduct_Code)
                        #_logger.info(sql)

                        self._cr.execute(sql)
                        rslt = self._cr.fetchall()
                        
                        if not rslt:
                            raise ValidationError("Product [%s] not found" % (vProduct_Code) )
                        
                        else:
                            vProduct_ID = rslt[0][0]

                    if oldCust_Code != vPartner_Code:
                        oldCust_Code = vPartner_Code

                        #Search Partner
                        sql = """ 
                            SELECT  id,kext_customer
                            FROM    res_partner
                            WHERE   kode_customer='%s'
                            """ % (vPartner_Code)
                        #_logger.info(sql)
                        self._cr.execute(sql)
                        rslt = self._cr.fetchall()

                        if not rslt:
                            raise ValidationError("Customer [%s] not found" % (vPartner_Code) )

                        else:

                            vPartner_ID = rslt[0][0]

                            vKext_Cust = rslt[0][1]
                            if vPartner_Kext != "" and vPartner_Kext != vKext_Cust:
                                sql = """ 
                                        UPDATE  res_partner
                                        SET     kext_customer='%s'
                                        WHERE   kode_customer='%s'
                                    """ % (vPartner_Kext,vPartner_Code)
                                #_logger.info(sql)
                                self._cr.execute(sql)

                            if vAction == "REPLACE":
                                #Delete Customer Products
                                sql = """ 
                                    DELETE
                                    FROM    res_partner_product
                                    WHERE   customer_id=%s AND product_id=%s AND schedule='%s'
                                    """ % (vPartner_ID,vProduct_ID,vSchedule)
                                #_logger.info(sql)
                                self._cr.execute(sql)
                                vDelete += 1


                    vals = {
                            'customer_id': vPartner_ID,
                            'product_id': vProduct_ID,
                            'schedule': vSchedule,
                            'product_active': vActive,
                            'ord_qty': vOrderQty,
                            'min_qty': vMinQuantity,
                            'max_qty': vMaxQuantity,
                    }

                    if vAction == "REPLACE":

                        _logger.info("Create [%s]" % (vals))
                        self.env['res.partner.product'].create(vals)
                        vCreate += 1

                    else:

                        rslt = self.env['res.partner.product'].search([
                                                                        ('customer_id','=', vPartner_ID),
                                                                        ('product_id','=', vProduct_ID),
                                                                        ('schedule','=', vSchedule)
                                                                    ], limit=1)

                        if rslt:
                            _logger.info("Write [%s]" % (vals))
                            rslt.write(vals)
                            vWrite += 1


                        else:
                            self.env['res.partner.product'].create(vals)
                            vCreate += 1

                    vBatch_Sequence += 1
                    if vBatch_Sequence > vBatch_Limit:
                        vBatch_Counter += 1
                        _logger.info("COMMIT - Batch #%s" % (vBatch_Counter))
                        vBatch_Sequence = 0
                        #self.env.cr.commit()


        finish_time = datetime.now()
        _logger.info("upload_xls_file Selesai [%s] [C%s D%s W%s]" % ((finish_time-start_time),vCreate,vDelete,vWrite))


