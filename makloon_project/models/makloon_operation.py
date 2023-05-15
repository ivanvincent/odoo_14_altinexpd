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
    purchase_category_id = fields.Many2one('purchase.order.category', string='Purchase Category')
    order_line = fields.One2many('makloon.operation.line', 'order_id', string='Makloon Operation Lines', copy=True,
                                track_visibility='onchange',)
    berita_acara_line = fields.One2many('makloon.operation.ba.line', 'order_id', string='Berita Acara', copy=True,
                                track_visibility='onchange',)

class MakloonOperationLine(models.Model):
    _name = "makloon.operation.line"
    _rec_name = 'product_category_id'

    order_id = fields.Many2one('makloon.operation', string='Makloon Operation', required=True, ondelete='cascade',
                                index=True, copy=False)
    product_category_id = fields.Many2one('product.category', 'Result')
    product_material_id = fields.Many2one('product.category', 'Material')
    name = fields.Char(string="Description")

class MakloonOperationBeritaAcaraLine(models.Model):
    _name = "makloon.operation.ba.line"
    
    name        = fields.Char(string="Name")
    order_id    = fields.Many2one('makloon.operation', string='Makloon Operation')
    
