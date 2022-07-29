from odoo import models, fields, api

class PartnerAddress(models.Model):
    _name = 'partner.address'

    name = fields.Char(string='Alamat')
    partner_id = fields.Many2one('res.partner', string='Partner', required=False, )