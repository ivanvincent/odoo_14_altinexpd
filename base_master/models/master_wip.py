from odoo import models, fields, api

class MasterWip(models.Model):
    _name = 'master.wip'

    name = fields.Char(string='Name')