from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    fpt_uid = fields.Integer(string='User UID', index=True)
    fpt_user_id = fields.Char(string='User ID', index=True)
    fpt_password = fields.Integer(string='User Password')
    fpt_card = fields.Integer(string='Card', default=0)
    fpt_privilege = fields.Integer(string='Privilege', default=0)
    fpt_machine_ids = fields.Many2many('dh.fpt.machine', 'dh_fpt_machine_ids', string='Machines',
                                       help="Multi Machine User")
    fpt_finger_line = fields.One2many('dh.fpt.machine.finger', 'employee_id', string='Data Fingers', copy=True,
                                      auto_join=True)
