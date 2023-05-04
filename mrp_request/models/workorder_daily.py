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
                select * from mrp_workorder where production_id = {mo_obj.id} and inputed_wo_daily = false order by name::INTEGER asc limit 1;
            """
            self._cr.execute(query)
            wo_obj = self._cr.dictfetchall()
            wo_id = self.env['mrp.workorder'].browse(wo_obj[0].get('id'))
            if not wo_id.date_planned_start:
                wo_id.sudo().button_start()
                data = {
                    'is_start': True,
                    'workcenter_name': wo_id.workcenter_id.name
                }
                return data
            else:
                data = {
                    'is_start': False,
                    'workcenter_name': wo_id.workcenter_id.name,
                    'production_qty': wo_id.production_qty,
                    'actual_qty': wo_id.actual_qty,
                    'remaining_qty': wo_id.production_qty - wo_id.actual_qty,
                    'workcenter_id': wo_id.workcenter_id.id
                }
                return data
        except Exception as e:
            print("===========Error scan_is_start========")
            print(e)
            return False

    @api.model
    def input_wo_daily(self, mo_name, machine_id, qty, qty_rework, wo_daily_id):
        try:
            user_id = self.env.user
            mo_obj = self.env['mrp.production'].search([('name', '=', mo_name)])
            machine_obj = self.env['mrp.machine'].browse(machine_id)
            # if mo_name:
            #     # wo_obj = self.env['mrp.workorder'].search([('workcenter_id', '=', user_id.workcenter_id.id), ('production_id', '=', mo_obj.id)], limit=1, order='name asc')
            #     wo_obj = self.env['mrp.workorder'].search([('production_id', '=', mo_obj.id), ('state', '=', 'progress')], limit=1, order='name asc')
            #     print("input_wo_daily========")
            #     print(wo_obj.name)
            #     sdnflsdks
            #     wo_obj.write({
            #         'inputed_wo_daily': True,
            #         'workorder_ids': [(0, 0, {
            #             'date': fields.Date.today(),
            #             'workcenter_id': user_id.workcenter_id.id,
            #             'employee_id': user_id.employee_id.id,
            #             'product_uom_qty': qty,
            #             'qty_rework': qty_rework,
            #             'wo_daily_id': wo_daily_id,
            #             'machine_id': machine_obj.id,
            #             'resource_calendar_ids': user_id.employee_id.resource_calendar_ids.id,
            #             'is_rework': True if int(qty_rework) > 0 else False,
            #         })]
            #     })

            #     if wo_obj.production_qty == wo_obj.actual_qty:
            #         wo_obj.button_done()
            # return True
            if mo_name:
                # wo_obj = self.env['mrp.workorder'].search([('workcenter_id', '=', user_id.workcenter_id.id), ('production_id', '=', mo_obj.id)], limit=1, order='name asc')
                # wo_obj = self.env['mrp.workorder'].search([('production_id', '=', mo_obj.id), ('state', '=', 'progress')], limit=1, order='name asc')
                query = f"""
                    select * from mrp_workorder where production_id = {mo_obj.id} and state = 'progress' order by name::INTEGER asc limit 1;
                """
                self._cr.execute(query)
                wo_obj = self._cr.dictfetchall()
                wo_id = self.env['mrp.workorder'].browse(wo_obj[0].get('id'))
                # print("input_wo_daily========")
                # print(wo_obj.name)
                # sdnflsdks
                wo_id.write({
                    'inputed_wo_daily': True,
                    'workorder_ids': [(0, 0, {
                        'date': fields.Date.today(),
                        'workcenter_id': wo_id.workcenter_id.id,
                        # 'employee_id': user_id.employee_id.id,
                        'product_uom_qty': qty,
                        'qty_rework': qty_rework,
                        'wo_daily_id': wo_daily_id,
                        # 'machine_ids': machine_obj.id,
                        # 'resource_calendar_ids': user_id.employee_id.resource_calendar_ids.id,
                        'parameter_id': wo_id.parameter_ids.filtered(lambda x: x.is_scanned == False).sorted(lambda x: x.sequence, reverse=True)[0].parameter_id.id,
                        'is_rework': True if int(qty_rework) > 0 else False,
                    })]
                })  
                if wo_id.production_qty == wo_id.actual_qty:
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
                'employee_id': employee_id.id
            }
        return data

    @api.model
    def get_machine(self, workcenter_id):
        print('==========get_action========')
        _logger.warning('==========get_action========')
        workcenter_obj = self.env['mrp.workcenter'].browse(workcenter_id)
        _logger.warning(workcenter_obj.workcenter_id.machine_ids.ids)
        return workcenter_obj.machine_ids.ids

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

