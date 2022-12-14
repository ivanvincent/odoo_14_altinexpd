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
{
    "name": "Garment Payroll",
    "version": "0.1",
    "category": "Payroll",
    "sequence": 20,
    "author":  "vITraining",
    "website": "www.vitraining.com",
    "license": "AGPL-3",
    "summary": "",
    "description": """

Payroll for Shafira Corporation

    """,
    "depends": [
        "base",
        "hr_contract",
        "hr_payroll",
        "hr_attendance",
        "hr_holidays",
        "vit_rolling_shift",
        "vit_hrd_common",
        "vit_attendance",
        "vit_overtime",
        "vit_hr_spg",
    ],
    "data": [
        "views/contract.xml",
        "views/hr_payslip_run.xml",
        "views/hr_payslip_employee.xml",
        "views/hr_payslip.xml",
        "data/salary_structure.xml",
        "reports/payslip_report.xml",
    ],

    "demo": [
    ],

    "test": [
    ],

    "installable": True,
    "auto_install": False,
    "application": True,
}