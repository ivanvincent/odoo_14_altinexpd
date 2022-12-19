from odoo import api, fields, models, _

class Hr_applicant_organization(models.Model):
    _name = 'hr.applicant.organization'

    name = fields.Char(string="Nama Organisasi", required=True)
    city = fields.Char(string="Kota")
    major = fields.Char(string="Jurusan")
    position = fields.Char(string="Jabatan")
    start_year = fields.Char(string="Tahun Masuk")
    end_year = fields.Char(string="Tahun Keluar")
    applicant_id = fields.Many2one(comodel_name="hr.applicant", string="Applicant")
