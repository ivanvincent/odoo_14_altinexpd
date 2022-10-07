from odoo import fields, models, api, _
from odoo.exceptions import UserError

class WorkorderDailyWizard(models.TransientModel):
    _name = 'workorder.daily.wizard'

    employee_id = fields.Many2one('hr.employee', string='Operator')
    date        = fields.Date(string='Date', default=fields.Date.today())
    workcenter_id = fields.Many2one('mrp.workcenter', string='Workcenter')
    quantity    = fields.Float(string='Quantity')
    scanner     = fields.Char('Scanner')
    machine_id  = fields.Many2one('mrp.machine', string='Machine')

    def action_confirm(self):
        print('action_confirm')
        ctx = self.env.context
        active_id = ctx.get('active_id')
        me_workcenter = self.env.user.workcenter_id.id
        workorder = self.env['mrp.workorder'].search([('production_id.name','=', self.scanner), ('workcenter_id', '=', me_workcenter)])
        workorder.write({
            'workorder_ids': [(0, 0, {
                'date': fields.Date.today(),
                'workcenter_id': me_workcenter,
                'employee_id': self.employee_id.id,
                'product_uom_qty': self.quantity,
                'wo_daily_id': active_id,
                'machine_id': self.machine_id,
            })]
        })

    @api.model
    def barcode_scan(self, barcode, active_id):
        print('barcode', barcode)
        print('active_id', active_id)
        print('barcode_scan asdnfladnfasdf')
        self.scanner = barcode
    
    @api.onchange('scanner')
    def _onchange_qr_code(self):
        print('_onchange_qr_code')
        # if self.scanner:
        #     return {
        #         'warning' : {
        #             'title' : 'Success',
        #             'message' : 'Hasil Scanner %s' % (self.scanner)
        #         }
        #     }
