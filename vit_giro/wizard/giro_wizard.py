from odoo import fields, models, api, _
from odoo.exceptions import UserError

class GiroWizard(models.TransientModel):

    _name = 'giro.inv.wizard'
    
    
    giro_id     = fields.Many2one('vit.giro', string='Giro')
    giro_type = fields.Selection('Type',related='giro_id.type')
    invoice_type = fields.Char('Type',related='giro_id.invoice_type')
    partner_id  = fields.Many2one('res.partner', string='Partner')
    invoice_ids = fields.Many2many(
        comodel_name='account.move', 
        relation='account_move_giro__wizard_rel',
        domain=[('state', '=', 'posted'), ('payment_state', 'in', ('not_paid','partial'))],
        string='Invoice'
        )

    def action_add_invoice(self):
        
        if self.giro_id:
            invoice_ids = []
            for invoice in self.invoice_ids:
                if invoice.id in [line.invoice_id.id for line in self.giro_id.giro_invoice_ids]:
                    raise UserError('Mohon maaf invoice %s sudah dimasukan ke dalam list'%(invoice.name))
                else:
                    invoice_ids += [(0,0,{"invoice_id":invoice.id,"amount_invoice":invoice.amount_total if invoice.state == 'not_paid' else invoice.amount_residual})]
                    
                
            self.giro_id.write({"giro_invoice_ids":invoice_ids})
                
             
