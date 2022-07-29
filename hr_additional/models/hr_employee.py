from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    contract_type_id = fields.Many2one(related='contract_id.type_id', string='Contract')
    shift_id         = fields.Many2one('hr.employee.shift', string='Shift')
    golongan_id      = fields.Many2one('hr.employee.golongan', string='Golongan')
    kelompok_id      = fields.Many2one('hr.employee.kelompok', string='Kelompok')
    grop_id          = fields.Many2one('hr.employee.grop', string='Group')
    
    
    
    

    