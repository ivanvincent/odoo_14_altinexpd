from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    uudp_credit_account_id   = fields.Many2one('account.account', string='Account Kredit Pengajuan')
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config                = self.env['ir.config_parameter'].sudo()
        uudp_credit_account_id  = ir_config.get_param('uudp_credit_account_id')
        
        
        res.update(
            uudp_credit_account_id=int(uudp_credit_account_id),
        )
        
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("uudp_credit_account_id", self.uudp_credit_account_id.id)
        
        
        
        