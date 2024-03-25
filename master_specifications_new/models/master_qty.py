<<<<<<< HEAD
from odoo import models, fields, api

class MasterQty(models.Model):
    _name = 'master.qty.new'
    _order = "urutan asc"

    name = fields.Char(string='Name')
=======
from odoo import models, fields, api

class MasterQty(models.Model):
    _name = 'master.qty.new'
    _order = "urutan asc"

    name = fields.Char(string='Name')
>>>>>>> 42cdb9030f851b5fe403eed06a6fc058da9468d8
    urutan = fields.Integer(string='Urutan', default=99)