from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError

class Assetpurchase(models.TransientModel):
    _name = "wiz.makloon.hpp"
    _description = "Wizard Makloon HPP"

    hpp_ids = fields.Many2many(comodel_name="makloon.hpp", string="Makloon Hpp", )

    # @api.multi
    def action_hpp(self):
        if len(self.hpp_ids) == 0:
            raise ValidationError(_('List Empty!'))

        # writing to One2many asset_ids
        self.write({'hpp_ids': self.hpp_ids})
        context = {
            'lang': 'en_US',
            'active_ids': [self.id],
        }

        return {
            'context': context,
            'data': None,
            'type': 'ir.actions.report.xml',
            'report_name': 'tj_makloon_custom.report_makloon_hpp_menu',
            'report_type': 'qweb-pdf',
            'report_file': 'tj_makloon_custom.report_makloon_hpp_menu',
            'name': 'Makloon HPP',
            'flags': {'action_buttons': True},
        }