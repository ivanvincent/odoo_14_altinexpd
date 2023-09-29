from odoo import models, fields, api

class MasterQty(models.Model):
    _name = 'master.qty'

    name = fields.Char(string='Name')