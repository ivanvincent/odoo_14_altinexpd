
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import mysql.connector
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    mysql_host      = fields.Char(string='Mysql Host')
    mysql_port      = fields.Integer(string='Mysql Port')
    mysql_username  = fields.Char(string='Mysql User')
    mysql_password  = fields.Char(string='Mysql Pass')
    mysql_database  = fields.Char(string='Mysql Database Name')
    
    
    def check_mysql_connection(self):
        connection  = mysql.connector.connect(user=self.mysql_username,
                                            password=self.mysql_password,      
                                            host=self.mysql_host,
                                            charset='utf8',
                                            database=self.mysql_database,port=self.mysql_port,use_pure=True)
        
        if connection:
            raise ValidationError('Database Connected')
        
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config       = self.env['ir.config_parameter'].sudo()
        mysql_host      = ir_config.get_param('mysql_host')
        mysql_port      = ir_config.get_param('mysql_port')
        mysql_username  = ir_config.get_param('mysql_username')
        mysql_password  = ir_config.get_param('mysql_password')
        mysql_database  = ir_config.get_param('mysql_database')
        res.update(
            mysql_host=mysql_host,
            mysql_port=mysql_port,
            mysql_username=mysql_username,
            mysql_password=mysql_password,
            mysql_database=mysql_database,
        )
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        if self.mysql_password:
            _logger.warning('='*40)
            _logger.warning('MYSQL PASS')
            _logger.warning(self.mysql_password)
            _logger.warning('='*40)
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("mysql_host", self.mysql_host or "")
        ir_config.set_param("mysql_port", self.mysql_port or 0)
        ir_config.set_param("mysql_username", self.mysql_username or "")
        ir_config.set_param("mysql_password", self.mysql_password or "")
        ir_config.set_param("mysql_database", self.mysql_database or "")