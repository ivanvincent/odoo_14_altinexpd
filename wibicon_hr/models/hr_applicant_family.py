from odoo import api, fields, models, _

class Hr_applicant_family(models.Model):
    _name = 'hr.applicant.family'

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
    applicant_id = fields.Many2one(comodel_name="hr.applicant", string="Applicant")