from odoo import api, fields, models, _

class Hr_applicant_education(models.Model):
    _name = 'hr.applicant.education'

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
    applicant_id = fields.Many2one(comodel_name="hr.applicant", string="Applicant")
