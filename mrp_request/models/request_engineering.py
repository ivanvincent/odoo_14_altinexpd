from odoo import models, fields, api

class RequestEngineering(models.Model):
    _inherit = 'request.engineering'

    request_id = fields.Many2one('mrp.request', string='Mor')