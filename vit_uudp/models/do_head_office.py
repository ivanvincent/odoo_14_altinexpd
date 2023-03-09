from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DOHeadOffice(models.Model):
    _inherit = 'do.head.office'
    
    
    ajuan_id            = fields.Many2one('uudp', string='Ajuan',domain=[('type','=','pengajuan')])
    do_expense_ids      = fields.One2many('uudp.detail', 'do_id', string='Expense')


    