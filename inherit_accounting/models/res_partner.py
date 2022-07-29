from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    address_ids = fields.One2many('partner.address', 'partner_id', 'Partner Address')