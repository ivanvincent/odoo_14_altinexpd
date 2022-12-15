from odoo import api, fields, models, exceptions, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

class Hr_applicant(models.Model):
    _name = 'hr.applicant'
    _inherit = 'hr.applicant'

    # #data pribadi
    partner_name = fields.Char("Applicant's Name", required=True)
    department_id = fields.Many2one('hr.department', required=True)
    job_id = fields.Many2one('hr.job', "Applied Job", required=True, domain="[('state','=','reqruit')]")
    npwp = fields.Char(string="NPWP")
    nomor_ktp = fields.Char(string="Nomor KTP", required=True)
    nomor_rekening = fields.Char(string="Nomor Rekening")
    religion                = fields.Selection([('islam', 'Islam'), 
                                                ('kristen', 'Kristen'), 
                                                ('katolik', 'Katolik'), 
                                                ('hindu', 'Hindu'),
                                                ('budha', 'Budha'),
                                                ('konghuchu', 'Konghuchu'),],string='Agama')
    alamat = fields.Char(string="Alamat Tinggal")
    alamat_ktp = fields.Char(string="Alamat KTP")
    tempat_lahir = fields.Char(string="Tempat Lahir")
    tanggal_lahir = fields.Date(string="Tanggal Lahir")
    jenis_kelamin = fields.Selection([('male', 'Male'), 
                                    ('female', 'Female'), 
                                    ('other', 'Other')],string='Jenis Kelamin')
    tinggi_badan = fields.Integer(string="Tinggi Badan")
    berat_badan = fields.Integer(string="Berat Badan")
    status     = fields.Selection([('single', 'Single'), 
                                    ('married', 'Married'), 
                                    ('widower', 'Widower'),
                                    ('divorced', 'Divorced'),],string='Status Pernikahan')
    jumlah_anak = fields.Integer(string="Jumlah Anak")
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


    family_ids = fields.One2many(comodel_name="hr.applicant.family", string="Family", inverse_name="applicant_id")
    education_ids = fields.One2many(comodel_name="hr.applicant.education", string="Education", inverse_name="applicant_id")
    organization_ids = fields.One2many(comodel_name="hr.applicant.organization", string="Organization", inverse_name="applicant_id")
    work_ids = fields.One2many(comodel_name="hr.applicant.work", string="Work", inverse_name="applicant_id")
    reference_ids = fields.One2many(comodel_name="hr.applicant.reference", string="Reference", inverse_name="applicant_id")
    guardian_ids = fields.One2many(comodel_name="hr.applicant.guardian", string="Guardian", inverse_name="applicant_id")    

    @api.onchange('nomor_ktp')
    def _check_ktp(self):
        ktp = self.nomor_ktp
        if ktp:
            pesan = ''
            cek_ktp_applicant = self.env['hr.applicant'].search([('nomor_ktp','=',ktp)])
            cek_ktp_employee = self.env['hr.employee'].search([('identification_id','=',ktp)])
            if cek_ktp_employee and cek_ktp_applicant:
                for ktp_e in cek_ktp_employee:
                    warning_mess = {
                        'title': _('Warning!'),
                        'message' : _('Nomor identitas %s sudah pernah di inputkan di Master Employee dan Applicant') % \
                            (ktp_e.identification_id)
                        }
                    return {'warning': warning_mess}

            elif cek_ktp_employee:
                for ktp_e in cek_ktp_employee:
                    warning_mess = {
                        'title': _('Warning!'),
                        'message' : _('Nomor identitas %s sudah pernah di inputkan di Master Employee') % \
                            (ktp_e.identification_id)
                       }
                    return {'warning': warning_mess}

            elif cek_ktp_applicant:
                for ktp_a in cek_ktp_applicant:
                    warning_mess = {
                        'title': _('Warning!'),
                        'message' : _('Nomor identitas %s sudah pernah di inputkan di Master Applicant') % \
                        (ktp_a.nomor_ktp)
                      }
                    return {'warning': warning_mess}

    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            jabatan = self.env['hr.job'].search([('id','=',applicant.job_id.id)]).name
            limit = self.env['hr.job'].search([('id','=',applicant.job_id.id)]).no_of_recruitment
            amount = self.env['hr.employee'].search([('job_id','=',applicant.job_id.id),('batch_recruitment','=',applicant.batch_recruitment)])
            if amount:
                if limit <= len(amount):
                    raise exceptions.ValidationError(_("Kebutuhan karyawan baru untuk posisi %(jabatan)s sudah terpenuhi!") % {
                                                        'jabatan': jabatan,})
            #create partner
            data = {
            'name': applicant.name,
            'company_type':'person',
            'is_company': False,
            'street':applicant.alamat,
            'street2':applicant.alamat_ktp,
            'phone':applicant.partner_phone,
            'mobile':applicant.partner_mobile,
            'email':applicant.email_from,
            }
            partner = self.env['res.partner'].create(data)

            appl = self.env['hr.applicant'].search([('id','=',applicant.id)])
            appl.write({'partner_id': partner.id})

            address_id = contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.name_get()[0][1]
            if applicant.job_id and (applicant.partner_name or contact_name):
            	bank_id = {}
            	if applicant.nomor_rekening != False:
            		data_rek = {
            		'acc_number':applicant.nomor_rekening,
            		'partner_id':partner.id,
            		}
            		bank = self.env['res.partner.bank'].create(data_rek)
            		bank_id = bank.id
                # applicant.job_id.write({'no_of_hired_employee' : applicant.job_id.no_of_hired_employrr + 1})
                # employee = self.env['hr.employee'].create({'name': applicant.partner_name or contact_name,
                #                                            'job_id': applicant.job_id.id,
                #                                            'address_home_id': address_id,'department_id': applicant.department_id.id or False,'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
                #                                            'work_email': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False,
                #                                            'work_phone': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.phone or False,
                #                                            'npwp': applicant.npwp,
                #                                            'identification_id':applicant.nomor_ktp,
                #                                            'bank_account_id':bank_id,
                #                                            'religion':applicant.religion,
                #                                            'place_of_birth':applicant.tempat_lahir,
                #                                            'birthday':applicant.tanggal_lahir,
                #                                            'gender':applicant.jenis_kelamin,
                #                                            'tinggi_badan': applicant.tinggi_badan,
                #                                            'berat_badan': applicant.berat_badan,
                #                                            'marital': applicant.status,
                #                                            'children': applicant.jumlah_anak,
                #                                            'kendaraan': applicant.kendaraan,
                #                                            'jenis_sim': applicant.jenis_sim,
                #                                            'anak_ke': applicant.jumlah_saudara,
                #                                            'address_home_id':partner.id,
                #                                            'is_phl':applicant.is_phl,
                #                                            'batch_recruitment':applicant.batch_recruitment,
                #                                            'nik':False})
                # applicant.write({'emp_id': employee.id})
                # applicant.write({'stage_id':5})

                if applicant.family_ids:
                    for fam in applicant.family_ids:
                        family={
                			'employee_id':employee.id,
                			'family':fam.family,
							'name':fam.name,
							'place_of_birth':fam.place_of_birth,
							'birthday':fam.birthday,
							'age':fam.age,
							'work':fam.work,}
                        self.env['hr.employee.family'].create(family)

                if applicant.education_ids:
                    for edu in applicant.education_ids:
                        education={
                			'employee_id':employee.id,
                			'education':edu.education,
						    'name':edu.name,
						    'major':edu.major,
						    'city':edu.city,
						    'start_year':edu.start_year,
						    'end_year':edu.end_year,
						    'certificate':edu.certificate,}
                        self.env['hr.employee.education'].create(education)

                if applicant.organization_ids:
                    for org in applicant.organization_ids:
                        organization={
                        	'employee_id':employee.id,
						    'name':org.name,
						    'city':org.city,
						    'major':org.major,
						    'position':org.position,
						    'start_year':org.start_year,
						    'end_year':org.end_year,}
                        self.env['hr.employee.organization'].create(organization)

                if applicant.organization_ids:
                    for org in applicant.organization_ids:
                        organization={
                        	'employee_id':employee.id,
						    'name':org.name,
						    'city':org.city,
						    'major':org.major,
						    'position':org.position,
						    'start_year':org.start_year,
						    'end_year':org.end_year,}
                        self.env['hr.employee.organization'].create(organization)

                if applicant.work_ids:
                    for wo in applicant.work_ids:
                        work={
                        	'employee_id':employee.id,
						    'name':wo.name,
						    'position':wo.position,
						    'start_year':wo.start_year,
						    'end_year':wo.end_year,
						    'reasons_leaving_the_job':wo.reasons_leaving_the_job,
						    'last_salary':wo.last_salary,}
                        self.env['hr.employee.work'].create(work)

                if applicant.reference_ids:
                    for refer in applicant.reference_ids:
                        reference={
                        	'employee_id':employee.id,
						    'name':refer.name,
						    'position':refer.position,
						    'phone':refer.phone,}
                        self.env['hr.employee.reference'].create(reference)

                if applicant.guardian_ids:
                    for guard in applicant.guardian_ids:
                        guardian={
						    'name':guard.name,
						    'phone':guard.phone,
						    'relation':guard.relation,}
                        self.env['hr.employee.guardian'].create(guardian)

                applicant.job_id.message_post(
                    body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired")
                employee._broadcast_welcome()
            else:
                raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        if employee:
            dict_act_window['res_id'] = employee.id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window


    