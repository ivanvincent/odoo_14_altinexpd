from odoo import models, fields, api

class StreetDelivery(models.Model):
    _name = 'street.delivery'

    name        = fields.Text(string='Name')
    active      = fields.Boolean(string='Active')
    company_id  = fields.Many2one('res.company', string='Company')