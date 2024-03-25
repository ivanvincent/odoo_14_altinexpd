from odoo import models, fields, api

class MasterQty(models.Model):
    _name = 'master.qty.new'
    _order = "urutan asc"

    name = fields.Char(string='Name')
    urutan = fields.Integer(string='Urutan', default=99)