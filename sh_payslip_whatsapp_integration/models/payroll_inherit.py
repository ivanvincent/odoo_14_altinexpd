# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import uuid


class sh_send_whatsapp_message(models.TransientModel):
    _inherit = "sh.base.send.whatsapp.message.wizard"

    employee_ids = fields.Many2one("hr.employee", string="Recipients ")

    def action_paylsip_send_whatsapp_message(self):
        for rec in self:
            if not rec.employee_ids:
                raise UserError("Please select Recipient !")
            if self.employee_ids:
                for employee in self.employee_ids:
                    sh_message = ""
                    if self.message:
                        sh_message = str(self.message).replace(
                            '*', '').replace('_', '').replace('%0A', '<br/>').replace('%20', ' ').replace('%26', '&')

                    if employee.mobile:
                        return {
                            'type':
                            'ir.actions.act_url',
                            'url':
                            "https://web.whatsapp.com/send?l=&phone=" +
                            employee.mobile + "&text=" +
                            rec.message.replace('&', '%26'),
                            'target':
                            'new',
                            'res_id':
                            rec.id,
                        }
                    else:
                        raise UserError("Employee Mobile Number Not Exist")


class Employee(models.Model):
    _inherit = 'hr.employee'

    mobile = fields.Char("Personal Mobile")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    report_token = fields.Char("Access Token")
    payslip_url = fields.Text('Url')

    def action_quotation_send_wp(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        if not self.employee_id.mobile:
            raise UserError(_("Employee's Mobile Number Not Exist !"))

        self.ensure_one()
        lang = self.env.context.get('lang')
        template = self.env.ref(
            'sh_payslip_whatsapp_integration.email_template_edi_payslip_custom')
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {

            'default_model': 'hr.payslip',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template.id),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            # 'model_description': self.with_context(lang=lang).type_name,
            'default_is_wp': True,
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name)

    def _get_token(self):
        """ Get the current record access token """
        if self.report_token:
            return self.report_token
        else:
            report_token = str(uuid.uuid4())
            self.write({'report_token': report_token})
            return report_token

    def get_download_report_url(self):
        url = ''
        if self.id:
            self.ensure_one()
            url = '/download/payslip/' + '%s?access_token=%s' % (
                self.id, self._get_token())
        return url

    text_message = fields.Text("Message", compute="get_message_detail")

    @api.depends('employee_id', 'company_id')
    def get_message_detail(self):
        if self:
            for rec in self:
                # rec.txt_message = False
                txt_message = ""
                if rec.company_id.payroll_information_in_message and rec.employee_id and rec.company_id:
                    txt_message += "Hello " + '*' + str(
                        rec.employee_id.name
                    ) + '*' + "," + "%0A%0A" + "Your payslip for period " + '*' + str(
                        rec.date_from.strftime(
                            "%d-%m-%Y")) + '*' + " to " + '*' + str(
                                rec.date_to.strftime("%d-%m-%Y")
                    ) + '*' + " is generated. " + "%0A"

                if rec.company_id.payroll_send_pdf_in_message:
                    base_url = self.env['ir.config_parameter'].sudo(
                    ).get_param('web.base.url')
                    quot_url = "%0A%0A Payslip Report Download Link : %0A" + base_url + rec.get_download_report_url(
                    )
                    self.write({'payslip_url': base_url
                               + rec.get_download_report_url()})
                    txt_message += quot_url + "%0A%0A" + " Thank you. "

                if rec.company_id.payroll_signature and rec.env.user.sign:
                    txt_message += "%0A%0A%0A" + str(rec.env.user.sign)
            rec.text_message = txt_message.replace('&', '%26')

    def send_by_whatsapp_direct(self):
        if self.employee_id.mobile:
            return {
                'type':
                'ir.actions.act_url',
                'url':
                "https://web.whatsapp.com/send?l=&phone=" +
                self.employee_id.mobile + "&text=" +
                self.text_message.replace('&', '%26'),
                'target':
                'new',
                'res_id':
                self.id,
            }
        else:
            raise UserError("Employee Mobile Number Not Exist")
