from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError

class Assetpurchase(models.TransientModel):
    _name = "wiz.makloon.harga.outlet"
    _description = "Wizard Makloon Harga Outlet"

    harga_outlet_ids = fields.Many2many(comodel_name="makloon.harga.outlet", string="Makloon Harga Outlet", )

    # @api.multi
    def action_harga_outlet(self):
        if len(self.harga_outlet_ids) == 0:
            raise ValidationError(_('List Empty!'))

        # writing to One2many asset_ids
        self.write({'harga_outlet_ids': self.harga_outlet_ids})
        context = {
            'lang': 'en_US',
            'active_ids': [self.id],
        }

        return {
            'context': context,
            'data': None,
            'type': 'ir.actions.report.xml',
            'report_name': 'tj_makloon_custom.report_makloon_harga_outlet_menu',
            'report_type': 'qweb-pdf',
            'report_file': 'tj_makloon_custom.report_makloon_harga_outlet_menu',
            'name': 'Makloon Harga Outlet',
            'flags': {'action_buttons': True},
        }