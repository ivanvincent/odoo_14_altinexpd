from odoo import models, fields, api, _
from odoo.exceptions import UserError

class InheritMktProductionLine(models.Model):
    _inherit = 'mkt.production.line'

    mrp_request_ids = fields.One2many('mrp.request', 'mkt_production_id', string='Mrp Request Line')