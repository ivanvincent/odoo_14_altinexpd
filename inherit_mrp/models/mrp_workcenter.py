from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'
    
    
    production_type_id = fields.Many2one('mrp.type', string='Production Type')
    is_planning        = fields.Boolean(string='Is Planning ?')

    