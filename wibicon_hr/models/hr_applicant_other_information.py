from odoo import api, fields, models, _

class Hr_applicant_reference(models.Model):
    _name = 'hr.applicant.reference'

    name = fields.Char(string="Nama", required=True)
    position = fields.Char(string="Posisi")
    phone = fields.Char(string="No HP", required=True)
    applicant_id = fields.Many2one(comodel_name="hr.applicant")


class Hr_applicant_guardian(models.Model):
    _name = 'hr.applicant.guardian'

    name = fields.Char(string="Nama", required=True)
    phone = fields.Char(string="No HP", required=True)
    relation = fields.Selection([('ayah', 'Ayah'), 
                                ('ibu', 'Ibu'), 
                                ('saudara', 'Saudara'), 
                                ('lainnya', 'Lainnya')],string='Hubungan', required=True)
    applicant_id = fields.Many2one(comodel_name="hr.applicant")