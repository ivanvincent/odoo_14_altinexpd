from odoo import api, fields, models, _

class Hr_employee_family(models.Model):
    _name = 'hr.employee.family'

    family  = fields.Selection([('ayah', 'Ayah'), 
                                  ('ibu', 'Ibu'), 
                                  ('suami_istri', 'Istri / Suami'),
                                  ('anak1', 'Anak ke 1'),
                                  ('anak2', 'Anak ke 2'),
                                  ('anak3', 'Anak ke 3'),],string='Anggota Keluarga', required=True)
    name = fields.Char(string="Nama", required=True)
    place_of_birth = fields.Char(string="Tempat Lahir")
    birthday = fields.Date(string="Tanggal Lahir")
    age = fields.Integer(string="Usia")
    work = fields.Char(string="Pekerjaan")
    employee_id = fields.Many2one(comodel_name="hr.employee", string="employee")


class Hr_employee_education(models.Model):
    _name = 'hr.employee.education'

    education  = fields.Selection([('sd', 'SD'), 
                                  ('smp', 'SMP'), 
                                  ('sma', 'SMA'),
                                  ('universitas', 'Akademi/Universitas')], string='Tingkat Pendidikan', required=True)
    name = fields.Char(string="Nama Sekolah", required=True)
    major = fields.Char(string="Jurusan")
    city = fields.Char(string="Kota")
    start_year = fields.Char(string="Tahun Masuk")
    end_year= fields.Char(string="Tahun Keluar")
    certificate = fields.Char(string="Ijasah")
    employee_id = fields.Many2one(comodel_name="hr.employee", string="employee")

class Hr_employee_organization(models.Model):
    _name = 'hr.employee.organization'

    name = fields.Char(string="Nama Organisasi", required=True)
    city = fields.Char(string="Kota")
    major = fields.Char(string="Jurusan")
    position = fields.Char(string="Jabatan")
    start_year = fields.Char(string="Tahun Masuk")
    end_year = fields.Char(string="Tahun Keluar")
    employee_id = fields.Many2one(comodel_name="hr.employee", string="employee")

class Hr_employee_work(models.Model):
    _name = 'hr.employee.work'

    name = fields.Char(string="Nama Perusahaan", required=True)
    position = fields.Char(string="Jabatan", required=True)
    start_year = fields.Char(string="Tahun Masuk")
    end_year = fields.Char(string="Tahun Keluar")
    reasons_leaving_the_job = fields.Char(string="Alasan Berhenti")
    last_salary = fields.Float(string="Gaji Terakhir")
    employee_id = fields.Many2one(comodel_name="hr.employee", string="employee")

class Hr_employee_reference(models.Model):
    _name = 'hr.employee.reference'

    name = fields.Char(string="Nama", required=True)
    position = fields.Char(string="Posisi")
    phone = fields.Char(string="No HP", required=True)
    employee_id = fields.Many2one(comodel_name="hr.employee")


class Hr_employee_guardian(models.Model):
    _name = 'hr.employee.guardian'

    name = fields.Char(string="Nama", required=True)
    phone = fields.Char(string="No HP", required=True)
    relation = fields.Selection([('ayah', 'Ayah'), 
                                ('ibu', 'Ibu'), 
                                ('saudara', 'Saudara'), 
                                ('lainnya', 'Lainnya')],string='Hubungan', required=True)
    employee_id = fields.Many2one(comodel_name="hr.employee")
