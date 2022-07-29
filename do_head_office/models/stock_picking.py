from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    
    do_id = fields.Many2one('do.head.office', string='DO',groups="do_head_office.group_do_head_office_user")
    

    