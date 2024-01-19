from odoo import fields, models, api, _

class CustomerMailWizard(models.TransientModel):
    _name = 'customer.mail.wizard'

    so_ids        = fields.Binary(string='SO', 
    # related="qrf_id.report_file.datas"
    )
    so_name       = fields.Char('Name')
    drawing_ids   = fields.Binary(string='Drawing')
    dwg_name      = fields.Char('Name')
    qrf_id        = fields.Many2one('quotation.request.form', string='Quotation')
    

    def action_print(self):
        self.qrf_id.so_id.action_quotation_send()
        # print("action_print")

    def _find_mail_template(self, force_confirmation_template=False):
        self.ensure_one()
        template_id = False

        if force_confirmation_template or (self.state == 'sale' and not self.env.context.get('proforma', False)):
            template_id = int(self.env['ir.config_parameter'].sudo().get_param('sale.default_confirmation_template'))
            template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
            if not template_id:
                template_id = self.env['ir.model.data'].xmlid_to_res_id('sale.mail_template_sale_confirmation', raise_if_not_found=False)
        if not template_id:
            template_id = self.env['ir.model.data'].xmlid_to_res_id('sale.email_template_edi_sale', raise_if_not_found=False)

        return template_id

    # def action_print(self):
    #     ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
    #     self.ensure_one()
    #     template_id = self._find_mail_template()
    #     lang = self.env.context.get('lang')
    #     template = self.env['mail.template'].browse(template_id)
    #     if template.lang:
    #         lang = template._render_lang(self.ids)[self.id]
    #     ctx = {
    #         'default_model': 'sale.order',
    #         'default_res_id': self.ids[0],
    #         'default_use_template': bool(template_id),
    #         'default_template_id': template_id,
    #         'default_composition_mode': 'comment',
    #         'mark_so_as_sent': True,
    #         'custom_layout': "mail.mail_notification_paynow",
    #         'proforma': self.env.context.get('proforma', False),
    #         'force_email': True,
    #         'model_description': self.with_context(lang=lang).type_name,
    #     }
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(False, 'form')],
    #         'view_id': False,
    #         'target': 'new',
    #         'context': ctx,
    #     }

    def action_so(self):
        print("action_so")
        self.so_ids = self.qrf_id.report_file.datas
        return {'type': 'ir.actions.client'}
        # return { 
        #     'type' : 'ir.actions.do_nothing'
        # }
        # return self.env.ref('master_specifications.action_qrf_report').report_action(self.qrf_id)
