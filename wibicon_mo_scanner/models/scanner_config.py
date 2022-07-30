from odoo import models, fields, api, _
from odoo.exceptions import UserError





class ScannerSession(models.Model):
    _name = 'mrp.scanner.session'


    SCANNER_SESSION_STATE = [
        ('opening_control', 'Opening Control'),  # method action_pos_session_open
        ('opened', 'In Progress'),               # method action_pos_session_closing_control
        ('done', 'Done'),
    ]

    name      = fields.Char(string='Session ID', required=True, readonly=True, default='/')
    
    config_id = fields.Many2one(
        'mrp.scanner.config', string='Scanner Configuration',
        required=True,
        index=True)
    
    state = fields.Selection(
        SCANNER_SESSION_STATE, string='Status',
        required=True, readonly=True,
        index=True, copy=False, default='opening_control')
    
    
    _sql_constraints = [('uniq_name', 'unique(name)', "The name of this Scanner Session must be unique !")]
    
    

class ScannerConfig(models.Model):
    _name = 'mrp.scanner.config'

    name      = fields.Char(string='Scanner Config')
    scan_type = fields.Selection([("auto","Auto"),("linier","Lininer")], string='Scanning Type')