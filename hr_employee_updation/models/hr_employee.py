# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Jesni Banu (<https://www.cybrosys.com>)
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
from datetime import datetime, timedelta
from odoo import models, fields, _, api

GENDER_SELECTION = [('male', 'Male'),
                    ('female', 'Female'),
                    ('other', 'Other')]


class HrEmployeeFamilyInfo(models.Model):
    """Table for keep employee family information"""

    _name = 'hr.employee.family'
    _description = 'HR Employee Family'

    employee_id = fields.Many2one('hr.employee', string="Employee", help='Select corresponding Employee',
                                  invisible=1)
    relation_id = fields.Many2one('hr.employee.relation', string="Relation", help="Relationship with the employee")
    member_name = fields.Char(string='Name')
    member_contact = fields.Char(string='Contact No')
    birth_date = fields.Date(string="DOB", tracking=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def mail_reminder(self):
        """Sending expiry date notification for ID and Passport"""

        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([])
        for i in match:
            if i.id_expiry_date:
                exp_date = fields.Date.from_string(i.id_expiry_date) - timedelta(days=14)
                if date_now >= exp_date:
                    mail_content = "  Hello  " + i.name + ",<br>Your ID " + i.identification_id + "is going to expire on " + \
                                   str(i.id_expiry_date) + ". Please renew it before expiry date"
                    main_content = {
                        'subject': _('ID-%s Expired On %s') % (i.identification_id, i.id_expiry_date),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.work_email,
                    }
                    self.env['mail.mail'].sudo().create(main_content).send()
        match1 = self.search([])
        for i in match1:
            if i.passport_expiry_date:
                exp_date1 = fields.Date.from_string(i.passport_expiry_date) - timedelta(days=180)
                if date_now >= exp_date1:
                    mail_content = "  Hello  " + i.name + ",<br>Your Passport " + i.passport_id + "is going to expire on " + \
                                   str(i.passport_expiry_date) + ". Please renew it before expiry date"
                    main_content = {
                        'subject': _('Passport-%s Expired On %s') % (i.passport_id, i.passport_expiry_date),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.work_email,
                    }
                    self.env['mail.mail'].sudo().create(main_content).send()

    personal_mobile = fields.Char(string='Mobile', related='address_home_id.mobile', store=True,
                  help="Personal mobile number of the employee")
    joining_date = fields.Date(string='Joining Date', help="Employee joining date computed from the contract start date",compute='compute_joining', store=True)
    id_expiry_date = fields.Date(string='Expiry Date', help='Expiry date of Identification ID')
    passport_expiry_date = fields.Date(string='Expiry Date', help='Expiry date of Passport ID')
    id_attachment_id = fields.Many2many('ir.attachment', 'id_attachment_rel', 'id_ref', 'attach_ref',
                                        string="Attachment", help='You can attach the copy of your Id')
    passport_attachment_id = fields.Many2many('ir.attachment', 'passport_attachment_rel', 'passport_ref', 'attach_ref1',
                                              string="Attachment",
                                              help='You can attach the copy of Passport')
    fam_ids = fields.One2many('hr.employee.family', 'employee_id', string='Family', help='Family Information')

    @api.depends('contract_id')
    def compute_joining(self):
        if self.contract_id:
            date = min(self.contract_id.mapped('date_start'))
            self.joining_date = date
        else:
            self.joining_date = False

    @api.onchange('spouse_complete_name', 'spouse_birthdate')
    def onchange_spouse(self):
        relation = self.env.ref('hr_employee_updation.employee_relationship')
        lines_info = []
        spouse_name = self.spouse_complete_name
        date = self.spouse_birthdate
        if spouse_name and date:
            lines_info.append((0, 0, {
                'member_name': spouse_name,
                'relation_id': relation.id,
                'birth_date': date,
            })
                              )
            self.fam_ids = [(6, 0, 0)] + lines_info


class EmployeeRelationInfo(models.Model):
    """Table for keep employee family information"""

    _name = 'hr.employee.relation'

    name = fields.Char(string="Relationship", help="Relationship with thw employee")

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    personal_mobile = fields.Char(string='Mobile',
                  help="Personal mobile number of the employee")
    
    joining_date = fields.Date(string='Joining Date')
    id_expiry_date = fields.Integer(string='id_expiry_date')
    passport_expiry_date = fields.Date(string='passport_expiry_date')
    employee_team = fields.Selection([
        ('1', 'Tim 1'),
        ('2', 'Tim 2'),
        ('3', 'Tim Netral'),
        ('4', 'Staff Non-Produksi'),
        ('5', 'Staff Produksi Tidak Langsung'),
        ('6', 'Tim Netral Non-Shift'),
    ], string='Employee Team')
    nama_alias = fields.Char(string='Nama Alias')
    nik_karyawan = fields.Char(string='NIK')
    resource_calendar_ids = fields.Many2one('resource.calendar', 'Working Hours',)
    mobile = fields.Char(string='Mobile')
    npwp = fields.Char(string='Product name')
    kendaraan = fields.Char(string='Product name')
    jumlah_saudara = fields.Integer(string='Quantity')
    jurnal_id = fields.Many2one('account.journal', string='Kasir')
    bpjs_kesehatan = fields.Char(string='Product name')
    bpjs_ketenagakerjaan = fields.Char(string='Product name')
    berat_badan = fields.Integer(string='Quantity')
    anak_ke = fields.Char(string='Product name')
    batch_recruitment  = fields.Integer(string="Batch Recruitment", readonly=True)
    contract_type_id = fields.Many2one(related='contract_id.type_id', string='Contract')
    # shift_id         = fields.Many2one('hr.employee.shift', string='Shift')
    golongan_id      = fields.Many2one('hr.employee.golongan', string='Golongan')
    kelompok_id      = fields.Many2one('hr.employee.kelompok', string='Kelompok')
    grop_id          = fields.Many2one('hr.employee.grop', string='Group')
    barcode_date            = fields.Date("Date Barcode")
    code                    = fields.Char(string="Barcode")
    npwp                    = fields.Char(string="NPWP")
    ptkp_id                 = fields.Many2one(comodel_name="hr.ptkp", string="PTKP Status")
    nik                     = fields.Char(string="NIK")
    bpjs_kesehatan          = fields.Char(string="BPJS Kesehatan", required=False)
    bpjs_ketenagakerjaan 	= fields.Char(string="BPJS Ketenagakerjaan", required=False)
    jurnal_id               = fields.Many2one('account.journal', string="Cara Bayar")
    religion                = fields.Selection([('islam', 'Islam'), 
                                                ('kristen', 'Kristen'), 
                                                ('katolik', 'Katolik'), 
                                                ('hindu', 'Hindu'),
                                                ('budha', 'Budha'),
                                                ('konghuchu', 'Konghuchu'),],string='Religion')

    department_id           = fields.Many2one('hr.department', string='Department', required=False)
    job_id                  = fields.Many2one('hr.job', string='Job Title', required=False)
    identification_id       = fields.Char(string='Identification No', required=False, store=True)
    job_level_id            = fields.Many2one('hr.job.level', string='Job Level')

    tinggi_badan = fields.Integer(string="Tinggi Badan")
    berat_badan = fields.Integer(string="Berat Badan")
    kendaraan = fields.Selection([('mobil','Mobil'),('motor','Motor')], string="Kendaraan yang Dimiliki")
    jenis_sim = fields.Selection([('a', 'A'), 
                                  ('b', 'B'), 
                                  ('b1', 'B1'),
                                  ('b2', 'B2'),
                                  ('b3', 'B3'),
                                  ('c', 'C'),],string='Jenis SIM')
    anak_ke = fields.Integer(string="Anak Ke")
    jumlah_saudara = fields.Integer(string="Saudara")
    is_phl = fields.Boolean(string="Is PHL")

    # family_ids = fields.One2many(comodel_name="hr.employee.family", string="Family", inverse_name="employee_id")
    # education_ids = fields.One2many(comodel_name="hr.employee.education", string="Education", inverse_name="employee_id")
    # organization_ids = fields.One2many(comodel_name="hr.employee.organization", string="Organization", inverse_name="employee_id")
    # work_ids = fields.One2many(comodel_name="hr.employee.work", string="Work", inverse_name="employee_id")
    # reference_ids = fields.One2many(comodel_name="hr.employee.reference", string="Reference", inverse_name="employee_id")
    # guardian_ids = fields.One2many(comodel_name="hr.employee.guardian", string="Guardian", inverse_name="employee_id")

    get_picture = fields.Boolean(string="Get Picture", default=False)

    #field fungsional untuk kebutuhan report
    # contract_id = fields.Many2one(comodel_name="hr.contract", string="contract", compute="get_contract")
    contract_id = fields.Many2one(comodel_name="hr.contract", string="contract")
    # hr_employee_absence = fields.One2many('hr.attendance', 'employee_id', string='Employee absent')
    credit_limit      = fields.Float(string='Credit Limit')
    sisa_limit        = fields.Float(string='Sisa Limit',compute="_get_sisa_limit")
    reset_limit       = fields.Selection([("week","Week"),("month","Month"),("year","Year")], string='Reset Limit',default="month")
    partner_id = fields.Many2one("res.partner", "Related Partner")
    is_mkt = fields.Boolean('Is MKT')
    code_mkt = fields.Char('MKT Code')
    is_mekanik = fields.Boolean('Is Mekanik')
    is_karu = fields.Boolean('Is Karu')
    is_kasie = fields.Boolean('Is Kasie')
    is_request = fields.Boolean('Is Request')

    is_op_persiapan = fields.Boolean('Is Persiapan')
    is_op_dyeing = fields.Boolean('Is OP Dyeing')
    is_op_printing = fields.Boolean('Is OP Printing')
    is_tracer = fields.Boolean('Is Tracer')
    is_profer = fields.Boolean('Is Profer')
    is_engraver = fields.Boolean('Is Engraver')
    is_designer = fields.Boolean('Is Designer')
    payslip_count = fields.Integer(compute='_compute_payslip_count', string='Payslip Count', groups="sh_hr_payroll.group_hr_payroll_user")
    payslip_count = fields.Integer(compute='_compute_payslip_count', string='Payslip Count',
                                   groups="om_om_hr_payroll.group_hr_payroll_user")
    birthday = fields.Date('Date of Birth', groups="base.group_user", help="Birthday")
    announcement_count = fields.Integer(compute='_announcement_count', string='# Announcements', help="Count of Announcement's")
    # slip_ids = fields.One2many('hr.payslip', 'employee_id', string='Payslips', readonly=True, help="payslip")
    payslip_count = fields.Integer(compute='_compute_payslip_count', string='Payslip Count')
