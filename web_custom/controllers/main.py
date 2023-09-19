# -*- coding: utf-8 -*-
import odoo
import os
import subprocess
import base64
from odoo import http, models, fields, _
from odoo.http import request
import json
from PIL import Image
from io import BytesIO
from datetime import date, datetime
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.auth_signup.controllers.main  import AuthSignupHome
from psycopg2 import OperationalError,InternalError
from odoo.addons.web.controllers.main import Home
# import werkzeug
# import magic
# import requests
# import shlex
import logging
_logger = logging.getLogger(__name__)

class Main(http.Controller):

    @http.route('/subscribe',type='http',auth='public',website=True)
    def subscribe(self,*kwargs):
        response_content = request.env['ir.ui.view']._render_template('web_custom.subscribe')
        return request.make_response(response_content,headers=[('Content-Type','text/html')])

    @http.route('/register',type='json',auth='public',website=True,cors="*")
    def prepare_subscribe(self,**kwargs):
        try:
            print('prepare_subscribe')
            firstname              = kwargs['data']['firstName'] if 'firstName' in kwargs['data'] else False
            lastname               = kwargs['data']['lastName'] if 'lastName' in kwargs['data'] else False
            email                  = kwargs['data']['email'] if 'email' in kwargs['data'] else False
            gender                 = kwargs['data']['gender'] if 'gender' in kwargs['data'] else False
            id_number              = kwargs['data']['idNumber'] if 'idNumber' in kwargs['data'] else False
            phone_number           = kwargs['data']['phoneNumber'] if 'phoneNumber' in kwargs['data'] else False
            address_user           = kwargs['data']['address'] if 'address' in kwargs['data'] else False
            job                    = kwargs['data']['job'] if 'job' in kwargs['data'] else False
            img_profile            = kwargs['data']['imgProfile'] if 'imgProfile' in kwargs['data'] else False
            nama_perusahaan        = kwargs['data']['nama_perusahaan'] if 'nama_perusahaan' in kwargs['data'] else False
            jabatan                = kwargs['data']['jabatan'] if 'jabatan' in kwargs['data'] else False
            divisi                 = kwargs['data']['divisi'] if 'divisi' in kwargs['data'] else False
            # proof_of_payments_url  = request.env["ir.config_parameter"].sudo().get_param(PROOFOFPAYMENTS_URL)
            # photo_id_url           = request.env["ir.config_parameter"].sudo().get_param(IDPHOTO_URL_KEY)
            # proof_of_payments_path = request.env["ir.config_parameter"].sudo().get_param(PROOFOFPAYMENTS_PATH_KEY)
            # photo_id_path          = request.env["ir.config_parameter"].sudo().get_param(IDPHOTO_PATH_KEY)
            pop_filename           = ''
            id_photo_filename      = ''
            saved_pop_path         = ''
            saved_id_photo_path    = ''
            
            
            
            identitas_url_binary = False
            bukti_transfer_binary = False
            # if id_photo and os.path.exists(photo_id_path):
            #     mime_type = ''
            #     if id_photo['mimeType'] == 'image/png':
            #         mime_type = '.png'
            #     elif id_photo['mimeType'] == 'image/jpeg':
            #         mime_type = '.jpeg'
            #     id_photo_filename =  firstname + lastname + mime_type
            #     saved_id_photo_path = photo_id_path + firstname + lastname +mime_type
            #     identitas_url_binary = id_photo['data'].split(',')[1]
            #     photo = Image.open(BytesIO(base64.b64decode(id_photo['data'].split(',')[1])))
            #     photo.save(saved_id_photo_path)
            
            # if proof_of_payments and os.path.exists(proof_of_payments_path):
            #     mime_type = ''
            #     if proof_of_payments['mimeType'] == 'image/png':
            #         mime_type = '.png'
            #     elif proof_of_payments['mimeType'] == 'image/jpeg':
            #         mime_type = '.jpeg'
                
            #     pop_filename =  firstname + lastname + mime_type
            #     saved_pop_path = proof_of_payments_path + firstname + lastname + mime_type
            #     photo = Image.open(BytesIO(base64.b64decode(proof_of_payments['data'].split(',')[1])))
            #     bukti_transfer_binary = proof_of_payments['data'].split(',')[1]
            #     photo.save(saved_pop_path)
            
            
            
            # if os.path.exists(photo_id_path):
            #     mime_type = None
            #     if id_photo['mimeType'] == 'image/png':
            #         mime_type = '.png'
            #     elif id_photo['mimeType'] == 'image/jpeg':
            #         mime_type = '.jpeg'
                    
            #     saved_id_photo_path = photo_id_path + firstname + lastname +mime_type
            #     with open(saved_id_photo_path,'w') as img:
            #         img.write(proof_of_payments['data'])
                    
            #         # img.write(base64.b64decode(id_photo['data'].split(',')[1]))
                    
            # if os.path.exists(proof_of_payments_path):
            #     mime_type = None
            #     if proof_of_payments['mimeType'] == 'image/png':
            #         mime_type = '.png'
            #     elif proof_of_payments['mimeType'] == 'image/jpeg':
            #         mime_type = '.jpeg'
            #     saved_pop_path = photo_id_path + firstname + lastname +mime_type
            #     with open(saved_pop_path,'w') as img:
            #         img.write(proof_of_payments['data'])
            #         # img.write(base64.b64decode(proof_of_payments['data'].split(',')[1]))
                    
                    
            # validation = request.env['res.users'].sudo()._constrains_sql(email,phone_number, id_number)
            # if validation:
            #     return {'success':False,'message':validation,'data':None, 'code':889}
            
            newPartner = request.env['res.partner'].sudo().create({
                'name':firstname + ' ' + lastname,
                'email':email,
            })
            
            _logger.warning(newPartner)
            
            
            
            if newPartner:
                newUser = request.env['res.users'].sudo().create({
                    'name':newPartner.name,
                    'login':email,
                    'gender_user':gender.lower(),
                    'partner_id':newPartner.id,
                    'identitas_number':id_number,
                    'address':address_user,
                    'job_users':job,
                    'phone':phone_number,
                    'image_1920':img_profile.split(',')[1],
                    'password': '1234',
                    'nama_perusahaan': nama_perusahaan,
                    'jabatan': jabatan,
                    'divisi': divisi,
                    # 'action_id': 1457,
                    # 'bukti_transfer_url': proof_of_payments_url + id_photo_filename,
                    # 'identitas_url': photo_id_url + pop_filename,
                    # 'bukti_transfer_binary': bukti_transfer_binary,
                    # 'identitas_url_binary' : identitas_url_binary,
                    'groups_id': [(6, 0, [9])],
                    
                })

                if newUser:
                    return {'success':True,'message':'Successfully Create User','data':newUser}
                else:
                    return {'success':False,'message':'Failed Create User','data':None}
            else:
                return {'success':False,'message':'Failed Create Partner','data':None}
        except InternalError as err:
            _logger.warning('='*100)
            _logger.warning(err)
            skip = True
            pass
            # return {'success':False,'message':err,'data':None}
        
        except OperationalError as err:
            skip = True
            # raise
            return {'success':False,'message':err,'data':None}
        except Exception as err:
            _logger.warning('='*100)
            _logger.warning(err)
            # return {'success':False,'message':err,'data':None, 'code':889}
    
    @http.route('/order-monoblock',type='http',auth='public',website=True)
    def order_monoblock(self,*kwargs):
        data = {
            'basics': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['basic.specification'].sudo().search([('type', '=', 'MONOBLOCK')])],
            'materials': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['material'].sudo().search([('type', '=', 'MONOBLOCK')])],
            'tips': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['tip.type'].sudo().search([])],
            'single_or_multi': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['single.or.multi.tip'].sudo().search([('type', '=', 'MONOBLOCK')])],
            'dust_cups': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['dust.cup.configuration'].sudo().search([('type', '=', 'MONOBLOCK')])],
            'keyway_config': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['keyway.configuration'].sudo().search([('type', '=', 'MONOBLOCK')])],
            'keyway_position': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['keyway.position'].sudo().search([('type', '=', 'MONOBLOCK')])],
            'head_flats': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['head.flat.extension'].sudo().search([('type', '=', 'MONOBLOCK')])],
            'heat_treatments': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['heat.treatment'].sudo().search([('type', '=', 'MONOBLOCK')])],
            'surface_treatments': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['surface.treatment'].sudo().search([('type', '=', 'MONOBLOCK')])],
            'custom_adjustments': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['custom.adjustment'].sudo().search([('type', '=', 'MONOBLOCK')])],
            'fat_options': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['fat.option'].sudo().search([('type', '=', 'MONOBLOCK')])],
            'hobbs': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['hobb'].sudo().search([('type', '=', 'MONOBLOCK')])],
            'drawings': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['drawing'].sudo().search([('type', '=', 'MONOBLOCK')])],

        }
        response_content = request.env['ir.ui.view']._render_template('web_custom.monoblock', data)
        return request.make_response(response_content,headers=[('Content-Type','text/html')])

    @http.route('/order-die',type='http',auth='public',website=True)
    def order_die(self,*kwargs):
        data = {
            'basics': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['basic.specification'].sudo().search([('type', '=', 'DIE')])],
            'materials': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['material'].sudo().search([('type', '=', 'DIE')])],
            'bores': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['bore.type'].sudo().search([])],
            'single_or_multi': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['single.or.multi.tip'].sudo().search([('type', '=', 'DIE')])],
            'die_screws': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['die.screw'].sudo().search([])],
            'optional_tapered_bores': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['optional.tapered.bore'].sudo().search([])],
            'heat_treatments': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['heat.treatment'].sudo().search([('type', '=', 'DIE')])],
            'surface_treatments': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['surface.treatment'].sudo().search([('type', '=', 'DIE')])],
            'custom_adjustments': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['custom.adjustment'].sudo().search([('type', '=', 'DIE')])],
            'fat_options': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['fat.option'].sudo().search([('type', '=', 'DIE')])],
            'die_setting_aligners': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['die.setting.aligner'].sudo().search([])],

        }
        response_content = request.env['ir.ui.view']._render_template('web_custom.die', data)
        return request.make_response(response_content,headers=[('Content-Type','text/html')])

    @http.route('/order-multipart',type='http',auth='public',website=True)
    def order_multipart(self,*kwargs):
        data = {
            'holder_specifications': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['holder.specification'].sudo().search([])],
            'holder_positions': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['holder.position'].sudo().search([])],
            'holder_materials': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['holder.material'].sudo().search([])],
            'dust_cup_configurations': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['dust.cup.configuration'].sudo().search([])],
            'keyway_configurations': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['keyway.configuration'].sudo().search([])],
            'keyway_positions': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['keyway.position'].sudo().search([])],
            'head_flat_extensions': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['head.flat.extension'].sudo().search([])],
            'holder_heat_treatments': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['holder.heat.treatment'].sudo().search([])],
            'holder_surface_treatments': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['holder.surface.treatment'].sudo().search([])],
            'tip_shapes': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['tip.shape'].sudo().search([])],
            'tip_positions': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['tip.position'].sudo().search([])],
            'tip_materials': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['tip.material'].sudo().search([])],
            'tip_heat_treatments': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['tip.heat.treatment'].sudo().search([])],
            'tip_surface_treatments': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['tip.surface.treatment'].sudo().search([])],
            'holder_caps': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['holder.cap'].sudo().search([])],
            'holder_cap_bores': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['holder.cap.bore'].sudo().search([])],
            'holder_cap_surface_treatments': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['holder.cap.surface.treatment'].sudo().search([])],
            'custom_adjustments': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['custom.adjustment'].sudo().search([])],
            'fat_options': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['fat.option'].sudo().search([('type', '=', 'MULTIPART')])],
            'hobbs': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['hobb'].sudo().search([('type', '=', 'MULTIPART')])],
            'drawings': [{'id': b.id, 'val':'%s ( IDR %s )' % (b.name,b.price) } for b in request.env['drawing'].sudo().search([])],

        }
        response_content = request.env['ir.ui.view']._render_template('web_custom.multipart', data)
        return request.make_response(response_content,headers=[('Content-Type','text/html')])

    @http.route('/confirm-order-monoblock',type='json',auth='public',website=True,cors="*")
    def prepare_order_monoblock(self,**kwargs):
        try:
            basicSpecification =  int(kwargs['data']['basicSpecification']) if 'basicSpecification' in kwargs['data'] else False
            materials          =  int(kwargs['data']['materials']) if 'materials' in kwargs['data'] else False
            tips               =  int(kwargs['data']['tips']) if 'tips' in kwargs['data'] else False
            single_or_multi    =  int(kwargs['data']['single_or_multi']) if 'single_or_multi' in kwargs['data'] else False
            dust_cups          =  int(kwargs['data']['dust_cups']) if 'dust_cups' in kwargs['data'] else False
            keyway_config      =  int(kwargs['data']['keyway_config']) if 'keyway_config' in kwargs['data'] else False
            keyway_position    =  int(kwargs['data']['keyway_position']) if 'keyway_position' in kwargs['data'] else False
            head_flats         =  int(kwargs['data']['head_flats']) if 'head_flats' in kwargs['data'] else False
            heat_treatments    =  int(kwargs['data']['heat_treatments']) if 'heat_treatments' in kwargs['data'] else False
            surface_treatments =  int(kwargs['data']['surface_treatments']) if 'surface_treatments' in kwargs['data'] else False
            custom_adjustments =  int(kwargs['data']['custom_adjustments']) if 'custom_adjustments' in kwargs['data'] else False
            fat_options        =  int(kwargs['data']['fat_options']) if 'fat_options' in kwargs['data'] else False
            hobbs              =  int(kwargs['data']['hobbs']) if 'hobbs' in kwargs['data'] else False
            drawings           =  int(kwargs['data']['drawings']) if 'drawings' in kwargs['data'] else False
            punch              =  int(kwargs['data']['punch']) if 'punch' in kwargs['data'] else False
            tip           =  int(kwargs['data']['tip']) if 'tip' in kwargs['data'] else False

            monoblock_obj = request.env['monoblock'].sudo().create({
                'basic_specification_id' : basicSpecification,
                'material_id' : materials,
                'tip_type_id' : tips,
                'single_multi_tip_id' : single_or_multi,
                'dust_cup_configuration_id' : dust_cups,
                'keyway_position_id' : keyway_position,
                'head_flat_extension_id' : head_flats,
                'heat_treatment_id' : heat_treatments,
                'surface_treatment_id' : surface_treatments,
                'custom_adjustment_id' : custom_adjustments,
                'fat_option_id' : fat_options,
                'hobb_id' : hobbs,
                'drawing_id' : drawings,
                'keyway_configuration_id' : keyway_config,
                'user_id' : request.env.user.id,
                'punch': punch,
                'tip': tip
            })
            return monoblock_obj.id

        except Exception as err:
            _logger.warning('='*100)
            _logger.warning(err)
            return False

    @http.route('/confirm-die',type='json',auth='public',website=True,cors="*")
    def prepare_order_die(self,**kwargs):
        try:
            basics = int(kwargs['data']['basics']) if 'basics' in kwargs['data'] else False
            materials = int(kwargs['data']['materials']) if 'materials' in kwargs['data'] else False
            bores = int(kwargs['data']['bores']) if 'bores' in kwargs['data'] else False
            single_or_multi = int(kwargs['data']['single_or_multi']) if 'single_or_multi' in kwargs['data'] else False
            die_screws = int(kwargs['data']['die_screws']) if 'die_screws' in kwargs['data'] else False
            optional_tapered_bores = int(kwargs['data']['optional_tapered_bores']) if 'optional_tapered_bores' in kwargs['data'] else False
            heat_treatments = int(kwargs['data']['heat_treatments']) if 'heat_treatments' in kwargs['data'] else False
            surface_treatments = int(kwargs['data']['surface_treatments']) if 'surface_treatments' in kwargs['data'] else False
            custom_adjustments = int(kwargs['data']['custom_adjustments']) if 'custom_adjustments' in kwargs['data'] else False
            fat_options = int(kwargs['data']['fat_options']) if 'fat_options' in kwargs['data'] else False
            die_setting_aligners = int(kwargs['data']['die_setting_aligners']) if 'die_setting_aligners' in kwargs['data'] else False

            die = request.env['die'].sudo().create({
                'basic_specification_id' : basics,
                'material_id' : materials,
                'bore_type_id' : bores,
                'single_multi_tip_id' : single_or_multi,
                'die_screw_id' : die_screws,
                'optional_tapered_bore_id' : optional_tapered_bores,
                'heat_treatment_id' : heat_treatments,
                'surface_treatment_id' : surface_treatments,
                'custom_adjustment_id' : custom_adjustments,
                'fat_option_id' : fat_options,
                'die_setting_aligner_id' : die_setting_aligners,
                'user_id' : request.env.user.id,
            })
        except Exception as err:
            _logger.warning('='*100)
            _logger.warning(err)
    
    @http.route('/confirm-multipart',type='json',auth='public',website=True,cors="*")
    def prepare_order_multipart(self,**kwargs):
        try:
            holder_specification_id = int(kwargs['data']['holder_specifications']) if 'holder_specifications' in kwargs['data'] else False
            holder_position_id = int(kwargs['data']['holder_positions']) if 'holder_positions' in kwargs['data'] else False
            holder_material_id = int(kwargs['data']['holder_materials']) if 'holder_materials' in kwargs['data'] else False
            dust_cup_configuration_id = int(kwargs['data']['dust_cup_configurations']) if 'dust_cup_configurations' in kwargs['data'] else False
            keyway_configuration_id = int(kwargs['data']['keyway_configurations']) if 'keyway_configurations' in kwargs['data'] else False
            keyway_position_id = int(kwargs['data']['keyway_positions']) if 'keyway_positions' in kwargs['data'] else False
            head_flat_extension_id = int(kwargs['data']['head_flat_extensions']) if 'head_flat_extensions' in kwargs['data'] else False
            holder_heat_treatment_id = int(kwargs['data']['holder_heat_treatments']) if 'holder_heat_treatments' in kwargs['data'] else False
            holder_surface_treatment_id = int(kwargs['data']['holder_surface_treatments']) if 'holder_surface_treatments' in kwargs['data'] else False
            tip_shape_id = int(kwargs['data']['tip_shapes']) if 'tip_shapes' in kwargs['data'] else False
            tip_position_id = int(kwargs['data']['tip_positions']) if 'tip_positions' in kwargs['data'] else False
            tip_material_id = int(kwargs['data']['tip_materials']) if 'tip_materials' in kwargs['data'] else False
            tip_heat_treatment_id = int(kwargs['data']['tip_heat_treatments']) if 'tip_heat_treatments' in kwargs['data'] else False
            tip_surface_treatment_id = int(kwargs['data']['tip_surface_treatments']) if 'tip_surface_treatments' in kwargs['data'] else False
            holder_cap_id = int(kwargs['data']['holder_caps']) if 'holder_caps' in kwargs['data'] else False
            holder_cap_bore_id = int(kwargs['data']['holder_cap_bores']) if 'holder_cap_bores' in kwargs['data'] else False
            holder_cap_surface_id = int(kwargs['data']['holder_cap_surface_treatments']) if 'holder_cap_surface_treatments' in kwargs['data'] else False
            custom_adjustment_id = int(kwargs['data']['custom_adjustments']) if 'custom_adjustments' in kwargs['data'] else False
            fat_option_id = int(kwargs['data']['fat_options']) if 'fat_options' in kwargs['data'] else False
            hobb_id = int(kwargs['data']['hobbs']) if 'hobbs' in kwargs['data'] else False
            drawing_id = int(kwargs['data']['drawings']) if 'drawings' in kwargs['data'] else False

            multipart = request.env['multipart'].sudo().create({
                'holder_specification_id' : holder_specification_id,
                'holder_position_id' : holder_position_id,
                'holder_material_id' : holder_material_id,
                'dust_cup_configuration_id' : dust_cup_configuration_id,
                'keyway_configuration_id' : keyway_configuration_id,
                'keyway_position_id' : keyway_position_id,
                'head_flat_extension_id' : head_flat_extension_id,
                'holder_heat_treatment_id' : holder_heat_treatment_id,
                'holder_surface_treatment_id' : holder_surface_treatment_id,
                'tip_shape_id' : tip_shape_id,
                'tip_position_id' : tip_position_id,
                'tip_material_id' : tip_material_id,
                'tip_heat_treatment_id' : tip_heat_treatment_id,
                'tip_surface_treatment_id' : tip_surface_treatment_id,
                'holder_cap_id' : holder_cap_id,
                'holder_cap_bore_id' : holder_cap_bore_id,
                'holder_cap_surface_id' : holder_cap_surface_id,
                'custom_adjustment_id' : custom_adjustment_id,
                'fat_option_id' : fat_option_id,
                'hobb_id' : hobb_id,
                'drawing_id' : drawing_id,
                'user_id' : request.env.user.id,
            })

        except Exception as err:
            _logger.warning('='*100)
            _logger.warning(err)

    @http.route('/page/success',type='http',auth='public',website=True)
    def success_subscribe(self,**kwargs):
        print('====success_subscribe===')
        print(kwargs)
        if kwargs.get('user'):
            data = {'name_user': base64.b64decode(kwargs.get('user'))}
            response_content = request.env['ir.ui.view']._render_template('web_custom.success_subscribe', data)
            return request.make_response(response_content,headers=[('Content-Type','text/html')])
    
    @http.route('/page/error',type='http',auth='public',website=True)
    def error_subscribe(self,**kwargs):
        
        response_content = request.env['ir.ui.view']._render_template('web_custom.error_subscribe')
        return request.make_response(response_content,headers=[('Content-Type','text/html')])