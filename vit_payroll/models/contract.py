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

class HRContract(models.Model):
    _inherit = "hr.contract"

    t_jabatan = fields.Float('Tj Jabatan')
    t_fungsional = fields.Float('Tj Fungsional')
    t_komunikasi = fields.Float('Tj Komunikasi')
    t_transport = fields.Float('Tj Transport')
    t_makan = fields.Float('Tj Makan')
    t_luar_kota = fields.Float('Tj Harian Luar Kota')
    t_kendaraan_dinas = fields.Float('Tj Kendaraan Dinas')
    t_masa_kerja = fields.Float('Tj Masa Kerja')
    t_kost = fields.Float('Tj Kost')
    potongan_sukarela = fields.Float('Potongan Sukarela')
    potongan_inhealth = fields.Float('Potongan Inhealth')
    potongan_zakat = fields.Boolean('Zakat Profesi (2.5%)')
    potongan_makan = fields.Float('Potongan Tj Makan')
    bpjs_ketenagakerjaan = fields.Float('BPJS Ketenagakerjaan')
    bpjs_kesehatan = fields.Float('BPJS Kesehatan')

HRContract()