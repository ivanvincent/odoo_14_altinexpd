from odoo import api, fields, models


class DhFptMachineFinger(models.Model):
    _name = 'dh.fpt.machine.finger'
    _order = 'fpt_fid'

    name = fields.Char(string='Name',)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade', index=True,
                                  copy=False)
    fpt_uid = fields.Integer(string='Uid', )
    fpt_fid = fields.Integer(string='Fid', )
    fpt_valid = fields.Integer(string='Valid', )
    fpt_size = fields.Integer(string='Size', )
    fpt_template = fields.Text(string='Template', )
