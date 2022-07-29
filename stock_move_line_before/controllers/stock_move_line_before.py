from base64 import b64decode
import json
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from odoo import http, tools, _, SUPERUSER_ID
from odoo.http import request ,send_file
from odoo.modules.module import get_resource_path
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)



class Main(http.Controller):
    
    @http.route('/api/employee', type='http', method="POST", auth='public', cors='*', csrf=False, save_session=True)
    def get_employee(self,**kwargs):
        try:
            employee_barcode = kwargs['employee_barcode'] if 'employee_barcode' in kwargs else False
            if employee_barcode:
                employee = request.env['hr.employee'].sudo().search([('barcode','=',employee_barcode)])
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
            
            
            
    @http.route('/api/mrp/wo', type='http', method="POST", auth='public', cors='*', csrf=False, save_session=True)
    def get_works_order(self,**kwargs):
        try:
            mrp_barcode = kwargs['mrp_barcode'] if 'mrp_barcode' in kwargs else False
            if mrp_barcode:
                production = request.env['mrp.production'].sudo().search([('name','=',mrp_barcode)])
                response_content = {
                        "success":True,
                        "message":"Mrp Production has found",
                        "data": {
                            "id":production.id,
                            "name":production.name,
                            "workorder_ids":[ {"id":line.id,
                                                "name": line.name,
                                                "workcenter_id":{"id":line.workcenter_id.id,"name":line.workcenter_id.name},
                                                "date_planned_start": line.date_planned_start,
                                                "date_planned_finished": line.date_planned_finished,
                                                "date_start": line.date_start,
                                                "date_finished": line.date_finished,
                                                "duration_expected": line.duration_expected,
                                                "duration": line.duration,
                                                "no_urut":line.no_urut,
                                                "state": line.state,
                                            #   "beam_id": line.beam_id,
                                                } for line in production.workorder_ids.sorted(lambda x: x.no_urut)],
                            "product_id": {
                                "id":production.product_id.id,
                                "name":production.product_id.name},
                            "product_qty":production.product_qty,
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
        
    
    @http.route('/api/mrp/movelinebefore/create', type='http', method="POST", auth='public', cors='*', csrf=False, save_session=True)
    def get_mrp_order(self,**kwargs):
        try:
            production_id = kwargs['production_id'] if 'production_id' in kwargs else False
            machine_id    = kwargs['machine_id'] if 'production_id' in kwargs else False
            quantity      = kwargs['quantity'] if 'quantity' in kwargs else False
            date          = kwargs['date'] if 'date' in kwargs else False
            employee_id   = kwargs['employee_id'] if 'employee_id' in kwargs else False
            shift         = kwargs['shift'] if 'shift' in kwargs else False
            beam_id       = kwargs['beam_id'] if 'beam_id' in kwargs else False
            grade         = kwargs['grade'] if 'grade' in kwargs else False
            # if mrp_barcode:
            #     production = request.env['mrp.production'].sudo().search([('name','=',mrp_barcode)])
            #     response_content = {
            #             "success":True,
            #             "message":"Mrp Production has found",
            #             "data": {
            #                 "id":production.id,
            #                 "name":production.name,
            #                 "move_line_before_ids":[ {"id":line.id,
            #                                           "date": line.date,
            #                                           "lot_id":{"id":line.lot_id.id,"name":line.lot_id.name},
            #                                           "production_id":{"id":line.production_id.id,"name":line.production_id.name},
            #                                           "employee_id":{"id":line.employee_id.id,"name":line.employee_id.name},
            #                                           "shift": line.shift,
            #                                         #   "beam_id": line.beam_id,
            #                                           "is_inspecting": line.is_inspecting,
            #                                           } for line in production.move_line_before_ids],
            #                 "product_id": {
            #                     "id":production.product_id.id,
            #                     "name":production.product_id.name},
                            
            #                 "state": production.state,
            #             }
            #         }
                    
                
            #     return http.Response(json.dumps(response_content,default=str), status=200,mimetype='application/json')
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