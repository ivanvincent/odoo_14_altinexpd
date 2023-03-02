from odoo import fields, models, api, _
from odoo.exceptions import UserError

class LaporanShiftTigaWizard(models.TransientModel):
    _name = 'laporan.shift.tiga.wizard'

    date_start = fields.Date(string='Date Start', required=True, )
    date_end = fields.Date(string='Date End', required=True, )

    def action_generate(self):        
        action = self.env.ref('inherit_hr.hr_attendance_pivot_shift_3_action').read()[0]        
        action['domain'] = [('shift_3_counter', '>', 0), ('check_in', '>=', self.date_start),
                            ('check_in', '<=', self.date_end)]
        return action