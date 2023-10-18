from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    address            = fields.Char(string='Address', readonly=False, store=False,)
    nama_perusahaan    = fields.Char(string='Nama Perusahaan')
    jabatan            = fields.Char(string='Jabatan')
    divisi             = fields.Char(string='Divisi')
    gender_user        = fields.Selection([("male","Male"),("female","Female")], string='Gender', readonly=False, store=False)

    def compute_info(self):
        for rec in self:
            user_id = self.env['res.partner'].search([('partner_id', '=', rec.id)])
            rec.address = user_id.address
            rec.nama_perusahaan = user_id.nama_perusahaan
            rec.jabatan = user_id.jabatan
            rec.divisi = user_id.divisi
            rec.gender_user = user_id.gender_user