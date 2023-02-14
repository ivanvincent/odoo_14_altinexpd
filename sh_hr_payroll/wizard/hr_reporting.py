# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta

_STATE =[("bpjs", "Laporan Gaji pada BPJS"),
         ("gs", "Laporan Gaji pada GS"),
]

class HrReporting(models.TransientModel):
    _name = 'hr.reporting.wizard'
    _description = 'Generate payslips for all selected employees'

    date_start = fields.Date(string="Start date", required=True)
    date_end = fields.Date(string="End date", required=True)
    report_type     = fields.Selection(selection=_STATE, string='Report Type',default="bpjs")

    def action_generate_pdf(self):

        if self.report_type == 'bpjs': 
            query =f"""
            SELECT he.name, sum(payslip.total_gapok) as total_gapok, sum(payslip.KES) as total_kes
            FROM (
                    SELECT hpl.code, hpl.total as total_gapok, 0 as KES, hp.employee_id
                    FROM
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
                    WHERE hpl.code = 'GAPOK'
                    AND hp.date_from >= '{self.date_start}' AND hp.date_to <= '{self.date_start}' 

                    UNION
                    SELECT hpl.code, 0 as total_gapok, hpl.total as KES, hp.employee_id as karyawan
                    FROM 
                    hr_payslip hp left join hr_payslip_line hpl on hpl.slip_id = hp.id
                    WHERE hpl. code = 'KES'
                    AND hp.date_from >= '{self.date_start}' AND hp.date_to <= '{self.date_start}'
                ) AS payslip 
            left join hr_employee he on he.id = payslip.employee_id
            GROUP BY he.name
            """ 
            print("action_print")
            self._cr.execute(query)
            record = self._cr.dictfetchall()
            
            data = {
                'me': self,
                'ids': self.ids,
                'model': self._name,
                'form': {
                    'date_start': self.date_start,
                    'date_end': self.date_end,
                    'record' : record,
                },
            }
            return self.env.ref('sh_hr_payroll.action_report_salary_bpjs').report_action(None, data=data)

        elif self.report_type == 'gs': 
            data = {
                'me': self,
                'ids': self.ids,
                # 'model': self._name,
                'form': {
                    'date_start': self.date_start,
                    'date_end': self.date_end,
                    # 'data' : result,
                },
            }
            return self.env.ref('sh_hr_payroll.action_report_salary_gs').report_action(None, data=data)

class HrReportingBpjs(models.AbstractModel):
    _name = 'report.sh_hr_payroll.report_salary_bpjs'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('_get_report_values')
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        record = data['form']['record']
        return {
            'me': self,
            'date_start': date_start,
            'date_end': date_end,
            'doc_ids': data['ids'],
            'docs': record,
            
        }

class HrReportingGS(models.AbstractModel):
    _name = 'report.sh_hr_payroll.report_salary_gs'

    @api.model
    def _get_report_values(self, docids, data=None):
        # print('_get_report_values')
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        return {
            'date_start': date_start,
            'date_end': date_end,
        }