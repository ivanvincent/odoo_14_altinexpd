from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    uudp_credit_account_id   = fields.Many2one('account.account', string='Account Kredit Pengajuan')
    ajuan_sequence_id        = fields.Many2one('ir.sequence', string='Sequence Pengajuan')
    penyelesaian_sequence_id = fields.Many2one('ir.sequence', string='Sequence Penyelesaian')
    reimburse_sequence_id    = fields.Many2one('ir.sequence', string='Sequence Reimburse')
    domain_driver_ids        = fields.Many2many(comodel_name='hr.job', string='Domain Driver',relation="filter_uudp_job_driver_rel")
    domain_sales_ids         = fields.Many2many(comodel_name='hr.job', string='Domain Sales',relation="filter_uudp_job_sales_rel")
    domain_helper_ids        = fields.Many2many(comodel_name='hr.job', string='Domain Helper',relation="filter_uudp_job_helper_rel")
    
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config                = self.env['ir.config_parameter'].sudo()
        uudp_credit_account_id  = ir_config.get_param('uudp_credit_account_id')
        ajuan_sequence_id  = ir_config.get_param('ajuan_sequence_id')
        penyelesaian_sequence_id  = ir_config.get_param('penyelesaian_sequence_id')
        reimburse_sequence_id  = ir_config.get_param('reimburse_sequence_id')
        domain_driver_ids  = ir_config.get_param('domain_driver_ids')
        domain_sales_ids  = ir_config.get_param('domain_sales_ids')
        domain_helper_ids  = ir_config.get_param('domain_helper_ids')
        
        
        res.update(
            uudp_credit_account_id=int(uudp_credit_account_id),
            ajuan_sequence_id=int(ajuan_sequence_id),
            penyelesaian_sequence_id=int(penyelesaian_sequence_id),
            reimburse_sequence_id=int(reimburse_sequence_id),
            domain_driver_ids=[(6, 0, literal_eval(domain_driver_ids))] if domain_driver_ids else False,
            domain_sales_ids=[(6, 0, literal_eval(domain_sales_ids))] if domain_sales_ids else False,
            domain_helper_ids=[(6, 0, literal_eval(domain_helper_ids))] if domain_helper_ids else False,
        )
        
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("uudp_credit_account_id", self.uudp_credit_account_id.id)
        ir_config.set_param("ajuan_sequence_id", self.ajuan_sequence_id.id)
        ir_config.set_param("penyelesaian_sequence_id", self.penyelesaian_sequence_id.id)
        ir_config.set_param("reimburse_sequence_id", self.reimburse_sequence_id.id)
        ir_config.set_param("domain_driver_ids", self.domain_driver_ids.ids)
        ir_config.set_param("domain_sales_ids", self.domain_sales_ids.ids)
        ir_config.set_param("domain_helper_ids", self.domain_helper_ids.ids)
        
        
        
        