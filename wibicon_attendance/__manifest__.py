# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017  Odoo SA  (http://www.wibicon.com)
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
    "name": "HR Employee Attendances",
    "version": "0.1",
    "category": "Extra Tools",
    "sequence": 16,
    "author":  "wibicon",
    "website": "https://wibicon.com",
    "license": "AGPL-3",
    "summary": "",
    "description": """

    """,
    "depends": [
        "base",
        # "hr",
        "hr_recruitment",
        "hr_contract",
        "wibicon_hr",
        "hr_attendance",
    ],
    "data": [
        "security/ir.model.access.csv",
        # "data/cron.xml",
        "views/employee_attendance.xml",
        # "views/hr_attendance.xml",
        "views/absen_from_finger_print.xml",
        # "static/src/xml/tree_view_asset.xml",
        "wizard/wizard_absence_periode.xml",
        "wizard/wizard_export_absent.xml"
    ],


    "demo": [
    ],

    "test": [
    ],
    'qweb': [
        # 'static/src/xml/button.xml'
        ],

    "installable": True,
    "auto_install": False,
    "application": True,
}
