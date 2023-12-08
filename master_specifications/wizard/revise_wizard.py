from odoo import fields, models, api, _
from odoo.exceptions import UserError

class ReviseWizard(models.TransientModel):
    _name = 'revise.wizard'

    note          = fields.Text(string='Note Revisi')
    qrf_id        = fields.Many2one('quotation.request.form', string='Quotation', required=True,)
    

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
                rec.qrf_id.state = 'waiting'
                rec.qrf_id.sudo().message_post(body="<strong>%s</strong>" % (
                            rec.note))