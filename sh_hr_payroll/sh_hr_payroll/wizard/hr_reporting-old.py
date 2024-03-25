# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
import logging
logger = logging.getLogger(__name__)


_STATE =[("bpjs", "Laporan Gaji pada BPJS"),
         ("gs", "Laporan Gaji pada GS"),
]

class HrReporting(models.TransientModel):
    _name = 'hr.reporting.wizard'
    _description = 'Generate payslips for all selected employees'

    current_year = datetime.now().year
    date_start = fields.Date(string="Start date", required=False)
    date_end = fields.Date(string="End date", required=False)
    report_type     = fields.Selection(selection=_STATE, string='Report Type',default="bpjs")
    month_selection = fields.Selection([
                        ("01","Januari %s" % current_year),   
                        ("02","Februari %s" % current_year),
                        ("03","Maret %s" % current_year),
                        ("04","April %s" % current_year),
                        ("05","Mei %s" % current_year),
                        ("06","Juni %s" % current_year),
                        ("07","Juli %s" % current_year),
                        ("08","Agustus %s" % current_year),
                        ("09","September %s" % current_year),
                        ("10","Oktober %s" % current_year),
                        ("11","November %s" % current_year),
                        ("12","Desember %s" % current_year),
                        ],string='Month Selection')
    job_ids = fields.Many2many('hr.job', string='Access Job', compute='compute_job_ids', compute_sudo=True)

	
	
    def action_generate_pdf(self):
	    record = self.query()
	    data = {
			'me': self,
			'ids': self.ids,
			'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'month_selection': self.month_selection,
                'record' : record,
            },
        }
		if self.report_type == 'bpjs': 
			return self.env.ref('sh_hr_payroll.action_report_salary_bpjs').report_action(None, data=data)
		else:
			return self.env.ref('sh_hr_payroll.action_report_salary_gs').report_action(None, data=data)

    @api.depends('report_type')
    def compute_job_ids(self):
        manajer_payroll = self.env['res.groups'].sudo().browse(240)
        payroll_staff = self.env['res.groups'].sudo().browse(241)
        payroll_spv = self.env['res.groups'].sudo().browse(244)
        uid = self.env.user.id
        if uid in manajer_payroll.users.ids:
            rule = manajer_payroll.rule_groups.filtered(lambda x: x.model_id.name == 'Pay Slip')
        elif uid in payroll_staff.users.ids:
            rule = payroll_staff.rule_groups.filtered(lambda x: x.model_id.name == 'Pay Slip')
        elif uid in payroll_spv.users.ids:
            rule = payroll_spv.rule_groups.filtered(lambda x: x.model_id.name == 'Pay Slip')
        else:
            self.job_ids = [(6, 0, [])]
            return
        job_ids = rule.domain_force.split(",'in',")[1].replace(")])", "")
        for rec in self:
            rec.job_ids = [(6, 0, list(map(int, job_ids[1:-1].split(','))) if job_ids else [])]
    
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