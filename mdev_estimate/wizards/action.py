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

class EstimateActionWizard(models.TransientModel):
    _name = 'estimate.action.wizard'
    _description = 'Estimate Action Wizard'

    action_type = fields.Selection([('validate','Validate'),
                                    ],
                                    default="validate", string="Action Type", required="1")

    est_date = fields.Date(string="Estimate Date", required="1", default=fields.Date.today)
    dlv_date = fields.Date(string="Delivery Date", required="1", default=fields.Date.today)

    picking_type_id = fields.Many2one('stock.picking.type', string="Operation Type" ) 
    location_id = fields.Many2one('stock.location', string="Source Location" ) 
    location_dest_id = fields.Many2one('stock.location', string="Destination Location" ) 

    divisi_id = fields.Many2one('res.partner.divisi', string="Division" )
    jalur_id = fields.Many2one('res.partner.jalur', string="Route" )

    def process(self):

        self.ensure_one()
        start_time = datetime.now()
        so_created = 0

        vest_date = self.est_date
        vdlv_date = self.dlv_date

        sql = """ 
                SELECT   id,estimate_date,estimate_type,commitment_date,customer_id,divisi_id,group_id,route_id,route_jwk,product_id,product_qty,so_number
                FROM     estimate
                WHERE    state='confirm' AND product_qty > 0 AND to_char(estimate_date, 'YYYY-MM-DD')='%s' AND to_char(commitment_date, 'YYYY-MM-DD')='%s'
            """ % (vest_date,vdlv_date)

        #if self.divisi_id:
        #    sql = sql + "AND custom_div_id=%s " % (str(self.divisi_id.id))

        #if self.jalur_id:
        #    sql = sql + "AND custom_group_id=%s " % (str(self.jalur_id.id))

        sql = sql + "ORDER BY estimate_date,estimate_type,commitment_date,divisi_id,route_id,customer_id"

        #_logger.info("ESTIMATE %s " % (sql))
        self._cr.execute(sql)
        estimate = self._cr.fetchall()
        #_logger.info("ESTIMATE => %s " % (estimate))

        est_head = []
        est_prod = []

        old_key = ""
        for est in estimate:

            vest_id          = est[0]
            vestimate_date   = est[1]
            vestimate_type   = est[2]
            vcommitment_date = est[3]
            vcustomer_id     = est[4]
            vdivisi_id       = est[5]
            vgroup_id        = est[6]
            vroute_id        = est[7]
            vroute_jwk       = est[8]
            vproduct_id      = est[9]
            vproduct_qty     = est[10]
            vso_number       = est[11]

            vkey = str(vestimate_date)+vestimate_type.upper()+str(vcommitment_date)+str(vcustomer_id)
            if old_key != vkey:
                old_key = vkey

                est_head.append({   'key': vkey,
                                    'est_id': vest_id,
                                    'estimate_date': vestimate_date,
                                    'estimate_type': vestimate_type,
                                    'commitment_date': vcommitment_date,
                                    'customer_id': vcustomer_id,
                                    'divisi_id': vdivisi_id,
                                    'group_id': vgroup_id,
                                    'route_id': vroute_id,
                                    'route_jwk': vroute_jwk,
                                    'so_number': vso_number,
                                })

            est_prod.append({   'key': vkey,
                                'est_id': vest_id,
                                'estimate_type': vestimate_type,
                                'product_id': vproduct_id,
                                'product_qty': vproduct_qty,
                            })

        #_logger.info("est_head %s " % (est_head))
        #_logger.info("est_prod %s " % (est_prod))

        for est in est_head:

            vkey             = est['key']
            vest_id          = est['est_id']
            vestimate_date   = est['estimate_date']
            vestimate_type   = est['estimate_type']
            vcommitment_date = est['commitment_date']
            vcustomer_id     = est['customer_id']
            vdivisi_id       = est['divisi_id']
            vgroup_id        = est['group_id']
            vroute_id        = est['route_id']
            vroute_jwk       = est['route_jwk']
            vso_number       = est['so_number']

            so_temp = [row for row in est_prod if vkey == row['key']]
            so_line = []

            est_ids = []
            for y in so_temp:
                est_ids.append(y['est_id'])
                so_line.append((0,0,{   'type': y['estimate_type'],
                                        'product_id': y['product_id'],
                                        'product_uom_qty': y['product_qty'],
                                    }))
            if est_ids:
                est_ids.append(y['est_id'])

            so_vals = { 'date_order':       vestimate_date,
                        'partner_id':       vcustomer_id,
                        'commitment_date':  vcommitment_date,
                        'order_line':       so_line
                    }
            #_logger.info("so_vals %s " % (so_vals))

            so_id = self.env['sale.order'].create(so_vals)

            if so_id:

                so_created += 1
                _logger.info("SO Created %s " % (so_id.name))

                #Validate Estimate
                sql = """ 
                        UPDATE   estimate
                        SET      state='done',so_number=%s
                        WHERE    id IN %s
                    """ % (so_id.id,tuple(est_ids))
                self._cr.execute(sql)

                #Confirm SO
                so_id.sudo().action_confirm()

                #Update Divisi,Group,Jalur,JWK
                sql = """ 
                        UPDATE  sale_order
                        SET     custom_div_id=%s,custom_group_id=%s,custom_jalur_id=%s,custom_jalur_jwk='%s'
                        WHERE   id=%s                        
                    """ % (vdivisi_id,vgroup_id,vroute_id,vroute_jwk,so_id.id)
                self._cr.execute(sql)

                sql = """ 
                        UPDATE  stock_picking
                        SET     custom_div_id=%s,custom_group_id=%s,custom_jalur_id=%s,custom_jalur_jwk='%s'
                        WHERE   origin='%s'                        
                    """ % (vdivisi_id,vgroup_id,vroute_id,vroute_jwk,so_id.name)
                self._cr.execute(sql)

        finish_time = datetime.now()
        _logger.info("Validated -> %s (created: %s)" % ((finish_time-start_time),so_created))
