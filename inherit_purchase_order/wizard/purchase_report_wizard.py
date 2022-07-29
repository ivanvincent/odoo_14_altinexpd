from odoo import fields, models, api, _
from odoo.exceptions import UserError

class PurchaseReportWizard(models.TransientModel):

    _name = 'purchase.report.wizard'
    
    
    report_type = fields.Selection([("vendor","Vendor"),("detal_vendor","Detail Vendor")], string='Report Type',default='vendor')

    def preview(self):
        ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        report_id = self.env[active_model].browse(ids)
        if self.report_type == 'vendor':
            return {
                'type': 'ir.actions.client',
                'tag': 'purchase_report_generic',
                'params': {
                    'url': '/reporting/output_format/purchase/active_id',
                    'model': 'report.po.supplier',
                    'active_id':report_id.id,
                    'report_type':'vendor',
                }
            }
            
