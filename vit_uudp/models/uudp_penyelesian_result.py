from odoo import models, fields, api, _
from odoo.exceptions import UserError

class UudpHasilPenyelasaianResult(models.Model):
    _name = 'uudp.hasil.penyelesian'

    name = fields.Char(string='Label dari Field')