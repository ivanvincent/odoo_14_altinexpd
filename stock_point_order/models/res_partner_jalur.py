from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartnerJalur(models.Model):
    _inherit = 'res.partner.jalur'
    
    
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')

    