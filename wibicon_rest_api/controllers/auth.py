
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



class RestAuth(http.Controller):
    
    @http.route('/api/v1/auth/',type='http', auth='none', methods=["POST"], csrf=False,)
    def authenticate(self,**args):
        try:
            username  = args.get('username')
            password  = args.get('password')
            device_id = args.get('device_id')
            debe =  args.get('db')
            res = request.session.authenticate(debe, username, password)
            session_info = request.env['ir.http'].sudo().session_info()
            user_id = request.env['res.users'].sudo().browse(res)
            if not user_id:
                session_info.sudo().update({'uid':0})
                response={
                    "success":False,
                    "message":"Invalid Credential",
                    "data": None
                }
                return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
            elif not user_id.device_id and not device_id:
                
                response = {
                    "success":False,
                    "message": 'Device Belum Terdaftar',
                    "data": None
                }
                
                return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
            
            elif not user_id.device_id and device_id:
                user_id.sudo().write({"device_id":device_id})
                response={
                "success":True,
                "message":"Login Successful",
                "data": {
                    "user_id":user_id.id,
                    "username":user_id.name,
                    "session_id":session_info.get('session_id'),
                    "device_id": user_id.device_id,
                    "fcm_key":user_id.fcm_key,
                    "department_id": user_id.department_id.id,
                    "department_name": user_id.department_id.name,
                    "job_id": user_id.job_id.id,
                    "job_name": user_id.job_id.name,
                }
            }
                
                return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
                
            
            response={
                "success":True,
                "message":"Login Successful",
                "data": {
                    "user_id":user_id.id,
                    "username":user_id.name,
                    "session_id":session_info.get('session_id'),
                    "device_id": user_id.device_id,
                    "fcm_key":user_id.fcm_key,
                    "department_id": user_id.department_id.id,
                    "department_name": user_id.department_id.name,
                    "job_id": user_id.job_id.id,
                    "job_name": user_id.job_id.name,
                }
            }
            return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
                    
        except Exception as e:
            response = {
                    "success":False,
                    "message":e,
                    "data":[]
                }
            return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
    
    
    @http.route('/api/v1/regis/',type='http', auth='none', methods=["POST"], csrf=False,)
    def register(self,**args):
        try:
            user_id    = args.get('user_id')
            device_id  = args.get('device_id')
            user_id = request.env['res.users'].sudo().search([('id','=',user_id)])
            if user_id and device_id:
                user_id.sudo().write({'device_id':device_id})
                response = {
                    "success": True,
                    "message":"Device Berhasil Di Registrasi",
                    "data":[]
                }
                return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
            else:
                response = {
                    "success": False,
                    "message":"Device GAgaL Di Registrasi",
                    "data":[]
                }
                return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
            
        except Exception as e:
            response = {
                    "success":False,
                    "message":e,
                    "data":[]
                }
            return http.Response(json.dumps(response,default=str),status=200,mimetype='application/json')
    
    
           