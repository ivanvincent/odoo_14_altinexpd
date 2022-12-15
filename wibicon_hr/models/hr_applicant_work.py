from odoo import api, fields, models, _

class Hr_applicant_work(models.Model):
    _name = 'hr.applicant.work'

    name = fields.Char(string="Nama Perusahaan", required=True)
    position = fields.Char(string="Jabatan", required=True)
    start_year = fields.Char(string="Tahun Masuk")
    end_year = fields.Char(string="Tahun Keluar")
    reasons_leaving_the_job = fields.Char(string="Alasan Berhenti")
    last_salary = fields.Float(string="Gaji Terakhir")
    applicant_id = fields.Many2one(comodel_name="hr.applicant", string="Applicant")
