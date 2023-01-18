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

from odoo import api, fields, models, _, SUPERUSER_ID
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Hr_payslip_run(models.Model):
    _name = 'hr.payslip.run'
    _inherit = "hr.payslip.run"

    date_start = fields.Date(string='Date From', required=True, readonly=True,
        states={'draft': [('readonly', False)]}, default=str(datetime.now()+ relativedelta(months=-1, day=21)))

    date_end = fields.Date(string='Date To', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        default=time.strftime('%Y-%m-20'))

    slip_ids = fields.One2many('hr.payslip', 'payslip_run_id', string='Payslips', readonly=True,
        states={'draft': [('readonly', False)]})

    jurnal_id = fields.Many2one('account.journal', string="Cara Bayar", domain="['|',('type', '=', 'cash'),('type', '=', 'bank')]", readonly=True,
        states={'draft': [('readonly', False)]}, required=True,)

    
    def action_compute_all(self):
        for slip in self.slip_ids :
            slip.compute_sheet()
        return {}