from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

class HrDepartment(models.Model):
    _inherit = 'hr.department'
    
    
    
    default_code           = fields.Char(string='Code')
    jumlah_mpp             = fields.Integer(string='Mpp')
    jumlah_actual_karyawan = fields.Integer(compute='_compute_actual_karyawan', string='Actual Karyawan', store=False)
    kebutuhan              = fields.Float(compute='_compute_kebutuhan', string='Kebutuhan', store=False)
    
    @api.depends('member_ids')
    def _compute_actual_karyawan(self):
        for department in self:
            department.jumlah_actual_karyawan = len(department.member_ids)
        
    
    
    @api.depends('jumlah_mpp','jumlah_actual_karyawan')
    def _compute_kebutuhan(self):
        for department in self:
            department.kebutuhan = department.jumlah_mpp - department.jumlah_actual_karyawan
    

    