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

class PartnerGroupingXLS(models.TransientModel):
    _name = 'res.partner.grouping.xls'
    _description = 'Customer Grouping Upload'

    action_type = fields.Selection([('update','Update'),('replace','Replace')], default="update", string="Action Type")
    xls_file = fields.Binary("Upload File (*.XLS)", required=True, filter='*.xls' )
    batch_limit = fields.Integer("Batch Limit", default=2000, required=True )

    def upload_xls_file(self):

        vAction = self.action_type.upper()
        wbook   = xlrd.open_workbook(file_contents=base64.decodestring(self.xls_file))
        vSheet  = ""
        for sheet in wbook.sheets():
            if sheet.name.lower() == "customer_grouping":
                vSheet = sheet.name

        if vSheet == "":
            raise ValidationError("Template Sheet not found")
 
        sheet = wbook.sheet_by_name(vSheet)

        start_time = datetime.now()
        _logger.info('upload_xls_file')

        oldCust_Int = "@"
        oldCust_Jlr = "@"
        oldCust_JWK = "@"
        oldCust_Div = "@"
        oldCust_Grp = "@"

        vPartner_Id  = 0
        vRoute_Id    = 0
        vJWK_Id      = ""
        vDivision_Id = 0
        vGroup_Id    = 0

        vBatch_Counter = 0
        vBatch_Sequence = 0
        vBatch_Limit = self.batch_limit
        for i in range(sheet.nrows):

            row = sheet.row(i)
            if i > 0:

                vCust_Acc = str(row[0].value).lower()
                vCust_Int = str(row[1].value)
                if ".0" in vCust_Int:
                    vCust_Int = vCust_Int.split('.')[0]

                if vCust_Int > "":

                    vCust_Ext = str(row[2].value)
                    vCust_Jlr = str(row[4].value)
                    vCust_JWK = str(row[6].value)
                    vCust_Div = str(row[7].value)
                    vCust_Grp = str(row[8].value)

                    if oldCust_Int != vCust_Int:
                        oldCust_Int = vCust_Int

                        #Search Partner
                        sql = """ 
                            SELECT  id,kext_customer,custom_acc_id,custom_div_id,custom_group_id
                            FROM    res_partner
                            WHERE   kode_customer='%s'
                            """ % (vCust_Int)
                        #_logger.info(sql)
                        self._cr.execute(sql)
                        rslt = self._cr.fetchall()

                        if not rslt:
                            raise ValidationError("Customer [%s] not found" % (vCust_Int) )

                        else:

                            vPartner_Id = rslt[0][0]

                            vExt_Cust = rslt[0][1]
                            vAcc_Cust = rslt[0][2]
                            vDiv_Cust = rslt[0][3]
                            vGrp_Cust = rslt[0][4]

                            if oldCust_Div != vCust_Div:
                                oldCust_Div = vCust_Div

                                #Search Division
                                sql = """ 
                                    SELECT  id
                                    FROM    res_partner_divisi
                                    WHERE   name='%s'
                                    """ % (vCust_Div)
                                #_logger.info(sql)

                                self._cr.execute(sql)
                                rslt = self._cr.fetchall()
                                
                                if not rslt:
                                    raise ValidationError("Division [%s] not found" % (vCust_Div) )
                                
                                else:
                                    vDivision_Id = rslt[0][0]


                            if oldCust_Grp != vCust_Grp:
                                oldCust_Grp = vCust_Grp

                                #Search Group
                                sql = """ 
                                    SELECT  id
                                    FROM    res_partner_group
                                    WHERE   name='%s'
                                    """ % (vCust_Grp)
                                #_logger.info(sql)

                                self._cr.execute(sql)
                                rslt = self._cr.fetchall()
                                
                                if not rslt:
                                    raise ValidationError("Group [%s] not found" % (vCust_Grp) )
                                
                                else:
                                    vGroup_Id = rslt[0][0]


                            if (vExt_Cust != vCust_Ext) or (vAcc_Cust != vCust_Acc) or (vDiv_Cust != vCust_Div) or (vGrp_Cust != vCust_Grp):
                                sql = """ 
                                        UPDATE  res_partner
                                        SET     kext_customer='%s',
                                                custom_acc_id='%s',
                                                custom_div_id=%s,
                                                custom_group_id=%s
                                        WHERE   kode_customer='%s'
                                    """ % (vCust_Ext,vCust_Acc,vDivision_Id,vGroup_Id,vCust_Int)
                                _logger.info(sql)
                                self._cr.execute(sql)

                            if vAction == "REPLACE":
                                #Delete Customer Grouping
                                sql = """ 
                                    DELETE
                                    FROM    res_partner_jalur_line
                                    WHERE   jalur_line_id=%s
                                    """ % (vPartner_Id)
                                _logger.info(sql)
                                self._cr.execute(sql)

                    if oldCust_Jlr != vCust_Jlr:
                        oldCust_Jlr = vCust_Jlr

                        #Search Jalur
                        sql = """ 
                            SELECT  id
                            FROM    res_partner_jalur
                            WHERE   code='%s'
                            """ % (vCust_Jlr)
                        _logger.info(sql)

                        self._cr.execute(sql)
                        rslt = self._cr.fetchall()
                        
                        if not rslt:
                            raise ValidationError("Route [%s] not found" % (vCust_Jlr) )
                        
                        else:
                            vRoute_Id = rslt[0][0]

                    if oldCust_JWK != vCust_JWK:
                        oldCust_JWK = vCust_JWK

                        vJWK_Id = vCust_JWK.upper()[:3]
                        if vJWK_Id == "SEN":
                            vJWK_Id = '1'
                        elif vJWK_Id == "SEL":
                            vJWK_Id = '2'
                        elif vJWK_Id == "RAB":
                            vJWK_Id = '3'
                        elif vJWK_Id == "KAM":
                            vJWK_Id = '4'
                        elif vJWK_Id == "JUM":
                            vJWK_Id = '5'
                        elif vJWK_Id == "SAB":
                            vJWK_Id = '6'
                        elif vJWK_Id == "MIN":
                            vJWK_Id = '7'
                        else:
                            vJWK_Id = '0'

                    vals = {
                            'jalur_line_id': vPartner_Id,
                            'jalur_id': vRoute_Id,
                            'jwk': vJWK_Id
                    }
                    _logger.info(vals)

                    if vAction == "REPLACE":
                        self.env['res.partner.jalur.line'].create(vals)

                    else:

                        rslt= self.env['res.partner.jalur.line'].search([ '&','&',
                                                                        ('jalur_line_id','=', vPartner_Id),
                                                                        ('jalur_id','=', vRoute_Id),
                                                                        ('jwk','=', vJWK_Id)
                                                                    ])
                    
                        if rslt:
                            rslt.write(vals)

                        else:
                            self.env['res.partner.jalur.line'].create(vals)

                    vBatch_Sequence += 1
                    if vBatch_Sequence > vBatch_Limit:
                        vBatch_Counter += 1
                        _logger.info("COMMIT - Batch #%s" % (vBatch_Counter))
                        vBatch_Sequence = 0
                        #self.env.cr.commit()


        finish_time = datetime.now()
        _logger.info("upload_xls_file Selesai [%s]" % ((finish_time-start_time)))


