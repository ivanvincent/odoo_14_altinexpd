from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResUser(models.Model):
    _inherit = 'res.users'

    tag_employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id   = fields.Many2one(related='tag_employee_id.department_id', string='Department')
    job_id          = fields.Many2one(related='tag_employee_id.job_id', string='Job Position')
    parent_id       = fields.Many2one(related='tag_employee_id.parent_id', string='Superior')
    device_id       = fields.Char(string='Device Id')
    fcm_key         = fields.Char(string='FCM Key')
    tipe_permintaan = fields.Selection([('produksi', 'Produksi'), ('non_produksi', 'Non Produksi')], string="Tipe Permintaan")