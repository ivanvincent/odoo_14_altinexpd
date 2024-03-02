from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
import pandas as pd

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),  # YTI This state seems to be unused. To remove
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved'),
        ('expired', 'Expired')
        ], string='Status', compute='_compute_state', store=True, tracking=True, copy=False, readonly=False,
        help="The status is set to 'To Submit', when a time off request is created." +
        "\nThe status is 'To Approve', when time off request is confirmed by user." +
        "\nThe status is 'Refused', when time off request is refused by manager." +
        "\nThe status is 'Approved', when time off request is approved by manager." +
        "\nThe status is 'Expired', when time off request is expired in the previous year.")

class HrContract(models.Model):
    _inherit = 'hr.contract'

    wage = fields.Monetary('Gaji', required=True, tracking=True, readonly=True, compute="_compute_wage_grade", help="Employee's monthly gross wage.")
    gapok_bpjs_kes = fields.Monetary('Gapok BPJS Kes',tracking=True, help="Gaji Pokok untuk kepentingan BPJS Kesehatan.")
    gapok_bpjs_tk = fields.Monetary('Gapok BPJS TK',tracking=True, help="Gaji Pokok untuk kepentingan BPJS TK.")
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
    alokasi_izin = fields.Float(string='alokasi_izin') #sementara
    is_reseted = fields.Boolean(string='Reset ?', default=False)
    # tax_tarif_id = fields.Many2one('hr.tax_tarif', string="Tax Tarif")
    
    
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
        hari_izin_sakit = 14
        hari_izin_normatif = 3
        data_karyawan = self.env['hr.employee'].search([('id','=',employee_id)])
        gender = data_karyawan.gender
        marital = data_karyawan.marital

        if (gender == "male") and (marital == "married"):
            alokasi_izin_maternity = 0.0
            alokasi_izin_paternity = 3.0
        elif (gender == "female") and (marital == "married"):
            alokasi_izin_maternity = 90.0
            alokasi_izin_paternity = 0.0
        else:
            alokasi_izin_maternity = 0.0
            alokasi_izin_paternity = 0.0


        cuti = 0.0
        employee_type = values.get('type_id')
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

        dict_izin_sakit = {
                            'name': 'Izin Sakit',
                            'holiday_status_id': 5,
                            'holiday_type': 'employee',
                            'employee_id': employee_id,
                            'number_of_days' : hari_izin_sakit
                        }
        dict_izin_normatif = {
                            'name': 'Izin Normatif',
                            'holiday_status_id': 6,
                            'holiday_type': 'employee',
                            'employee_id': employee_id,
                            'number_of_days' : hari_izin_normatif
                        }
        dict_izin_maternity = {
                            'name': 'Izin Maternitas',
                            'holiday_status_id': 7,
                            'holiday_type': 'employee',
                            'employee_id': employee_id,
                            'number_of_days' : alokasi_izin_maternity
                        }
        dict_izin_paternity = {
                            'name': 'Izin Paternitas',
                            'holiday_status_id': 11,
                            'holiday_type': 'employee',
                            'employee_id': employee_id,
                            'number_of_days' : alokasi_izin_paternity
                        }
        dict_cuti = {
                            'name': 'Cuti Tahunan',
                            'holiday_status_id': 10,
                            'holiday_type': 'employee',
                            'employee_id': employee_id,
                            'number_of_days' : cuti
                        }
        values['allocations_ids'] = [(0, 0, dict_izin_sakit),(0, 0, dict_izin_normatif),(0, 0, dict_izin_maternity),(0, 0, dict_izin_paternity),(0, 0, dict_cuti)]
        result = super(HrContract, self).create(values)
        return result
    
    def update_allocation(self):
        if self.allocations_ids:
            for l in self.allocations_ids.filtered(lambda x: x.state != 'validate'):
                contract_id = l.contract_id
                if l.holiday_status_id.id == 5:
                    l.write({'number_of_days': contract_id.alokasi_izin_sakit})
                elif l.holiday_status_id.id == 6:
                    l.write({'number_of_days': contract_id.alokasi_izin_normatif})
                elif l.holiday_status_id.id == 7:
                    l.write({'number_of_days': contract_id.alokasi_izin_maternity})
                elif l.holiday_status_id.id == 11:
                    l.write({'number_of_days': contract_id.alokasi_izin_paternity})
                elif l.holiday_status_id.id == 10:
                    l.write({'number_of_days': contract_id.alokasi_cuti})
        else:
            dict_izin_sakit = {
                            'name': 'Izin Sakit',
                            'holiday_status_id': 5,
                            'holiday_type': 'employee',
                            'employee_id': self.employee_id.id,
                            'number_of_days' : self.alokasi_izin_sakit
                        }
            dict_izin_normatif = {
                                'name': 'Izin Normatif',
                                'holiday_status_id': 6,
                                'holiday_type': 'employee',
                                'employee_id': self.employee_id.id,
                                'number_of_days' : self.alokasi_izin_normatif
                            }
            dict_izin_maternity = {
                                'name': 'Izin Maternitas',
                                'holiday_status_id': 7,
                                'holiday_type': 'employee',
                                'employee_id': self.employee_id.id,
                                'number_of_days' : self.alokasi_izin_maternity
                            }
            dict_izin_paternity = {
                                'name': 'Izin Paternitas',
                                'holiday_status_id': 11,
                                'holiday_type': 'employee',
                                'employee_id': self.employee_id.id,
                                'number_of_days' : self.alokasi_izin_paternity
                            }
            dict_cuti = {
                                'name': 'Cuti Tahunan',
                                'holiday_status_id': 10,
                                'holiday_type': 'employee',
                                'employee_id': self.employee_id.id,
                                'number_of_days' : self.alokasi_cuti
                            }
            self.allocations_ids = [(0, 0, dict_izin_sakit),(0, 0, dict_izin_normatif),(0, 0, dict_izin_maternity),(0, 0, dict_izin_paternity),(0, 0, dict_cuti)]

    def action_reset_leave(self):
        
        today = date.today()
        this_year = today.year
        last_year = this_year - 1
        cut_off_str = str(last_year)+'-12-21'
        year_end_str = str(last_year)+'-12-31'
        cut_off_str2 = str(this_year)+'-01-20'

        cut_off_date = datetime.strptime(cut_off_str,'%Y-%m-%d').date()
        year_end_date = datetime.strptime(year_end_str,'%Y-%m-%d').date()
        cut_off_date2 = datetime.strptime(cut_off_str2,'%Y-%m-%d').date()
        leave = self.env['hr.leave'].search([('employee_id', '=', self.employee_id.id),
                                             ('state', '=', 'validate')])
        for l in leave:
            
            if(today <= year_end_date):
                l.state = 'validate'
            elif (today > year_end_date and today <= cut_off_date2):
                if (l.request_date_from <= cut_off_date):
                    l.state = 'expired'
                elif(l.request_date_from > cut_off_date and l.request_date_from <= cut_off_date2):
                    l.state = 'validate'
                else:
                    l.state = 'validate'
            else:
                if (l.request_date_from <= cut_off_date):
                    l.state = 'expired'
                elif(l.request_date_from > cut_off_date and l.request_date_from <= year_end_date):
                    l.state = 'expired'
                else:
                    l.state = 'validate'
            
            # l.action_refuse()
        # self.is_reseted = True

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

class TaxTarif(models.Model):
    _name = 'hr.tax_tarif'
    _rec_name = 'tax_tarif'
    _description = 'tax tarif master'

    category = fields.Char(string='Category')
    bruto_from = fields.Char(string = 'Bruto From')
    bruto_to = fields.Char(string = 'Bruto To')
    tax_tarif = fields.Float('Tax Tarif (%)')

class BankMaster(models.Model):
    _name = 'hr.domestic_bank'
    _rec_name = 'bank_name'
    _description = 'list of domestic bank code and name'
    rtgs_code = fields.Char('RTGS Code')
    bank_code = fields.Char('Bank Code')
    online_bank_code = fields.Char('Online Bank Code')
    bank_name = fields.Char('Bank Name')
    city_name = fields.Char('City Name')
    

    

