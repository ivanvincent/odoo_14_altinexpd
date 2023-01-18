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
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools, _, SUPERUSER_ID


class HRPayslip(models.Model):
    _inherit = "hr.payslip"


    date_from = fields.Date(string='Date From', readonly=True, required=True,
        default=str(datetime.now()+ relativedelta(months=-1, day=21)), states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='Date To', readonly=True, required=True,
         default=time.strftime('%Y-%m-20'),
        states={'draft': [('readonly', False)]})

    line_ids = fields.One2many('hr.payslip.line', 'slip_id', string='Payslip Lines', readonly=True,
        states={'draft': [('readonly', False)]})

    net = fields.Float(string="Nett")
    kasbon = fields.Float(string="Potogan Kasbon")

    #field untuk keperluar report
    full_basic_salary = fields.Float(string="Full Basic Salary")
    basic_salary = fields.Float(string="Basic Salary")
    t_jabatan = fields.Float(string="Tunjangan Jabatan")
    t_fungsional = fields.Float(string="Tunjangan Fungsional")
    t_komunikasi = fields.Float(string="Tunjangan Komunikasi")
    t_transport = fields.Float(string="Tunjangan Transport")
    t_makan = fields.Float(string="Uang Makan")
    t_kost = fields.Float(string="Tunjangan Kost")
    t_kemahalan = fields.Float(string="Tunjangan Kemahalan")
    t_luarkota = fields.Float(string="Tunjangan Harian Luar Kota")
    paket_lembur = fields.Float(string="Paket Lembur")
    uang_makan_backpay = fields.Float(string="Uang makan backpay")
    iuran_wajib = fields.Float(string="Iuran Wajib")
    potongan_inhealth = fields.Float(string="Potongan Inhealth")
    zakat_profesi = fields.Float(string="Zakat Profesi")
    potongan_unpaid_leave = fields.Float(string="Potongan Unpaid Leave")
    potongan_uang_makan = fields.Float(string="Potongan Uang Makan")
    potongan_lainlain = fields.Float(string="Potongan Lain-Lain")
    piutang_perusahaan = fields.Float(string="Piutang Perusahaan")
    jaminan_pensiun = fields.Float(string="Jaminan Pensiun Employee")
    bpjs_employee = fields.Float(string="BPJS K Employee")
    jht_employee = fields.Float(string="JHT Employee")
    pph21 = fields.Float(string="PPH 21")
    total_deduction = fields.Float(string="Total Deduction")
    take_home_pay = fields.Float(string="Take Home Pay")

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day):
            day = fields.Date.to_string(datetime_day)
            return self.env['hr.holidays'].search([
                ('state', '=', 'validate'),
                ('employee_id', '=', employee_id),
                ('type', '=', 'remove'),
                ('date_from', '<=', day),
                ('date_to', '>=', day)
            ], limit=1).holiday_status_id.name

        res = []
        #fill only if the contract as a working schedule linked
        for contract in self.env['hr.contract'].browse(contract_ids).filtered(lambda contract: contract.working_hours):
            attendances = {
                 'name': _("Normal Working Days paid at 100%"),
                 'sequence': 1,
                 'code': 'Work100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            presences = {
                 'name': _("Presences"),
                 'sequence': 2,
                 'code': 'Presences',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            overtime = {
                 'name': _("Overtime"),
                 'sequence': 3,
                 'code': 'Overtime',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            overtime2 = {
                 'name': _("Overtime Day Off"),
                 'sequence': 4,
                 'code': 'Overtime2',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            alpha = {
                 'name': _("Tanpa Keterangan/Mangkir"),
                 'sequence': 5,
                 'code': 'Alpha',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            obj_shift = self.env['hr.contract.detail']
            leaves = {}
            day_from = fields.Datetime.from_string(date_from)
            day_to = fields.Datetime.from_string(date_to)
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                #menghitung lembur
                employee_id = contract.employee_id.id
                datas = day_from + timedelta(days=day)
                tanggal = datas.strftime("%Y-%m-%d")
                obj_over = self.env['hr.overtime']
                obj_ovemp = self.env['hr.overtime.employee']
                spg_over = self.env['attendance.spg']
                spg_ovemp = self.env['attendance.spg.details']
                # lembur pegawai tanpa schedule
                if not contract.working_hours and not contract.shift_working_schedule:
                    dtime_from = datas.strftime("%Y-%m-%d 00:00:00")
                    dtime_to = datas.strftime("%Y-%m-%d 23:59:59")
                    spg_ovemp_exist = spg_ovemp.search([('employee_id','=',employee_id),('sign_in','>=',dtime_from),('sign_out','<=',dtime_to),('total_lembur_calc','>',0.0)],limit=1)
                    if spg_ovemp_exist :
                        if spg_ovemp_exist.attendance_spg_id.state == 'confirm':
                            jml_lembur = spg_ovemp_exist.total_lembur_calc
                            overtime['number_of_hours'] += jml_lembur
                            if jml_lembur >= 8.0 :
                                    overtime2['number_of_days'] += 1
                else :
                    # lembur pegawai dengan schedule
                    src_over = obj_over.search([('tgl_lembur','=',tanggal),('state','=','validate')])
                    for overt in src_over :
                        src_ovemp = obj_ovemp.search([('overtime_id','=',overt.id),('employee_id','=',employee_id)],limit=1)
                        if src_ovemp :
                            jumlah = src_ovemp.total_jam
                            overtime['number_of_hours'] += jumlah
                            if overt.hari_libur:
                                overtime2['number_of_hours'] += jumlah
                                if jumlah >= 4.0 :
                                    overtime2['number_of_days'] += 1
                date = (day_from + timedelta(days=day))
                dates = str(date)[:10]    
                # jika kerja shift-shift an    
                if contract.shift_working_schedule :
                    working_hours_exist = obj_shift.search([('contract_id','=',contract.id),('start_date','<=',dates),('end_date','>=',dates)], limit=1, order='id desc')
                    if not working_hours_exist :
                        continue
                    working_hours_on_day = working_hours_exist.schedule_id.working_hours_on_day(day_from + timedelta(days=day))
                else :
                    # kerja non shift
                    working_hours_on_day = contract.working_hours.working_hours_on_day(day_from + timedelta(days=day))
                if working_hours_on_day:
                    #the employee had to work
                    leave_type = was_on_leave(employee_id, day_from + timedelta(days=day))
                    if leave_type:
                        #if he was on leave, fill the leaves dict
                        if leave_type in leaves:
                            leaves[leave_type]['number_of_days'] += 1.0
                            leaves[leave_type]['number_of_hours'] += working_hours_on_day
                        else:
                            leaves[leave_type] = {
                                'name': leave_type,
                                'sequence': 6,
                                'code': leave_type,
                                'number_of_days': 1.0,
                                'number_of_hours': working_hours_on_day,
                                'contract_id': contract.id,
                            }
                    else:
                        #add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours_on_day
                        #kehadiran
                        real_working_hours_on_day = self.env['hr.attendance'].real_working_hours_on_day(employee_id, day_from + timedelta(days=day))
                        if real_working_hours_on_day >= 0.000000000000000001 and leave_type == False :
                            presences['number_of_days'] += 1.0
                            presences['number_of_hours'] += working_hours_on_day
            leaves = [value for key, value in leaves.items()]
            res += [attendances] + leaves + [presences] + [overtime] + [overtime2]
            total_alpha = attendances['number_of_days'] - presences['number_of_days'] # tanpa_keterangan dianggap alpha
            if total_alpha > 0 :
                alpha['number_of_days'] = total_alpha
                res += [alpha]
        return res


    
    def compute_sheet(self):
        # import pdb;pdb.set_trace();
        res = super(HRPayslip, self).compute_sheet()
        nett = 0

        #variabel untuk kebutuhan report
        full_basic_salary = 0
        basic_salary = 0
        t_jabatan = 0
        t_fungsional = 0
        t_komunikasi = 0
        t_transport = 0
        t_makan = 0
        t_kost = 0
        t_kemahalan = 0
        t_luarkota = 0
        paket_lembur = 0
        uang_makan_backpay = 0
        iuran_wajib = 0
        potongan_inhealth = 0
        zakat_profesi = 0
        potongan_unpaid_leave = 0
        potongan_uang_makan = 0
        potongan_lainlain = 0
        piutang_perusahaan = 0
        jaminan_pensiun = 0
        bpjs_employee = 0
        jht_employee = 0
        pph21 = 0
        total_deduction = 0
        take_home_pay = 0

        for payslip in self:
            res = super(HRPayslip, self).compute_sheet()
            payslip_line_obj = self.env['hr.payslip.line']
            take_home_pay = payslip_line_obj.search([('slip_id','=',payslip.id),('category_id.code','ilike','NET')], limit=1, order="sequence desc")
            if take_home_pay :
                nett = take_home_pay.total

            #field untuk kebutuhan report
            payslip_detail = payslip_line_obj.search([('slip_id','=',payslip.id)])
            if payslip_detail:
                for detail in payslip_detail:
                    if detail.code == 'TJB':
                        t_jabatan = detail.total

                    if detail.code == 'TFSNL':
                        t_fungsional = detail.total

                    if detail.code == 'TKOM':
                        t_komunikasi = detail.total

                    if detail.code == 'TTRANS':
                        t_transport = detail.total

                    if detail.code == 'TMEAL':
                        t_makan = detail.total

                    if detail.code == 'TKOST':
                        t_kost = detail.total

                    if detail.code == 'TKMHL':
                        t_kemahalan = detail.total

                    if detail.code == 'PL12J':
                        paket_lembur = detail.total

                    if detail.code == 'IWJB1':
                        iuran_wajib = detail.total

                    if detail.code == 'IWJB2':
                        iuran_wajib = detail.total

                    if detail.code == 'PIH':
                        potongan_inhealth = detail.total

                    if detail.code == 'ZP':
                        zakat_profesi = detail.total

                    if detail.code == 'UNPAID':
                        potongan_unpaid_leave = detail.total

                    if detail.code == 'POTMEAL':
                        potongan_uang_makan = detail.total

                    if detail.code == 'PUM':
                        potongan_uang_makan = detail.total

                    if detail.code == 'POTL':
                        potongan_lainlain = detail.total

                    if detail.code == 'BPJSJP':
                        jaminan_pensiun = detail.total

                    if detail.code == 'BPJSKES':
                        bpjs_employee = detail.total

                    if detail.code == 'BPJSJHT':
                        jht_employee = detail.total

                    if detail.code == 'TTLDED':
                        total_deduction = detail.total

                    payslip.write({
                                   't_jabatan': int(round(t_jabatan,0)),
                                   't_fungsional': int(round(t_fungsional,0)),
                                   't_komunikasi': int(round(t_komunikasi,0)),
                                   't_transport': int(round(t_transport,0)),
                                   't_makan': int(round(t_makan,0)),
                                   't_kost': int(round(t_kost,0)),
                                   't_kemahalan': int(round(t_kemahalan,0)),
                                   'paket_lembur': int(round(paket_lembur,0)),
                                   'iuran_wajib': int(round(iuran_wajib,0)),
                                   'potongan_inhealth': int(round(potongan_inhealth,0)),
                                   'zakat_profesi': int(round(zakat_profesi,0)),
                                   'potongan_unpaid_leave': int(round(potongan_unpaid_leave,0)),
                                   'potongan_uang_makan': int(round(potongan_uang_makan,0)),
                                   'potongan_lainlain': int(round(potongan_lainlain,0)),
                                   'jaminan_pensiun': int(round(jaminan_pensiun,0)),
                                   'bpjs_employee': int(round(bpjs_employee,0)),
                                   'jht_employee': int(round(jht_employee,0)),
                                   'total_deduction': int(round(total_deduction,0)),
                                })

            payslip.write({'net': int(round(nett,0)),})
        return True

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_kasbon(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        kasbon_amount = 0
        check_cash_receipt = self.env['hr.kasbon'].search([('employee_id','=',employee.id),('state','=','confirm')])
        if check_cash_receipt:
            for result in check_cash_receipt:
                for kasbon in result.kasbon_ids:
                    if kasbon.tanggal_angsuran >= date_from and kasbon.tanggal_angsuran <= date_to and kasbon.paid == False:
                        kasbon_amount = kasbon.nominal

        self.kasbon = kasbon_amount

    
    def action_payslip_done(self):
        check_cash_receipt = self.env['hr.kasbon'].search([('employee_id','=',self.employee_id.id),('state','=','confirm')])
        total_piutang = 0
        if check_cash_receipt:
            for result in check_cash_receipt:
                for kasbon in result.kasbon_ids:
                    if kasbon.tanggal_angsuran >= self.date_from and kasbon.tanggal_angsuran <= self.date_to and kasbon.paid == False:
                        kasbon.write({'paid':True})

                    #get piutang perusahaan
                    if kasbon.paid == False:
                        total_piutang = total_piutang + kasbon.nominal

                    self.write({'piutang_perusahaan': total_piutang})
        self.compute_sheet()
        return self.write({'state': 'done'})

HRPayslip()