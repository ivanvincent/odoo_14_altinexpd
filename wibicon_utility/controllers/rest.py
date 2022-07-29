
from base64 import b64decode
import json
import logging
import os
import subprocess
import time
import werkzeug.utils

from odoo import http, tools ,fields
from odoo.http import request ,send_file
from odoo.modules.module import get_resource_path



# from odoo.addons.hw_drivers.event_manager import event_manager
# from odoo.addons.hw_drivers.main import iot_devices, manager
# from odoo.addons.hw_drivers.tools import helpers

_logger = logging.getLogger(__name__)



class Rest(http.Controller):
    
    @http.route('/api/purchase-order', type='json', auth="user")
    def get_purchase_order(self,**params):
        domain = [tuple(domain)  for domain in params.get("domain") if domain != "|" and domain != '&']
        orders = request.env['purchase.order'].search(domain)
        data = []
        for i , order in enumerate(orders):

            line = []
            for x, ln in enumerate(order.order_line):
                query = """ select purchase_request_line_id from purchase_request_purchase_order_line_rel where purchase_order_line_id = %s """ % (ln.id)
                request._cr.execute(query)
                id_pr = request._cr.fetchone()
                prl_obj = request.env['purchase.request.line'].browse(id_pr if id_pr else False)
                line.append({"no":x+1,
                            "id":ln.id,
                            "product":ln.product_id.name,
                            "product_qty":ln.product_qty,
                            "product_uom":ln.product_uom.name,
                            "price_unit":ln.price_unit,
                            #  "discount":ln.discount,
                            "price_subtotal":ln.price_subtotal,
                            "taxes_id":', '.join(ln.taxes_id.mapped('name')),
                            "qty_onhand": prl_obj.qty_on_hand,
                            #  "amount_tax":order.order_id.amount_tax,
                        })

            data.append({
                "no":i,
                "id":order.id,
                "name":order.name,
                "partner_id":order.partner_id.name,
                "amount_tax":order.amount_tax,
                "date_order":fields.Date.to_string(order.date_order.date()),
                "amount_total":order.amount_total,
                "order_line": line,
            })
        
        
        return data
       
    
    @http.route('/api/product-attribute', type='json', auth="user")
    def get_product_attribute(self,**params):
        domain = [tuple(domain)  for domain in params.get("domain") if domain != "|" and domain != '&']
        attributes = request.env['product.attribute'].search(domain)
        data = []
        for i , attribute in enumerate(attributes):
            data.append({
                "no":i,
                "id":attribute.id,
                "name":attribute.name,
                "display_type":attribute.display_type,
                "create_variant":attribute.create_variant,
                "value_ids": [ {"no":x+1,
                                "id":value.id,
                                "name":value.name,
                                 }
                               for x, value in  enumerate(attribute.value_ids)],
                "product_tmpl_ids": [ {"no":x+1,
                                "id":product.id,
                                "name":product.name,
                                 }
                               for x, product in  enumerate(attribute.product_tmpl_ids)]
            })
        
        
        return data
    
    @http.route('/api/master-design', type='json', auth="user")
    def get_master_design(self,**params):
        domain = [tuple(domain)  for domain in params.get("domain") if domain != "|" and domain != '&']
        attributes = request.env['master.design'].search(domain)
        data = []
        for i , attribute in enumerate(attributes):
            data.append({
                "no":i,
                "id":attribute.id,
                "name":attribute.name,
                "display_type":attribute.display_type,
                "create_variant":attribute.create_variant,
                "warna_ids": [ {"no":x+1,
                                "id":value.id,
                                "name":value.name,
                                 }
                               for x, value in  enumerate(attribute.warna_ids)],
            })
        
        
        return data
       
    
    @http.route('/api/request-requisition', type='json', auth="user")
    def get_request_requisition(self,**params):
        domain = [tuple(domain)  for domain in params.get("domain") if domain != "|" and domain != '&']      # _logger.warning('='*40)
        _logger.warning('domain')
        _logger.warning(domain)
        _logger.warning('='*40)
        requests = request.env['request.requisition'].search(domain)
        data = []
        for i , req in enumerate(requests):
            data.append({
                "no":i,
                "id":req.id,
                "name":req.name,
                "request_by_warehouse":req.request_by_warehouse,
                "warehouse_id":req.warehouse_id.name,
                "internal_transfer_picking":req.internal_transfer_picking.name,
                "no_komunikasi":req.no_komunikasi,
                "internal_transfer_count":req.internal_transfer_count,
                "requested_by":req.requested_by.name,
                "request_id":req.request_id.name,
                "state":req.state,
                "request_date":fields.Date.to_string(req.request_date),
                "order_ids": [ {"no":x+1,
                                "id":line.id,
                                 "name":line.name,
                                 "product":line.product_id.name,
                                 "spesification":line.spesification,
                                 "qty_onhand":line.qty_onhand,
                                 "quantity":line.quantity,
                                 "uom_id":line.uom_id.name,
                                 }
                               for x, line in  enumerate(req.order_ids)]
            })
        
        # _logger.warning('='*40)
        # _logger.warning('data')
        # _logger.warning(data)
        # _logger.warning('='*40)
        
        return data
    
    
    @http.route('/api/session/',type='http', auth='none', methods=["GET"], csrf=False,)
    def check_session(self):
        try:
            request.session.check_security()
            request.uid = request.session.uid
            session =  request.env['ir.http'].session_info()
            if request.uid:
                response={
                    "success":True,
                    "message":"Session is valid",
                    "data": session
                }
            return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
        except Exception as e:
            response={"success":False,"message":e}
            return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
            

    @http.route('/api/auth/',type='json', auth='none', methods=["POST"], csrf=False,)
    def authenticate(self,**data):
        try:
            username = data['username']
            password = data['password']
            debe =  data['db']
            try:
                res = request.session.authenticate(debe, username, password)
                session_info = request.env['ir.http'].session_info()
                if not session_info['uid']:
                    session_info.update({'uid':0})
                    return session_info
                else:
                    return session_info
            except Exception:
                return "Invalid credentials."
        except Exception as e:
            response = {
                    "success":False,
                    "message":e,
                    "data":[]
                }
            return response