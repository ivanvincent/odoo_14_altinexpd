# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta


class HrReporting(models.TransientModel):
    _name = 'hr.reporting.wizard'
    _description = 'Generate payslips for all selected employees'

    name = fields.Char(required=True, translate=True)
    date_start = fields.Date(string="Start date", required=True)
    date_end = fields.Date(string="End date", required=True)

    def action_generate_pdf(self):
        date_start_tmp  = datetime.strptime(self.date_start.strftime('%Y-%m-%d') + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        date_start      = date_start_tmp - timedelta(hours=7)
        
        date_end_tmp    = datetime.strptime(self.date_end.strftime('%Y-%m-%d') + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        date_end        = date_end_tmp - timedelta(hours=7)

        # % (date_start, date_end, self.kelompok)

        # self._cr.execute(query)
        # result = self._cr.dictfetchall()
        
        data = {
            'me': self,
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                # 'data' : result,
            },
        }
        return self.env.ref('sh_hr_payroll.action_report_salary_bpjs').report_action(None, data=data)

class HrReporting(models.AbstractModel):
    _name = 'report.sh_hr_payroll.report_salary_to_bpjs'

    @api.model
    def _get_report_values(self, docids, data=None):
        # print('_get_report_values')
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        return {
            'date_start': date_start,
            'date_end': date_end,
        }