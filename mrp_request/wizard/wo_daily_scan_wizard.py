from odoo import fields, models, api, _
from odoo.exceptions import UserError

class WoDailyScanWizard(models.TransientModel):
    _name = 'wo.daily.scan.wizard'

    scanner     = fields.Char('Scanner')

    # @api.model
    def barcode_scan(self):
        action = self.env.ref('mrp_request.workorder_daily_wizard_action').read()[0]
        return action
    
    @api.onchange('scanner')
    def _onchange_qr_code(self):
        if self.scanner:
            return {
                'warning' : {
                    'title' : 'Success',
                    'message' : 'Hasil Scanner %s' % (self.scanner)
                }
            }
