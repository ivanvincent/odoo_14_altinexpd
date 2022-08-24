from odoo import models, fields, api

class WorkorderDaily(models.Model):
    _name = 'workorder.daily'

    name        = fields.Char(string='Name')
    employee_id = fields.Many2one('hr.employee', string='Operator',)
    date        = fields.Date(string='Date', default=fields.Date.today())
    mrp_workorder_line_ids = fields.One2many('mrp.workorder.line', 'wo_daily_id', 'Line')

    @api.model
    def barcode_scan(self, active_id):
        action = self.env.ref('mrp_request.workorder_daily_wizard_action').read()[0]
        return action