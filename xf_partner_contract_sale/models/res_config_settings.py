# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.addons.xf_partner_contract.models.selection import UseContract


class Company(models.Model):
    _inherit = 'res.company'

    use_sale_contract = fields.Selection(
        string='Use Contract for Sale Orders',
        selection=UseContract.list,
        default=UseContract.default,
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_sale_contract = fields.Selection(
        string='Use Contract for Sale Orders',
        related='company_id.use_sale_contract',
        readonly=False,
    )
