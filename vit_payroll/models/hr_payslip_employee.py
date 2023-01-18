# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017  Odoo SA  (http://www.vitraining.com)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Hr_payslip_employee(models.TransientModel):
    _name = 'hr.payslip.employees'
    _inherit = "hr.payslip.employees"

    def _get_active_journal(self):
        context = self.env.context
        if context.get('active_model') == 'hr.payslip.run':
            payslip = context.get('active_id', False)
            jurnal_id = self.env['hr.payslip.run'].search([('id','=',payslip)]).jurnal_id
            if jurnal_id:
                return jurnal_id.id
        return False

    jurnal_id = fields.Many2one('account.journal', string="Cara Bayar", default=_get_active_journal)

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees', domain='[("jurnal_id","=",jurnal_id)]')