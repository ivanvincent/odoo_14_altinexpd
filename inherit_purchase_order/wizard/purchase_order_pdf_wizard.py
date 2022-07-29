from odoo import fields, models, api, _
from odoo.exceptions import UserError

class PurchaseOrderPdfWizard(models.TransientModel):
    _name = 'purchase.order.pdf.wizard'

    date_start = fields.Date(string='Date Start', required=True, )
    date_end = fields.Date(string='Date End', required=True, default=fields.Date.today())

    def action_get_pdf(self):
        print('action_get_pdf')
        po_obj = self.env['purchase.order'].search([('create_date', '>', self.date_start), ('create_date', '<', self.date_end)])
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'data' : [{'name': a.name, 'vendor': a.partner_id.name, 'origin': a.origin, 'amount_total': a.amount_total, 'inv_state': dict(a._fields['invoice_status'].selection).get(a.invoice_status)} for a in po_obj],
            },
        }
        return self.env.ref('inherit_purchase_order.action_report_purchase_order').report_action(None, data=data)
    
class ReportPurhaseOrder(models.AbstractModel):
    _name = 'report.inherit_purchase_order.report_purchase_order_periode'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('_get_report_values')
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        docs = data['form']['data']
        print(docs)
        return {
            'doc_ids': data['ids'],
            'date_start': date_start,
            'date_end': date_end,
            'docs': docs,
            'doc_ids' : docids,
        }