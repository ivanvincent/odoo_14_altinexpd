from odoo import models, fields, api
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)
class WorkorderDaily(models.Model):
    _name = 'workorder.daily'

    name        = fields.Char(string='Name')
    employee_id = fields.Many2one('hr.employee', string='Operator',)
    date        = fields.Date(string='Date', default=fields.Date.today())
    mrp_workorder_line_ids = fields.One2many('mrp.workorder.line', 'wo_daily_id', 'Line')
    scanner     = fields.Char('Scanner')

    # @api.model
    def barcode_scan(self):
        action = self.env.ref('mrp_request.workorder_daily_wizard_action').read()[0]
        return action
    
    @api.onchange('scanner')
    def _onchange_qr_code(self):
       if self.scanner:
            return {
                'warning' : {
                    'title' : 'Success',
                    'message' : 'Hasil Scanner %s' % (self.scanner)
                }
            }

    @api.model
    def scan_is_start(self, mo_name):
        try:
            mo_obj = self.env['mrp.production'].search([('name', '=', mo_name)])
            user_id = self.env.user
            # wo_obj = self.env['mrp.workorder'].search([('workcenter_id', '=', user_id.workcenter_id.id), ('production_id', '=', mo_obj.id)], limit=1, order='name asc')
            # wo_obj = self.env['mrp.workorder'].search([('production_id', '=', mo_obj.id), ('inputed_wo_daily', '=', False)], limit=1, order='no_urut asc')
            # print("scan_is_start=========")
            # print(wo_obj.name)
            # if not wo_obj.date_planned_start:
            #     wo_obj.sudo().button_start()
            #     data = {
            #         'is_start': True,
            #         'workcenter_name': user_id.workcenter_id.name
            #     }
            #     return data
            # else:
            #     data = {
            #         'is_start': False,
            #         'workcenter_name': user_id.workcenter_id.name,
            #         'production_qty': wo_obj.production_qty,
            #         'actual_qty': wo_obj.actual_qty,
            #         'remaining_qty': wo_obj.production_qty - wo_obj.actual_qty
            #     }
            #     return data
            # wo_obj = self.env['mrp.workorder'].search([('production_id', '=', mo_obj.id), ('inputed_wo_daily', '=', False)], limit=1, order='no_urut asc')
            query = f"""
                select * from mrp_workorder where production_id = {mo_obj.id} and state <> 'done' order by name::INTEGER asc limit 1;
            """
            self._cr.execute(query)
            wo_obj = self._cr.dictfetchall()
            wo_id = self.env['mrp.workorder'].browse(wo_obj[0].get('id'))
            print('wo_iddddd', wo_id)

            list_parameter  = wo_id.parameter_ids.ids
            list_parameter_scanned  = wo_id.parameter_ids.filtered(lambda x: x.is_scanned).ids
            parameter_now = wo_id.parameter_ids.filtered(lambda x: not x.is_scanned).sorted(lambda x: x.sequence, reverse=False)[0].parameter_id.name
            # if not wo_id.date_planned_start:
            if not wo_id.date_planned_start:
                wo_id.sudo().button_start()
                data = {
                    'is_start': True,
                    'workcenter_name': wo_id.workcenter_id.name
                }
                return data 
            elif len(list_parameter) != len(list_parameter_scanned):
                data = {
                    'is_start': False,
                    'workcenter_name': wo_id.workcenter_id.name,
                    'production_qty': wo_id.production_qty,
                    'actual_qty': wo_id.actual_qty,
                    'remaining_qty': wo_id.production_qty - wo_id.actual_qty,
                    'workorder_id': wo_id.id,
                    'parameter': parameter_now
                }
                return data
        except Exception as e:
            print("===========Error scan_is_start========")
            print(e)
            return False

    @api.model
    def input_wo_daily(self, mo_name, machine_ids, qty, qty_rework, wo_daily_id, operator_id, parameter_id):
        try:
            mo_obj = self.env['mrp.production'].search([('name', '=', mo_name)])
            if mo_name:
                query = f"""
                    select * from mrp_workorder where production_id = {mo_obj.id} and state <> 'done' order by name::INTEGER asc limit 1;
                """
                self._cr.execute(query)
                wo_obj = self._cr.dictfetchall()
                wo_id = self.env['mrp.workorder'].browse(wo_obj[0].get('id'))
                employee_id = self.env['hr.employee'].browse(operator_id)
                if parameter_id != 0:
                    parameter_id = self.env['mrp.parameter'].browse(parameter_id).id
                else:
                    # parameter_id = wo_id.parameter_ids.filtered(lambda x: x.is_scanned == False).sorted(lambda x: x.sequence, reverse=False)[0].parameter_id .id if wo_id.parameter_ids else False
                    parameter_id = wo_id.parameter_ids.filtered(lambda x: x.is_scanned == False).sorted(lambda x: x.sequence, reverse=False)[0].parameter_id.id if wo_id.parameter_ids else False
                wo_id.write({
                    'inputed_wo_daily': True,
                    'workorder_ids': [(0, 0, {
                        'date': fields.Date.today(),
                        'workcenter_id': wo_id.workcenter_id.id,
                        'employee_id': employee_id.id,
                        'product_uom_qty': qty,
                        'qty_rework': qty_rework,
                        'wo_daily_id': wo_daily_id,
                        'machine_ids': [(6, 0, list(machine_ids))],
                        # 'resource_calendar_ids': user_id.employee_id.resource_calendar_ids.id,
                        'parameter_id': parameter_id,
                        'is_rework': True if int(qty_rework) > 0 else False,
                    })]
                })  
                mo_obj.write({
                    'process_terkini': wo_id.workcenter_id.id,
                    'parameter_terkini': parameter_id
                })
                if parameter_id:
                    parameter_id = self.env['mrp.operation.template.line.parameter'].search([('workorder_id', '=', wo_id.id), ('parameter_id', '=', parameter_id)])
                    parameter_id.write({
                        'is_scanned' : True
                    })
                list_parameter  = wo_id.parameter_ids.ids
                list_parameter_scanned  = wo_id.parameter_ids.filtered(lambda x: x.is_scanned).ids
                if len(list_parameter) == len(list_parameter_scanned):
                    wo_id.button_done()
            return True
        except Exception as e:
            print("===========Error input_wo_daily========")
            print(e)
            return False

    @api.model
    def create(self, values):
        seq = self.env['ir.sequence'].next_by_code('workorder.daily.code')
        values['name'] = seq
        result = super(WorkorderDaily, self).create(values)
        return result

    @api.model
    def create_wo_daily(self, badge):
        print('=========create_wo_daily=========')
        employee_id = self.env['hr.employee'].search([('barcode', '=', badge)])
        wod_obj = self.search([('employee_id', '=', employee_id.id), ('date', '<=', fields.Date.today()), ('date', '>=', fields.Date.today())])
        if not wod_obj:
            wod_obj = wod_obj.create({
                'date': fields.Date.today(),
                'employee_id': employee_id.id
            })
        data = {
                'wo_id': wod_obj.id,
                'name': wod_obj.name,
                'date': wod_obj.date,
                'employee_id': employee_id.name
            }
        return data

    @api.model
    def get_machine(self, workorder_id):
        workorder_obj = self.env['mrp.workorder'].browse(workorder_id)
        return workorder_obj.workcenter_id.machine_ids.ids
        
    @api.model
    def get_parameter(self, workorder_id):
        workorder_obj = self.env['mrp.workorder'].browse(workorder_id)
        return workorder_obj.parameter_ids.filtered(lambda x: not x.is_scanned).mapped('parameter_id.id')

    @api.model
    def scan_setter_machine(self, badge, no_mo, machine_id, time):
        print(badge)
        print(no_mo)
        # print(machine)
        print(time)
        user_id = self.env.user
        mo_obj = self.env['mrp.production'].search([('name', '=', no_mo)])
        wo_obj = self.env['mrp.workorder'].search([('workcenter_id', '=', user_id.workcenter_id.id), ('production_id', '=', mo_obj.id)])
        employee_id = self.env['hr.employee'].search([('barcode', '=', badge)])
        # machine_obj = self.env['mrp.machine'].search([('name', '=', machine)])
        sm_obj = self.env['setting.machine']
        sm = sm_obj.search([('employee_id', '=', employee_id.id), ('workorder_id', '=', wo_obj.id)])
        if sm:
            sm.write({
                'machine_id': machine_id,
                'time_setting': time,
                'employee_id': employee_id.id,
                'workorder_id': wo_obj.id
            })
        else:
            sm_obj.create({
                'machine_id': machine_id,
                'time_setting': time,
                'employee_id': employee_id.id,
                'workorder_id': wo_obj.id
            })

