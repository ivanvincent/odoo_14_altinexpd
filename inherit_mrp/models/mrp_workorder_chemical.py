from odoo import models, fields, api

class MrpWorkOrderChemical(models.Model):
    _name = 'nama.model'

    name = fields.Char(string='Label dari Field')