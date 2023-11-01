from odoo import fields, models, api, _
from odoo.exceptions import UserError

class PrintQrfWizard(models.TransientModel):
    _name = 'print.qrf.wizard'

    qrf_id          = fields.Many2one('quotation.request.form', string='Quotation', required=True,)
    type_report     = fields.Selection([
        ("surat_penawaran","Surat Penawaran"),
        ("quotation_request","Quotation Request Form Report"),
        ("quotation_request_nonpage","Quotation Request Form Report Non Page-Break"),
        ("quotation_request_summary","Quotation Request Form Summary Report"),
        ], string='Type'
    )

    def action_print(self):
        if self.type_report == 'quotation_request':
            return self.env.ref('master_specifications.action_qrf_report').report_action(self.qrf_id)
        elif self.type_report == 'surat_penawaran':
            return self.env.ref('master_specifications.action_qrf_report_penawaran').report_action(self.qrf_id)
        elif self.type_report == 'quotation_request_nonpage':
            return self.env.ref('master_specifications.action_qrf_report_unpage').report_action(self.qrf_id)
        elif self.type_report == 'quotation_request_summary':
            return self.env.ref('master_specifications.action_specifications_summary_2').report_action(self.qrf_id)

        return True

    def action_print_dqups2(self):
        if self.type_report == 'quotation_request':
            return self.env.ref('master_specifications.action_report_dqups2').report_action(self.qrf_id)
        elif self.type_report == 'quotation_request_nonpage':
            return self.env.ref('master_specifications.action_report_dqups2_unpage').report_action(self.qrf_id)
        elif self.type_report == 'quotation_request_summary':
            return self.env.ref('master_specifications.action_specifications_summary_2').report_action(self.qrf_id)

        return True