
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



class Main(http.Controller):
            
    @http.route('/api/mrp/workcenter', type='json', auth='public', cors='*', csrf=False, save_session=True)
    def get_workcenter(self,**kwargs):
        workname = kwargs.get('workname')
        # machine
        workecenter = request.env['mrp.workcenter'].sudo().search([('name','=',workname)],limit=1)
        if workecenter:
            response_content = {
                                "success":True,
                                "message":"Workcenter has found",
                                "data": {
                                    "id":workecenter.id,
                                    "name":workecenter.name,
                                    }
                                }
            return response_content
        
        response_content = {
                            "success":True,
                            "message":"Workcenter Not found",
                            "data": False
                                }
        return response_content
    
    @http.route('/api/mrp/employee', type='json', auth='public', cors='*', csrf=False, save_session=True)
    def update_shift_and_employee(self,**kwargs):
        employee_id  = kwargs.get('employee_id')
        shift        = kwargs.get('shift')
        operation_id = kwargs.get('operation_id')
        note         = kwargs.get('note')
        final_set_id = kwargs.get('final_set_id')
        workorder = request.env['mrp.workorder'].sudo().browse([operation_id])
        if workorder:
            workorder.sudo().write({
                "employee_id":employee_id,
                "shift":shift,
                "note":note,
                "final_set_id":final_set_id
            })
            response_content = {
                    "success":True,
                    "message": "Update Employee and shift Success",
                    "data":workorder.read()
                }
            return response_content
    
            
        response_content = {
            "success":False,
            "message": "Update Employee and shift Failed",
            "data": False
        }
        
        return response_content
    
    
    @http.route('/api/mrp/machineids', type='json', auth='public', cors='*', csrf=False, save_session=True)
    def filter_machine(self,**kwargs):
        workcenter_id = kwargs.get('workcenter_id')
        domain = []
        if workcenter_id:
            domain += [('workcenter_ids','in',int(workcenter_id))]
        machine_ids   = request.env['mrp.machine'].sudo().search(domain)
        response_content = {
                                "success":True,
                                "message":"Machine found",
                                "data": {
                                    "machine_ids": [ {"id":machine.id,"text":machine.name} for machine in machine_ids],
                                    
                                }
                                }
        return response_content
        
        
    
    
    
    @http.route('/api/mrp/machine', type='json', auth='public', cors='*', csrf=False, save_session=True)
    def update_machine(self,**kwargs):
        machine      = kwargs.get('machine')
        operation_id = kwargs.get('operation_id')
        response_content = None
        mrp_machine = request.env['mrp.machine'].sudo().search([('name','=',machine)],limit=1)
        operation = request.env['mrp.workorder'].sudo().browse([operation_id])
        if mrp_machine and operation:
            if not operation.workcenter_id.is_planning:
                operation.sudo().write({"mesin_id":mrp_machine.id})
            response_content = {
                                "success":True,
                                "message":"Machine has found",
                                "data": {
                                    "id":mrp_machine.id,
                                    "name":mrp_machine.name,
                                    }
                                }
            return response_content
        if not mrp_machine:
            response_content = {
                                "success":True,
                                "message":"Machine Not found",
                                "data": False
                                    }
        elif not operation:
            response_content = {
                                "success":True,
                                "message":"Work Order Not found",
                                "data": False
                                    }
        return response_content
    
    @http.route('/api/mrp/finalset', type='json', auth='public', cors='*', csrf=False, save_session=True)
    def update_finalset(self,**kwargs):
        finalset      = kwargs.get('finalset')
        operation_id = kwargs.get('operation_id')
        response_content = None
       
        
        
        final_set_id = request.env['mrp.production.final.set'].sudo().search([('name','=',finalset)],limit=1)
        operation = request.env['mrp.workorder'].sudo().browse([operation_id])
        if final_set_id and operation:
            operation.sudo().write({"final_set_id":final_set_id.id})
            response_content = {
                                "success":True,
                                "message":"Final set has found",
                                "data": {
                                    "id":final_set_id.id,
                                    "name":final_set_id.name,
                                    }
                                }
            return response_content
        if not final_set_id:
            response_content = {
                                "success":True,
                                "message":"Final Set Not found",
                                "data": False
                                    }
        elif not operation:
            response_content = {
                                "success":True,
                                "message":"Work Order Not found",
                                "data": False
                                    }
        return response_content
        
        
        
        
        
    @http.route('/mrp/scanner', type='http', auth='public', cors='*', csrf=False, save_session=True)
    def scanner_home_page(self):
        session_info = request.env['ir.http'].session_info()
        # session_info['user_context']['allowed_company_ids'] = pos_session.company_id.ids
        if 'uid' in session_info and session_info.get('uid') == None:
            request.session.authenticate(request.session.db, 'produksi@pmti.com', '1234')
            session_info = request.env['ir.http'].session_info()
            
        
        context = {
            'session_info': session_info,
            # 'login_number': pos_session.login(),
        }
        import logging;
        _logger = logging.getLogger(__name__)
        _logger.warning('='*40)
        _logger.warning(context)
        _logger.warning('='*40)
        return request.render('wibicon_mo_scanner.home_page', qcontext=context)
    
    
    
    
    
    @http.route('/api/employee', type='http', method="POST", auth='public', cors='*', csrf=False, save_session=True)
    def get_employee(self,**kwargs):
        try:
            employee_barcode = kwargs['employee_barcode'] if 'employee_barcode' in kwargs else False
            if employee_barcode:
                employee = request.env['hr.employee'].sudo().search([('pin','=',employee_barcode)])
                response_content = {
                        "success":True,
                        "message":"Employee has found",
                        "data": {
                            "id":employee.id,
                            "name":employee.name,
                            "barcode":employee.barcode,
                            "departement":{
                                "id":employee.department_id.id,
                                "name":employee.department_id.name},
                        }
                    }
                    
                
                return http.Response(json.dumps(response_content,default=str), status=200,mimetype='application/json')
            response_content = {
                "success":True,
                "message":"Employee Not found",
                "data": None
                }
            return http.Response(json.dumps(response_content,default=str), status=200,mimetype='application/json')
            
            
        
        except Exception as e:
            _logger.error('='*50)
            _logger.error(e)
            _logger.error('='*50)
            
            response_content = {
                "success":False,
                "message":"Get Employee has been errors because\n"%(str(e)),
                "data": {}
            }
            
            return http.Response(json.dumps(response_content,default=str), status=200,mimetype='application/json')
        
    
    def _prepare_timeline_vals(self, workcenter_id, duration, date_start, date_end=False):
        # Need a loss in case of the real time exceeding the expected
        if not workcenter_id.duration_expected or duration < workcenter_id.duration_expected:
            loss_id = request.env['mrp.workcenter.productivity.loss'].sudo().search([('loss_type', '=', 'productive')], limit=1)
            if not len(loss_id):
                raise UserError(_("You need to define at least one productivity loss in the category 'Productivity'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
        else:
            loss_id = request.env['mrp.workcenter.productivity.loss'].sudo().search([('loss_type', '=', 'performance')], limit=1)
            if not len(loss_id):
                raise UserError(_("You need to define at least one productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
        return {
            'workorder_id': workcenter_id.id,
            'workcenter_id': workcenter_id.workcenter_id.id,
            'description': _('Time Tracking: %(user)s', user=request.env.user.name),
            'loss_id': loss_id[0].id,
            'date_start': date_start,
            'date_end': date_end,
            'user_id': request.env.user.id,  # FIXME sle: can be inconsistent with company_id
            # 'company_id': request.company_id.id,
        }
    
    @http.route('/api/mrp/wo/start', type='http', method="POST", auth='public', cors='*', csrf=False, save_session=True)
    def start_wo(self,**kwargs):
        try:
            # mrp_barcode   = kwargs['mrp_barcode'] if 'mrp_barcode' in kwargs else False
            workcenter_id = kwargs['workcenter_id'] if 'workcenter_id' in kwargs else False
            if workcenter_id:
                workcenter_id = request.env['mrp.workorder'].sudo().search([('id','=',workcenter_id)])
                workcenter_id.button_start()
        #         workcenter_id.sudo().ensure_one()
        # # As button_start is automatically called in the new view
        #         if workcenter_id.state in ('done', 'cancel'):
        #             return True

        #         if workcenter_id.product_tracking == 'serial':
        #             workcenter_id.qty_producing = 1.0

        #         request.env['mrp.workcenter.productivity'].sudo().create(
        #             self._prepare_timeline_vals(workcenter_id,workcenter_id.duration, datetime.now())
        #         )
        #         if workcenter_id.production_id.state != 'progress':
        #             workcenter_id.production_id.sudo().write({
        #                 'date_start': datetime.now(),
        #             })
        #         # if workcenter_id.state == 'progress':
        #         #     return True
        #         start_date = datetime.now()
        #         vals = {
        #             'state': 'progress',
        #             'date_start': start_date,
        #         }
        #         if not workcenter_id.leave_id:
        #             leave = request.env['resource.calendar.leaves'].sudo().create({
        #                 'name': workcenter_id.display_name,
        #                 'calendar_id': workcenter_id.workcenter_id.resource_calendar_id.id,
        #                 'date_from': start_date,
        #                 'date_to': start_date + relativedelta(minutes=workcenter_id.duration_expected),
        #                 'resource_id': workcenter_id.workcenter_id.resource_id.id,
        #                 'time_type': 'other'
        #             })
        #             vals['leave_id'] = leave.id
        #             workcenter_id.sudo().write(vals)
        #         else:
        #             if workcenter_id.date_planned_start > start_date:
        #                 vals['date_planned_start'] = start_date
        #             if workcenter_id.date_planned_finished and workcenter_id.date_planned_finished < start_date:
        #                 vals['date_planned_finished'] = start_date
        #             workcenter_id.sudo().write(vals)
                
                
            # if mrp_barcode:
            #     production = request.env['mrp.production'].sudo().search([('name','=',mrp_barcode)])
            response_content = {
                    "success":True,
                    "message":"%s is started "%(workcenter_id.name),
            }
            
            return http.Response(json.dumps(response_content,default=str), status=200,mimetype='application/json')
                
            
        except Exception as e:
            _logger.error('='*50)
            _logger.error(e)
            _logger.error('='*50)
            
            response_content = {
                "success":False,
                "message":"Get Employee has been errors because\n%s"%(str(e)),
                "data": {}
            }
            return http.Response(json.dumps(response_content,default=str), status=200,mimetype='application/json')
            
            
            
    @http.route('/api/mrp/wo-json', type='json', method="POST", auth='public', cors='*', csrf=False, save_session=True)
    def get_works_order_json(self,**kwargs):
        production_id = kwargs.get('production_id')
        production = request.env['mrp.production'].sudo().browse([production_id])
        finalset_ids = request.env['mrp.production.final.set'].sudo().search([('name','!=',False)])
        
        if production:
            response_content = {
                        "success":True,
                        "message":"Mrp Production has found",
                        "data": {
                            "id":production.id,
                            "name":production.name,
                            "finalset_ids": [ {"id":final.id,"text":final.name} for final in finalset_ids],
                            "workorder_ids":[ {"id":line.id,
                                                "no":x+1,
                                                "name": line.name,
                                                "no_urut": line.no_urut,
                                                "workcenter_id":{"id":line.workcenter_id.id,"name":line.workcenter_id.name},
                                                "date_planned_start": fields.Datetime.add(line.date_planned_start,hours=7).strftime('%d/%m/%Y %H:%M:%S') if line.date_planned_start else False,
                                                "date_planned_finished": fields.Datetime.add(line.date_planned_finished,hours=7).strftime('%d/%m/%Y %H:%M:%S') if line.date_planned_finished else False,
                                                "date_start": fields.Datetime.add(line.date_start,hours=7).strftime('%d/%m/%Y %H:%M:%S') if line.date_start else False,
                                                "date_finished": fields.Datetime.add(line.date_finished,hours=7).strftime('%d/%m/%Y %H:%M:%S') if line.date_finished else False,
                                                "production_id": {"id":line.production_id.id,"name":line.production_id.name},
                                                "duration_expected": line.duration_expected,
                                                "mesin_id": {"id":line.mesin_id.id,"name":line.mesin_id.name},
                                                "shift": line.shift,
                                                "employee_id": {"id":line.employee_id.id,"name":line.employee_id.name},
                                                "duration": round(line.duration,2),
                                                "note":line.note if line.note else "",
                                                "state": line.state,
                                                } for x,line in enumerate(production.workorder_ids.sorted(lambda x:x.no_urut))],
                            "product_id": {
                                "id":production.product_id.id,
                                "name":production.product_id.name,
                                "color":production.product_id.color_id.name},
                            "product_qty":production.product_qty,
                            "html_color":production.html_color,
                            "handling_id":{"id":production.handling_id.id,"name":production.handling_id.name},
                            "process_type":{"id":production.process_type.opc_id.id,"name":production.process_type.opc_id.name},
                            "opc_scouring_id":{"id":production.opc_scouring_id.id,"name":production.opc_scouring_id.name},
                            "design_id":{"id":production.design_id.id,"name":production.design_id.name},
                            "std_potong":production.std_potong,
                            "note":production.note,
                            "type_id": {
                                "id":production.type_id.id,
                                "name":production.type_id.name},
                            "sale_id":{
                                "id":production.sale_id.id,
                                "name":production.sale_id.name,
                            },
                            "partner_id":{
                                "id":production.sale_id.partner_id.id,
                                "name":production.sale_id.partner_id.name
                            },
                            "components_availability_state": production.components_availability_state,
                            "state": production.state,
                        }
                    }
                    
                
            return response_content

        else: 
            return {
                "success":False,
                "message": "Production Id not Found",
                "data": []
            }
            
    
    
    @http.route('/api/mrp/wo', type='http', method="POST", auth='public', cors='*', csrf=False, save_session=True)
    def get_works_order(self,**kwargs):
        try:
            mrp_barcode = kwargs['mrp_barcode'] if 'mrp_barcode' in kwargs else False
            if mrp_barcode:
                production = request.env['mrp.production'].sudo().search([('name','=',mrp_barcode)])
                machine_ids = request.env['mrp.machine'].sudo().search([('mrp_type_id','=',2),('name','!=',False)])
                finalset_ids = request.env['mrp.production.final.set'].sudo().search([('name','!=',False)])
                response_content = {
                        "success":True,
                        "message":"Mrp Production has found",
                        "data": {
                            "id":production.id,
                            "name":production.name,
                            "machine_ids": [ {"id":machine.id,"text":machine.name} for machine in machine_ids],
                            "finalset_ids": [ {"id":final.id,"text":final.name} for final in finalset_ids],
                            "workcenter_ids": [ {"id":wo.workcenter_id.id,"text":wo.workcenter_id.name} for wo in production.workorder_ids],
                            "workorder_ids":[ {"id":line.id,
                                               "no":x+1,
                                                "name": line.name,
                                                "no_urut": line.no_urut,
                                                "workcenter_id":{"id":line.workcenter_id.id,"name":line.workcenter_id.name},
                                                "date_planned_start": fields.Datetime.add(line.date_planned_start,hours=7).strftime('%d/%m/%Y %H:%M:%S') if line.date_planned_start else False,
                                                "date_planned_finished": fields.Datetime.add(line.date_planned_finished,hours=7).strftime('%d/%m/%Y %H:%M:%S') if line.date_planned_finished else False,
                                                # "date_planned_start": line.date_planned_start,
                                                # "date_planned_finished": line.date_planned_finished,
                                                # "date_start": line.date_start,
                                                # "date_finished": line.date_finished,
                                                "date_start": fields.Datetime.add(line.date_start,hours=7).strftime('%d/%m/%Y %H:%M:%S') if line.date_start else False,
                                                "date_finished": fields.Datetime.add(line.date_finished,hours=7).strftime('%d/%m/%Y %H:%M:%S') if line.date_finished else False,
                                                "production_id": {"id":line.production_id.id,"name":line.production_id.name},
                                                "duration_expected": line.duration_expected,
                                                "mesin_id": {"id":line.mesin_id.id,"name":line.mesin_id.name},
                                                "shift": line.shift,
                                                "employee_id": {"id":line.employee_id.id,"name":line.employee_id.name},
                                                "duration": round(line.duration,2),
                                                "note":line.note if line.note else "",
                                                "state": line.state,
                                            #   "beam_id": line.beam_id,
                                                } for x,line in enumerate(production.workorder_ids.sorted(lambda x:x.no_urut))],
                            "product_id": {
                                "id":production.product_id.id,
                                "name":production.product_id.name,
                                "color":production.product_id.color_id.name},
                            "product_qty":production.product_qty,
                            "html_color":production.html_color,
                            "handling_id":{"id":production.handling_id.id,"name":production.handling_id.name},
                            "process_type":{"id":production.process_type.opc_id.id,"name":production.process_type.opc_id.name},
                            "opc_scouring_id":{"id":production.opc_scouring_id.id,"name":production.opc_scouring_id.name},
                            "design_id":{"id":production.design_id.id,"name":production.design_id.name},
                            "std_potong":production.std_potong,
                            "note":production.note,
                            "type_id": {
                                "id":production.type_id.id,
                                "name":production.type_id.name},
                            "sale_id":{
                                "id":production.sale_id.id,
                                "name":production.sale_id.name,
                            },
                            "partner_id":{
                                "id":production.sale_id.partner_id.id,
                                "name":production.sale_id.partner_id.name
                            },
                            "components_availability_state": production.components_availability_state,
                            "state": production.state,
                        }
                    }
                    
                
                return http.Response(json.dumps(response_content,default=str), status=200,mimetype='application/json')
            response_content = {
                "success":True,
                "message":"Production Not found",
                "data": None
                }
            return http.Response(json.dumps(response_content,default=str), status=200,mimetype='application/json')
        
        
        except Exception as e:
            _logger.error('='*50)
            _logger.error(e)
            _logger.error('='*50)
            
            response_content = {
                "success":False,
                "message":"Get Employee has been errors because\n"%(str(e)),
                "data": {}
            }
            return http.Response(json.dumps(response_content,default=str), status=200,mimetype='application/json')
            
            
        
    @http.route('/api/mrp/inspect', type='http', method="POST", auth='public', cors='*', csrf=False, save_session=True)
    def get_mrp_order(self,**kwargs):
        try:
            mrp_barcode = kwargs['mrp_barcode'] if 'mrp_barcode' in kwargs else False
            if mrp_barcode:
                production = request.env['mrp.production'].sudo().search([('name','=',mrp_barcode),('state','=','confirmed')])
                response_content = {
                        "success":True,
                        "message":"Mrp Production has found",
                        "data": {
                            "id":production.id,
                            "name":production.name,
                            "move_line_before_ids":[ {"id":line.id,
                                                      "date": line.date,
                                                      "lot_id":{"id":line.lot_id.id,"name":line.lot_id.name},
                                                      "production_id":{"id":line.production_id.id,"name":line.production_id.name},
                                                      "employee_id":{"id":line.employee_id.id,"name":line.employee_id.name},
                                                      "shift": line.shift,
                                                      "quantity": line.quantity,
                                                    #   "beam_id": line.beam_id,
                                                      "is_inspecting": line.is_inspecting,
                                                      } for line in production.move_line_before_ids],
                            "product_id": {
                                "id":production.product_id.id,
                                "name":production.product_id.name},
                            
                            "state": production.state,
                        }
                    }
                    
                
                return http.Response(json.dumps(response_content,default=str), status=200,mimetype='application/json')
            response_content = {
                "success":True,
                "message":"Production Not found",
                "data": None
                }
            return http.Response(json.dumps(response_content,default=str), status=200,mimetype='application/json')
            
            
        
        except Exception as e:
            _logger.error('='*50)
            _logger.error(e)
            _logger.error('='*50)
            
            response_content = {
                "success":False,
                "message":"Get Production has been errors because\n"%(str(e)),
                "data": {}
            }
            
            return http.Response(json.dumps(response_content,default=str), status=200,mimetype='application/json')
        
    