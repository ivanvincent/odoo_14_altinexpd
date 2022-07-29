from odoo import models, fields, api

class MasterHandling(models.Model):
    _name = 'master.handling'

    name = fields.Char(string='Name')
    active = fields.Boolean(string='Active', default=True)