from odoo import models, fields, api, _
from odoo.exceptions import UserError

class IrSequence(models.Model):
    _inherit = 'ir.sequence'
    
    def warehuse_sequencing(self, wh_code, wh_name):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', 'NO PR %s'%wh_name),
            ('code', '=', 'purchase.request'),
            ('prefix', '=', 'PR/'+wh_code+'/%(y)s/%(month)s/')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': 'NO PR %s'%wh_name,
                'code': 'purchase.request',
                'implementation': 'no_gap',
                'prefix': 'PR/'+wh_code+'/%(y)s/%(month)s/',
                'padding': 4
            })
        return sequence_id.next_by_id()

    