from odoo import api, fields, models, _
import datetime

class Hr_employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    #additional field
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
    identification_id       = fields.Char(string='Identification No', required=False)
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

    family_ids = fields.One2many(comodel_name="hr.employee.family", string="Family", inverse_name="employee_id")
    education_ids = fields.One2many(comodel_name="hr.employee.education", string="Education", inverse_name="employee_id")
    organization_ids = fields.One2many(comodel_name="hr.employee.organization", string="Organization", inverse_name="employee_id")
    work_ids = fields.One2many(comodel_name="hr.employee.work", string="Work", inverse_name="employee_id")
    reference_ids = fields.One2many(comodel_name="hr.employee.reference", string="Reference", inverse_name="employee_id")
    guardian_ids = fields.One2many(comodel_name="hr.employee.guardian", string="Guardian", inverse_name="employee_id")

    get_picture = fields.Boolean(string="Get Picture", default=False)

    #field fungsional untuk kebutuhan report
    # contract_id = fields.Many2one(comodel_name="hr.contract", string="contract", compute="get_contract")
    contract_id = fields.Many2one(comodel_name="hr.contract", string="contract")

    #sequence for nik
    @api.model
    def create(self, vals):
        # import pdb;pdb.set_trace()
        # if 'nik' in vals :
            # if not vals['nik']:
            #     month   =   datetime.datetime.now().strftime("%m")
            #     year    =   datetime.datetime.now().strftime("%y")
            #     cr = self.env.cr
            #     if vals.get('is_phl') ==  True:
            #         cr.execute("SELECT MAX(SUBSTRING(nik, 8)) FROM hr_employee WHERE LEFT(nik ,1) = 'M' and SUBSTRING(nik FROM 3 FOR 2) =%s and substring(nik FROM 5 for 2) =%s",(year,month))
            #         niklist = cr.fetchall()
            #         if niklist[0][0]!=None or niklist!=False:
            #             for n in niklist:
            #                 result = n[0]
            #                 number = int(result)+1 #increment
            #                 string_number = str(number)
            #                 sequence = string_number.zfill(3)
            #                 nik = '%s-%s%s-%s' % ('M',year,month,sequence)
            #                 vals['nik'] = nik
            #         else:
            #             number = 1
            #             string_number = str(number)
            #             sequence = string_number.zfill(3)
            #             nik = '%s-%s%s-%s' % ('M',year,month,sequence)
            #             vals['nik'] = nik
            #     else:
            #         cr.execute("SELECT max(SUBSTRING(nik, 1, 4)) FROM hr_employee WHERE LEFT(nik ,1) != 'M'")
            #         niklist = cr.fetchall()
            #         if niklist[0][0]!=None or niklist!=False:
            #             for n in niklist:
            #                 result = n[0]
            #                 sequence = int(result)+1 #increment
            #                 nik = '%i.%s.%s' % (sequence,month,year)
            #                 vals['nik'] = nik
            #         else:
            #             number = 1
            #             string_number = str(number)
            #             sequence = string_number.zfill(3)
            #             nik = '%i.%s.%s' % (sequence,month,year)
            #             vals['nik'] = nik

            if 'address_home_id' in vals:
                if not vals['address_home_id']:
                    # name = vals['name']
                    # nik = vals['nik']
                    data = {'name':vals.get('name', False),
                            'ref':vals.get('nik', False),
                            # 'customer':True,
                            # 'supplier':False,
                            'company_type':'person'}
                    partner_employee = self.env['res.partner'].create(data)
                    vals['address_home_id'] = partner_employee.id

            if 'bank_account_id' in vals:
                if vals['bank_account_id']:
                    bank_id = vals['bank_account_id']
                    bank = self.env['res.partner.bank'].search([('id','=',bank_id)])
                    bank.write({'partner_id':partner_employee.id})

            return super(Hr_employee, self).create(vals)


    #check for id_number employee if already exist
    @api.onchange('identification_id')
    def _check_user_id(self):
        id_employee = self.identification_id
        if id_employee:
            id_exist  = self.env['hr.employee'].search([('identification_id','=',id_employee)])
            for x in id_exist:
                if x.identification_id == id_employee:
                    warning_mess = {
                        'title': _('Warning!'),
                        'message' : _('Nomor identitas %s sudah pernah di inputkan') % \
                            (self.identification_id)
                    }
                    return {'warning': warning_mess}
        return {}

    @api.depends('nik')
    def get_contract(self):
        # import pdb;pdb.set_trace();
        for employee in self:
            contract =  self.env['hr.contract'].search([('employee_id','=',employee.id)])
            if contract:
                for c in contract:
                    employee.contract_id = c.id
            return True