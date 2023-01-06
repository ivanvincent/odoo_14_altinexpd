from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrContract(models.Model):
    _inherit = 'hr.contract'

    wage = fields.Monetary('Gaji', required=True, tracking=True, readonly=True, compute="_compute_wage_grade", help="Employee's monthly gross wage.")
    tunjangan_keahlian = fields.Monetary(string="Tunjangan Keahlian", readonly=True, compute="_compute_skill_grade")
    iuran_pensiun = fields.Monetary(string="Iuran Pensiun")
    alokasi_izin = fields.Float(string = 'Alokasi Izin', default = 2.50)
    alokasi_cuti = fields.Float(string='Alokasi Cuti', default = 12.0)
    wage_id = fields.Many2one('hr.wage_grade', string='Wage Grade')
    skill_id = fields.Many2one('hr.skill_grade', string='Skill Grade')
    
    @api.depends('wage_id')
    def _compute_wage_grade(self):
        self.wage = self.wage_id.gapok
    
    @api.depends('skill_id')
    def _compute_skill_grade(self):
        self.tunjangan_keahlian = self.skill_id.tunj_ahli
    
class WageGrade(models.Model):
    _name = 'hr.wage_grade'
    _rec_name ='wage_grade'
    _description = 'wage grade master'

    wage_grade = fields.Char(string='Wage Grade')
    gapok = fields.Float(string = 'Gaji Pokok')
    notes = fields.Text('Notes')

class SkillGrade(models.Model):
    _name = 'hr.skill_grade'
    _rec_name = 'skill_grade'
    _description = 'skill grade master'

    skill_grade = fields.Char(string='Skill Grade')
    tunj_ahli = fields.Float(string='Tunjangan Keahlian/hari')

