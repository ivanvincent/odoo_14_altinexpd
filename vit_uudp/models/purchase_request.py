from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'
    
    
    ajuan_id = fields.Many2one('uudp', string='Kasbon',help="uudp")
    
    
    
class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'
    
    
    ajuan_id = fields.Many2one('uudp', string='Kasbon',help="uudp")

    