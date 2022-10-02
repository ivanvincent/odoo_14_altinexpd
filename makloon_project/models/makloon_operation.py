from collections import namedtuple
import json
import time

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
# from odoo.addons.procurement.models import procurement
from odoo.exceptions import UserError

class MakloonOperation(models.Model):

    _name = "makloon.operation"

    _description = "Operation for Makloon"

    name = fields.Char(string="Jenis Makloon", required=True)
    sequence = fields.Integer("Sequence", default=1)



