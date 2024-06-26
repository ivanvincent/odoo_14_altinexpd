# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Anusha (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import models


class MassConfirmPayslip(models.TransientModel):
    _name = 'payslip.confirm'
    _description = 'Mass Confirm Payslip'

    def confirm_payslip(self):
        """Mass Confirmation of Payslip"""
        context = self._context
        record_ids = context.get('active_ids', [])
        for each in record_ids:
            payslip_id = self.env['hr.payslip'].search([('id', '=', each),
                                                        ('state', 'not in', ['cancel', 'done'])])
            if payslip_id:
                payslip_id.action_payslip_done()
                
class MassSetDraftPayslip(models.TransientModel):
    _name = 'payslip.set_draft'
    _description = 'Mass Set to Draft Payslip'

    def set_draft_payslip(self):
        """Mass Set To Draft of Payslip"""
        context = self._context
        record_ids = context.get('active_ids', [])
        for each in record_ids:
            payslip_id = self.env['hr.payslip'].search([('id', '=', each),
                                                        ('state', 'not in', ['cancel', 'draft'])])
            if payslip_id:
                payslip_id.state = 'draft'
                # payslip_id.state = 'draft'

