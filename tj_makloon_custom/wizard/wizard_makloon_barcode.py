from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError

class AssetBarcode(models.TransientModel):
    _name = "wiz.makloon.barcode"
    _description = "Wizard Makloon Barcode"

    barcode_ids = fields.Many2many(comodel_name="stock.production.lot", string="Barcode", )

    # @api.multi
    def action_barcode(self):
        if len(self.barcode_ids) == 0:
            raise ValidationError(_('List Empty!'))

        # writing to One2many asset_ids
        self.write({'barcode_ids': self.barcode_ids})
        context = {
            'lang': 'en_US',
            'active_ids': [self.id],
        }

        return {
            'context': context,
            'data': None,
            'type': 'ir.actions.report.xml',
            'report_name': 'tj_makloon_custom.report_makloon_barcode_menu',
            'report_type': 'qweb-pdf',
            'report_file': 'tj_makloon_custom.report_makloon_barcode_menu',
            'name': 'Makloon Barcode',
            'flags': {'action_buttons': True},
        }