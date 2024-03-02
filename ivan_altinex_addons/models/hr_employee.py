from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_team = fields.Selection([
        ('1', 'Tim 1'),
        ('2', 'Tim 2'),
        ('3', 'Tim Netral'),
        ('4', 'Staff Non-Produksi'),
        ('5', 'Staff Produksi Tidak Langsung'),
        ('6', 'Tim Netral Non-Shift'),
    ], string='Employee Team')
    nama_alias = fields.Char(string='Alias')
    nik_karyawan = fields.Char(string='NIK')
    tax_category = fields.Char(string='Tax Category',compute='_compute_tax_category',store=True)
    domestic_bank_id = fields.Many2one('hr.domestic_bank', string='Domestic Bank')
    no_rekening = fields.Char('No Rekening')
    jabatan = fields.Selection([
		('1', 'Direktur / Wakil Direktur'),
        ('2', 'Manager'),
        ('3', 'Supervisor'),
        ('4', 'Staff'),
        ('5', 'Operator'),
	], string='Jabatan')

    @api.depends('marital', 'children')
    def _compute_tax_category(self):
        marital = self.marital
        children = self.children
        
        if((marital == 'single' and children == 0) or (marital == 'single' and children == 1) or (marital == 'married' and children == 0)):
            self.tax_category = 'A'
        elif((marital == 'single' and children == 2) or (marital == 'single' and children == 3) or (marital == 'married' and children == 1) or (marital == 'married' and children == 2)):
            self.tax_category = 'B'
        else:
            self.tax_category = 'C'
        
    # @api.depends('domestic_bank_id')
    # def _compute_bank_name(self):
    #     bank_ids = self.env['hr.domestic_bank'].search([('id','=',self.domestic_bank_id.id)])
    #     for rec in bank_ids:
    #         self.domestic_bank_id = rec.bank_name
