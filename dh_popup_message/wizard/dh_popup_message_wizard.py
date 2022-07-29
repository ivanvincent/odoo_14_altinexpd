from odoo import fields, models

class DhPopupMessageWizard(models.TransientModel):
    _name = "dh.popup.message.wizard"
    _description = "Popup message warnings, alert ,success messages"

    def get_default(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    name = fields.Text(string="Message", readonly=True, default=get_default)
