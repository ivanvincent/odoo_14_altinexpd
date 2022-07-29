from odoo import fields, models, api, _
from datetime import date, datetime

class ProductPersupplierWizard(models.TransientModel):
    _name = 'product.persupplier.wizard'

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, )
    date_start = fields.Date(string='Date Start')
    date_end   = fields.Date(string='Date End')

    def action_print(self):
        print('=======action_print=========')
        domain = [('partner_id', '=', self.partner_id.id)]
        if self.date_start: domain.append(('date_approve', '>=', self.date_start))
        if self.date_end: domain.append(('date_approve', '<=', self.date_start))
        po_obj = self.env['purchase.order'].search(domain)
        url = self.env.ref('inherit_inventory.url_image_receipt').read()[0]['value']
        data = []
        for a in po_obj.picking_ids.filtered(lambda x:x.state == 'done'):
            for b in a.move_ids_without_package:
                vals = {
                    'product_name' : b.product_id.name,
                    'no_po'      : a.origin,
                    'tanggal_receipt' : a.date_done,
                    'keterangan' : b.picking_id.name,
                    'image_ids' : [{'filename' : str(img.id) + img.format_file, 'image_desc' : img.image_desc}  for img in b.image_ids]
                }
                data.append(vals)
        data = {
            'ids': self.ids,
            'model': 'product.persupplier.wizard',
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'data' : data,
                'vendor' : self.partner_id.name,
                'image_url' : url
            },
        }

        return self.env.ref('inherit_inventory.action_report_product_persupplier').report_action(None, data=data)

class ReportProductPersupplier(models.AbstractModel):
    _name = 'report.inherit_inventory.report_product_persupplier'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('_get_report_values')
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        docs = data['form']['data']
        vendor = data['form']['vendor']
        image_url = data['form']['image_url']
        return {
            'doc_ids': data['ids'],
            'date_start': date_start,
            'date_end': date_end,
            'docs': docs,
            'doc_ids' : docids,
            'vendor' : vendor,
            'image_url' : image_url,
        }
