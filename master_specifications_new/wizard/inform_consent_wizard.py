from odoo import fields, models, api, _
from odoo.exceptions import UserError

class InformConsentWizard(models.TransientModel):
    _name = 'inform.consent.wizard.new'

    qrf_id = fields.Many2one('quotation.request.form.new', string='Quotation', required=True,)

    def action_print(self):
        print("action_print")
        return self.env.ref('master_specifications_new.action_inform_consent_pdf_new').report_action(self.qrf_id)
        return True
