from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError

class Assetpurchase(models.TransientModel):
    _name = "wiz.makloon.purchase.order"
    _description = "Wizard Makloon Purchase Order"

    purchase_ids = fields.Many2many(comodel_name="purchase.order.line", string="Purchase Order Line", )

    # @api.multi
    def action_purchase(self):
        if len(self.purchase_ids) == 0:
            raise ValidationError(_('List Empty!'))

        # writing to One2many asset_ids
        self.write({'purchase_ids': self.purchase_ids})
        context = {
            'lang': 'en_US',
            'active_ids': [self.id],
        }

        return {
            'context': context,
            'data': None,
            'type': 'ir.actions.report.xml',
            'report_name': 'tj_makloon_custom.report_makloon_purchase_menu',
            'report_type': 'qweb-pdf',
            'report_file': 'tj_makloon_custom.report_makloon_purchase_menu',
            'name': 'Makloon Purchase',
            'flags': {'action_buttons': True},
        }