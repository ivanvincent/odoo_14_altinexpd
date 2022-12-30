from odoo import models, fields, api
from datetime import datetime
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
            wo_obj.button_start()
            return True
        else:
            return False

    @api.model
    def input_wo_daily(self, mo_name, machine_name, shift, qty, wo_daily_id):
        try:
            user_id = self.env.user
            mo_obj = self.env['mrp.production'].search([('name', '=', mo_name)])
            machine_obj = self.env['mrp.machine'].search([('name', '=', machine_name)])
            if mo_name and user_id:
                wo_obj = self.env['mrp.workorder'].search([('workcenter_id', '=', user_id.workcenter_id.id), ('production_id', '=', mo_obj.id)])
                wo_obj.write({
                    'workorder_ids': [(0, 0, {
                        'date': fields.Date.today(),
                        'workcenter_id': user_id.workcenter_id.id,
                        'employee_id': user_id.employee_id.id,
                        'product_uom_qty': qty,
                        'wo_daily_id': wo_daily_id,
                        'machine_id': machine_obj.id,
                    })]
                })
                if wo_obj.production_qty == wo_obj.actual_qty:
                    wo_obj.button_done()
                return "Data berhasil diinput"
        except Exception as e:            
            return e
            print(e)

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
            wod_obj.create({
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
        else:
            data = {
                    'wo_id': wod_obj.id,
                    'name': wod_obj.name,
                    'date': wod_obj.date,
                    'employee_id': employee_id.id
                }
            return data
