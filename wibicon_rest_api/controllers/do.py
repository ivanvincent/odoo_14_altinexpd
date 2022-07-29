
from base64 import b64decode
import json
import logging
import os
import subprocess
import time
from urllib import response
import werkzeug.utils
from odoo import http, tools ,fields
from odoo.http import request ,send_file
from odoo.modules.module import get_resource_path
_logger = logging.getLogger(__name__)


def error_response(message):
    response = {
                "success":False,
                "message":message,
                "data": None
                }
                
    return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')

        
    
    


class RestDo(http.Controller):
    
    @http.route('/api/v1/getRutebySales/',type='http', auth='user', methods=["POST"], csrf=False,)
    def get_do_by_sales(self,**args):
        try:
            user_id  = args.get('user_id')
            device_id = args.get('device_id')
            sales_id = request.env['res.users'].sudo().search([('id','=',user_id),('device_id','=',device_id)],limit=1)
            if sales_id:
                rute_ids = request.env['rute.sale'].sudo().search([('sales_id','=',sales_id.tag_employee_id.id)])
                if rute_ids:
                    response = {
                    "success":True,
                    "message":'Sukses \n Rute Sale ditemukan',
                    "data": [{
                        "rute_id"  :rute.id,
                        "rute_name":rute.name ,
                        "date_actual":rute.date_actual,
                        "warehouse_id":rute.warehouse_id.id,
                        "warehouse_name":rute.warehouse_id.name,
                        "user_id":user_id,
                        "jalur_id":rute.jalur_id.id,
                        "jalur_name":rute.jalur_id.name,
                        "vehicle_id":rute.vehicle_id.id,
                        "vehicle_name":rute.vehicle_id.name,
                        "customer_ids": [
                            {
                            "id":line.id,
                            "partner_id":line.partner_id.id,
                            "partner_name":line.partner_id.name,
                            "credit_limit":line.partner_id.credit_limit,
                            "remaining_limit":line.partner_id.outstanding_credit_limit,
                            "type":line.partner_id.customer_type,
                            "street":line.partner_id.street,
                            "street_2":line.partner_id.street2,
                            "city":line.partner_id.street2,
                            "zip":line.partner_id.zip,
                            "phone":line.partner_id.phone,
                            "mobile":line.partner_id.mobile,
                            "email":line.partner_id.email,
                            "partner_code":line.partner_id.ref,
                            "rute_id":line.rute_id.id,\
                            "rute_name":line.rute_id.name,"state_visit_id":line.state_visit_id.id,\
                            "move_id":line.move_id.id,"move_name":line.move_id.name,"move_amount":line.move_amount,\
                            "datetime_start":line.datetime_start,\
                            "datetime_end":line.datetime_end,
                            "akurasi":line.akurasi,
                            "property_product_pricelist_id":line.property_product_pricelist.id,
                            "property_product_pricelist_name":line.property_product_pricelist.name,
                            "tepat_tidak":line.tepat_tidak,
                            "partner_latitude":line.partner_latitude,
                            "partner_longitude":line.partner_longitude,
                            "currency_id":line.currency_id.id,
                            "currency_name":line.currency_id.name} for line in rute.rute_cust_ids],
                        "product_ids": [{"product_id":line.get('product_id')[0],"product_name":line.get('product_id')[1] ,"product_code":line.get('default_code')} for line in rute.line_ids.read_group([],['product_uom_qty'],['product_id','default_code'],lazy=False)],
                        "expense_ids": [{"expense_id":expense.expense_id.id ,"expense_name":expense.expense_id.name,"quantity":expense.quantity} for expense in rute.expense_ids],
                        "line_fg_ids": [ {
                                        "rute_id":line.rute_id.id,
                                        "location_id":line.location_id.id,
                                        "location_name":line.location_id.name,
                                        "product_id":line.product_id.id,
                                        "image_128":line.image_128,
                                        "product_code":line.default_code,
                                        "product_name":line.product_id.name,
                                        "product_uom_id":line.product_uom_id.id,
                                        "product_uom_name":line.product_uom_id.name,
                                        "product_uom_qty":line.product_uom_qty} for  line in rute.line_fg_ids],
                        "line_siba_ids":[ {
                                        "rute_id":line.rute_id.id,
                                        "location_id":line.location_id.id,
                                        "location_name":line.location_id.name,
                                        "product_id":line.product_id.id,
                                          "product_name":line.product_id.name,
                                        "product_code":line.default_code,
                                          "product_uom_id":line.product_uom_id.id,
                                          "product_uom_name":line.product_uom_id.name,
                                          "product_uom_qty":line.product_uom_qty} for  line in rute.line_siba_ids],
                        "line_return_ids":[ {
                                        "rute_id":line.rute_id.id,
                                        "location_id":line.location_id.id,
                                        "location_name":line.location_id.name,
                                        "product_id":line.product_id.id,
                                        "product_name":line.product_id.name,
                                        "product_code":line.default_code,
                                        "product_uom_id":line.product_uom_id.id,
                                        "product_uom_name":line.product_uom_id.name,
                                        "product_uom_qty":line.product_uom_qty} for  line in rute.line_return_ids],
                        } for rute in rute_ids],
                    }
                    
                    return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
                else:
                    response = {
                    "success":True,
                    "message":'Sukses \nRute Sale untuk sales %s tidak ditemukan'%(sales_id.name),
                    "data": [],
                    }
                    
                    return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
                    
            elif not sales_id:
                return  error_response('Sales Tidak Ditemukan')
        except Exception as e:
            return  error_response(e)
    
    @http.route('/api/v1/getItembyRute',type='http', auth='user', methods=["POST"], csrf=False,)
    def get_line_by_rute(self,**args):
        try:
            rute_id  = args.get('rute_id')
            rute_line_ids = request.env['rute.sale.line'].sudo().search([('rute_id','=',int(rute_id))])
            import logging;
            _logger = logging.getLogger(__name__)
            _logger.warning('='*40)
            _logger.warning(rute_line_ids)
            _logger.warning(rute_id)
            _logger.warning('='*40)
            if rute_line_ids:
                response = {
                    "success":True,
                    "message":'Sukses \n Do ditemukan',
                    "data": [{"rute_id":line.rute_id.id,
                              "product_id":line.product_id.id,
                              "product_name":line.product_id.name,
                              "product_code":line.default_code,
                              "product_uom_qty":line.product_uom_qty,
                              "product_uom_id":line.product_uom_id.id,
                              "product_uom_name":line.product_uom_id.name} for line in rute_line_ids] }
                return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
                
                
            else:
                response = {
                    "success":True,
                    "message":'Sukses \nDO untuk do %s tidak ditemukan'%(rute_id),
                    "data": [],
                    }
                    
                return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
                    
                
            
        except Exception as e:
            return error_response(e)
            
            
    
        
    @http.route('/api/v1/getOutletbyJalur',type='http', auth='user', methods=["POST"], csrf=False,)
    def get_outlet_by_jalur(self,**args):
        try:
            jalur_id  = args.get('jalur_id')
            customer_ids = request.env['res.partner.jalur.line'].sudo().search([('jalur_id','=',jalur_id)])
            if customer_ids:
                response = {
                    "success":True,
                    "message":'Sukses \n Do ditemukan',
                    "data": [{"line_id":line.id,
                              "id":line.partner_id.id,
                              "name":line.partner_id.name,
                              "type":line.partner_id.customer_type,
                              "code":line.partner_id.ref,
                              "street":line.partner_id.street,
                              "street_2":line.partner_id.street2,
                              "city":line.partner_id.street2,
                              "zip":line.partner_id.zip,
                              "phone":line.partner_id.phone,
                              "mobile":line.partner_id.mobile,
                              "email":line.partner_id.email,
                              "npwp":line.partner_id.npwp,
                              "credit_limit":line.partner_id.credit_limit,
                              "property_product_pricelist_id":line.partner_id.property_product_pricelist.id,
                               "property_product_pricelist_name":line.partner_id.property_product_pricelist.name,
                              "outstanding_credit_limit":line.partner_id.outstanding_credit_limit,
                              "jwk":line.jwk} for line in customer_ids]
                    }
                
                return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
            elif not customer_ids:
                response = {
                    "success":True,
                    "message":'Sukses \n Customer tidak ditemukan',
                    "data": []}
                
                return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
            
        except Exception as e:
            return  error_response(e)
            
    @http.route('/api/v1/invoice/create',type='http', auth='user', methods=["POST"], csrf=False,)
    def create_invoice(self,**args):
        try:
            user_id  = args.get('user_id')
            rute_id  = args.get('rute_id')
            partner_id = args.get('partner_id')
            moveline_ids = args.get('moveline_ids')
            rute_id = request.env['rute.sale'].sudo().search([('id','=',rute_id)],limit=1)
            moveline = []
            if moveline_ids:
                for move in moveline_ids:
                    moveline.append((0,0,{
                        "product_id":move.get('product_id'),
                        "price_unit":move.get('price_unit'),
                        "quantity":move.get('quantity'),
                    }))
            if rute_id and partner_id:
                partner_id = rute_id.rute_cust_ids.filtered(lambda l: l.partner_id == partner_id)
                partner_id = partner_id.partner_id if partner_id else False
            
                move = request.env['account.move'].create({
                    'partner_id': partner_id.id,
                    'move_type': 'in_invoice',
                    'payment_reference': rute_id.name,
                    'invoice_date': fields.Date.today(),
                    'invoice_line_ids': moveline
                })
                if move:
                    response = {
                    "success":True,
                    "message":'Sukses \n Invoice Berhasil dibentuk',
                    "data":{
                        "id":move.id,
                        "name":move.name,
                        "payment_reference":move.payment_reference,
                        "state":move.state,
                        "amount_total":move.amount_total,
                        "payment_state":move.payment_state,
                        "invoice_date":move.invoice_date,
                        "invoice_line_ids": [
                            {"product_id":line.product_id,
                             "product_uom_id":line.product_uom_id.id,
                             "price_unit":line.price_unit,
                             "quantity":line.quantity} for line in move.invoice_line_ids],
                        
                    }}
                    
                    return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
                    
            elif not rute_id:
                return error_response("Rute Sale Tidak Ditemukan")
            elif not partner_id:
                return error_response("Customer Tidak Ditemukan")
            
            
            
        except Exception as e:
            return  error_response(e)
            