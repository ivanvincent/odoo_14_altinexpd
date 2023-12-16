from odoo import fields, models, api, _

class CustomerMailWizard(models.TransientModel):
    _name = 'customer.mail.wizard'

    so_ids        = fields.Binary(string='SO')
    so_name       = fields.Char('Name')
    drawing_ids   = fields.Binary(string='Drawing')
    dwg_name      = fields.Char('Name')
    qrf_id        = fields.Many2one('quotation.request.form', string='Quotation')
    

    def action_print(self):
        print("action_print")

    def action_so(self):
        print("action_so")
        return self.env.ref('master_specifications.action_qrf_report').report_action(self.qrf_id)
        return True
