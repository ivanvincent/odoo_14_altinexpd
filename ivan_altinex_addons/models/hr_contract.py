from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrContract(models.Model):
    _inherit = 'hr.contract'

    # wage = fields.Monetary('Gaji', required=True, tracking=True, help="Employee's monthly gross wage.")
    test = fields.Text(string='PERCOBAAN')
    
    