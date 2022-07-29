from odoo import fields, models, api, _
from odoo.exceptions import UserError

class PrintInvoiceWizard(models.TransientModel):

    _name = 'print.invoice.wizard'
    
    
    move_id    = fields.Many2one('account.move', string='Invoice')
    print_type = fields.Selection([("kg","On Kg"),("meter","On Meter"),("yard",'On Yard')], string='Print Type')

    def action_print(self):
        if self.print_type == 'kg':
            return self.env.ref('pull_mysql.action_faktur_kg').report_action(self.move_id.id)
        elif self.print_type == 'meter':
            return self.env.ref('pull_mysql.action_faktur_meter').report_action(self.move_id.id)
        
        return self.env.ref('pull_mysql.action_faktur_yard').report_action(self.move_id.id)
        
