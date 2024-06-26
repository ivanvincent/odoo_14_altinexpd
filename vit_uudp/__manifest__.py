# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 vitraining.com.
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
    "name": "Pengajuan Dana dan Reimberse",
    "version": "2.9",
    "author": "vitraining.com",
    "category": "Extra Tools",
    "website": "www.vitraining.com",
    "license": "AGPL-3",
    "summary": "",
    "description": """
   * Ajuan dana
   * Reimbersement
   * Pencairan dana / reimberse
   * Penyelesaian / pertanggungjawaban dana
   * Tidak ada jurnal terkait bank / cash
""",
    "depends": ["base","analytic",
                "account",
                "hr",
                "product",
                # "hr_expense",
                "do_head_office",
                # "inherit_purchase_order"
                ],
    "data":[
        "security/group.xml",
        "security/ir.model.access.csv",
        "security/uudp_sequence.xml",
        "views/uudp.xml",
        "views/res_config_setting.xml",
        "views/hr_department.xml",
        "views/res_users.xml",
        "views/product.xml",
        # "views/rute_sale.xml",
        "views/expense_template_combine.xml",
        "views/report_uudp.xml",
        "views/do_head_office.xml",
        "wizard/reimburse_wizard.xml",
        "wizard/pengajuan_wizard.xml",
        "wizard/penyelesaian_wizard.xml",
        "wizard/expense_template_combine_wizard.xml",
        "wizard/penyelesaian_excel_wizard.xml",
        "report/laporan_penyelesaian.xml",
        "data/data.xml",
        ],
    "demo": [],
    "qweb": [],
    "test": [],
    "installable": True,
    "auto_install": False,
    "application": True,
}