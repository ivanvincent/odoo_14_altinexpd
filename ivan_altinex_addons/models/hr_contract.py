from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pandas as pd

class HrContract(models.Model):
    _inherit = 'hr.contract'

    wage = fields.Monetary('Gaji', required=True, tracking=True, readonly=True, compute="_compute_wage_grade", help="Employee's monthly gross wage.")
    tunjangan_keahlian = fields.Monetary(string="Tunjangan Keahlian", readonly=True, compute="_compute_skill_grade")
    iuran_pensiun = fields.Monetary(string="Iuran Pensiun")
    years_of_service = fields.Float('Years Of Service', compute="_compute_year_of_service")
    alokasi_izin_sakit = fields.Float(string = 'Izin Sakit', default = 14.0, readonly=True)
    alokasi_izin_normatif = fields.Float(string = 'Izin Normatif', default = 3.0, readonly=True)
    alokasi_izin_maternity = fields.Float(string = 'Izin Maternity', compute = "_compute_maternity_paternity_leaves")
    alokasi_izin_paternity = fields.Float(string = 'Izin Paternity', compute = "_compute_maternity_paternity_leaves")
    alokasi_cuti = fields.Float(string='Cuti Tahunan', compute="_compute_jatah_cuti")
    wage_id = fields.Many2one('hr.wage_grade', string='Wage Grade')
    skill_id = fields.Many2one('hr.skill_grade', string='Skill Grade')
    allocations_ids = fields.One2many('hr.leave.allocation', 'contract_id', 'Allocations Line')
    
    @api.depends('first_contract_date')
    def _compute_year_of_service(self):
        if self.first_contract_date:
            selisih = fields.Date.today() - self.first_contract_date
            lama_kerja_sec = selisih.total_seconds()
            lama_kerja_year = lama_kerja_sec / 31536000
            self.years_of_service = lama_kerja_year
        else:
            self.years_of_service = False

    @api.depends('employee_id')
    def _compute_maternity_paternity_leaves(self):
        data_karyawan = self.env['hr.employee'].search([('id','=',self.employee_id.id)])
        gender = data_karyawan.gender
        marital = data_karyawan.marital

        if (gender == "male") and (marital == "married"):
            self.alokasi_izin_maternity = 0.0
            self.alokasi_izin_paternity = 3.0
        elif (gender == "female") and (marital == "married"):
            self.alokasi_izin_maternity = 90.0
            self.alokasi_izin_paternity = 0.0
        else:
            self.alokasi_izin_maternity = 0.0
            self.alokasi_izin_paternity = 0.0

    @api.depends('type_id','years_of_service')
    def _compute_jatah_cuti(self):
        cuti = 0.0
        employee_id = self.employee_id.id
        employee_type = self.type_id.id
        if employee_type == 5:
            cuti = 12.0
        elif employee_type == 4:
            if self.years_of_service <= 1:
               cuti = 12.0
            elif self.years_of_service >= 1 and self.years_of_service < 2:
                cuti = 12.0
            elif self.years_of_service >= 2 and self.years_of_service < 3:
                cuti = 13.0
            elif self.years_of_service >= 3 and self.years_of_service < 5:
                cuti = 14.0
            elif self.years_of_service >= 5 and self.years_of_service < 8:
                cuti = 16.0
            elif self.years_of_service >= 8:
                cuti = 18.0    
        else:
            cuti = 0.0
        # isi jatah cuti sesui type karyawan (tetap / kontrak) dan lama kerja
        self.alokasi_cuti = cuti

        # alokasi hari cuti ke modul time off (hr.leave.allocation)
        time_off_data = self.env['hr.leave.allocation'].search([('employee_id','=',employee_id)])
        if time_off_data:
            # jika record sudah tersedia, periksa jenis cuti / izin
            # jika field holiday_status_id == cuti tahun berjalan, maka pass
            # jika bukan, maka tambahkan jatah cuti tahun berjalan sebanyak var cuti
            print(time_off_data)
        else:
            # jika record tidak tersedia, maka langsung tambahkan jatah cuti tahun berjalan sebanyak var cuti
            print("data cuti tidak tersedia")

    @api.depends('wage_id')
    def _compute_wage_grade(self):
        self.wage = self.wage_id.gapok
    
    @api.depends('skill_id')
    def _compute_skill_grade(self):
        self.tunjangan_keahlian = self.skill_id.tunj_ahli

    @api.model
    def create(self, values):
        employee_id = values.get('employee_id')
        dict_izin_sakit = {
                            'name': 'Izin sakit',
                            'holiday_status_id': 5,
                            'holiday_type': 'employee',
                            'employee_id': employee_id
                        }
        values['allocations_ids'] = [(0, 0, dict_izin_sakit)]
        result = super(HrContract).create(values)

        return result
    
class WageGrade(models.Model):
    _name = 'hr.wage_grade'
    _rec_name ='wage_grade'
    _description = 'wage grade master'

    wage_grade = fields.Char(string='Wage Grade')
    gapok = fields.Float(string = 'Gaji Pokok')
    notes = fields.Text('Notes')

class SkillGrade(models.Model):
    _name = 'hr.skill_grade'
    _rec_name = 'skill_grade'
    _description = 'skill grade master'

    skill_grade = fields.Char(string='Skill Grade')
    tunj_ahli = fields.Float(string='Tunjangan Keahlian/hari')

