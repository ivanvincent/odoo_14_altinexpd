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
        print('====== scan_is_start ====')
        mo_obj = self.env['mrp.production'].search([('name', '=', mo_name)])
        user_id = self.env.user
        wo_obj = self.env['mrp.workorder'].search([('workcenter_id', '=', user_id.workcenter_id.id), ('production_id', '=', mo_obj.id)])
        if not wo_obj.date_planned_start:
            wo_obj.sudo().button_start()
            data = {
                'is_start': True,
                'workcenter_name': user_id.workcenter_id.name
            }
            return data
        else:
            data = {
                'is_start': False,
                'workcenter_name': user_id.workcenter_id.name,
                'production_qty': wo_obj.production_qty,
                'actual_qty': wo_obj.actual_qty,
                'remaining_qty': wo_obj.production_qty - wo_obj.actual_qty
            }
            return data

    @api.model
    def input_wo_daily(self, mo_name, machine_id, qty, qty_rework, wo_daily_id):
        print('================input_wo_daily==========')
        user_id = self.env.user
        mo_obj = self.env['mrp.production'].search([('name', '=', mo_name)])
        machine_obj = self.env['mrp.machine'].browse(machine_id)
        if mo_name and user_id:
            wo_obj = self.env['mrp.workorder'].search([('workcenter_id', '=', user_id.workcenter_id.id), ('production_id', '=', mo_obj.id)])
            wo_obj.write({
                'workorder_ids': [(0, 0, {
                    'date': fields.Date.today(),
                    'workcenter_id': user_id.workcenter_id.id,
                    'employee_id': user_id.employee_id.id,
                    'product_uom_qty': qty,
                    'qty_rework': qty_rework,
                    'wo_daily_id': wo_daily_id,
                    'machine_id': machine_obj.id,
                    'resource_calendar_ids': user_id.employee_id.resource_calendar_ids.id,
                    'is_rework': True if int(qty_rework) > 0 else False,
                })]
            })
            if wo_obj.production_qty == wo_obj.actual_qty:
                wo_obj.button_done()

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
    def get_machine(self):
        print('==========get_action========')
        _logger.warning('==========get_action========')
        user = self.env.user
        _logger.warning(user.workcenter_id.machine_ids.ids)
        return user.workcenter_id.machine_ids.ids

    @api.model
    def scan_setter_machine(self, badge, no_mo, machine, time):
        print(badge)
        print(no_mo)
        print(machine)
        print(time)
        user_id = self.env.user
        mo_obj = self.env['mrp.production'].search([('name', '=', no_mo)])
        wo_obj = self.env['mrp.workorder'].search([('workcenter_id', '=', user_id.workcenter_id.id), ('production_id', '=', mo_obj.id)])
        employee_id = self.env['hr.employee'].search([('barcode', '=', badge)])
        machine_obj = self.env['mrp.machine'].search([('name', '=', machine)])
        sm_obj = self.env['setting.machine']
        sm = sm_obj.search([('employee_id', '=', employee_id.id), ('workorder_id', '=', wo_obj.id)])
        if sm:
            sm.write({
                'machine_id': machine_obj.id,
                'time_setting': time,
                'employee_id': employee_id.id,
                'workorder_id': wo_obj.id
            })
        else:
            sm_obj.create({
                'machine_id': machine_obj.id,
                'time_setting': time,
                'employee_id': employee_id.id,
                'workorder_id': wo_obj.id
            })

