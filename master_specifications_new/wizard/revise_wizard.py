from odoo import fields, models, api, _
from odoo.exceptions import UserError

class ReviseWizard(models.TransientModel):
    _name = 'revise.wizard.new'

    note          = fields.Text(string='Note Revisi')
    qrf_id        = fields.Many2one('quotation.request.form.new', string='Quotation', required=True,)
    so_ids        = fields.Binary(string='SO')
    so_name       = fields.Char('Name')
    drawing_ids   = fields.Binary(string='Drawing')
    dwg_name      = fields.Char('Name')
    

    def action_print(self):
        print("action_print")
        for rec in self:
            if rec.qrf_id.state == 'qrf_upload':
                rec.qrf_id.state = 'draft'
                rec.qrf_id.sudo().message_post(body="<strong>%s</strong>" % (
                            rec.note))
            elif rec.qrf_id.state == 'dwg_upload':
                rec.qrf_id.state = 'qrf_upload'
                rec.qrf_id.sudo().message_post(body="<strong>%s</strong>" % (
                            rec.note))
            elif rec.qrf_id.state == 'waiting':
                rec.qrf_id.state = 'dwg_upload'
                rec.qrf_id.sudo().message_post(body="<strong>%s</strong>" % (
                            rec.note))
            elif rec.qrf_id.state == 'approved':
                rec.qrf_id.state = 'dwg_upload'
                rec.qrf_id.sudo().message_post(body="<strong>%s</strong>" % (
                            rec.note))

    def action_submit_cancel(self):
        for rec in self:
            if rec.qrf_id.state == 'approved':
                rec.qrf_id.state = 'cancel'
                rec.qrf_id.sudo().message_post(body="<strong>%s</strong>" % (
                            rec.note))

    def action_so(self):
        print("action_so")
        return self.env.ref('master_specifications_new.action_qrf_report_new').report_action(self.qrf_id)
        return True
