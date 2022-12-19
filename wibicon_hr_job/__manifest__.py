# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 wibicon.com.
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
    "name": "HR Job",
    "version": "0.1",
    "author": "wibicon.com",
    "category": "HR",
    "website": "www.wibicon.com",
    "license": "AGPL-3",
    "summary": "",
    "description": """
   * Proteksi untuk maksimal rekrutmen karyawan untuk setiap posisi jabatan
""",
    "depends": ["base",
                "hr",
                "hr_recruitment",],
    "data":[
        # "security/ir.model.access.csv",
        # "views/hr_applicant.xml",
        # "views/hr_job.xml",
        "views/hr_employee.xml",
        ],
    "demo": [],
    "test": [],
    "installable": True,
    "auto_install": True,
    "application": True,
}