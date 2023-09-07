from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import logging
from odoo.addons.auth_signup.models.res_partner import SignupError, now
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    bukti_transfer_url = fields.Char(string='Proof Of Payments', readonly=False, store=True)
    identitas_url      = fields.Char(string='Id Photo', readonly=False, store=True)
    identitas_number   = fields.Char(string='Id Number', readonly=False, store=True,)
    gender_user        = fields.Selection([("male","Male"),("female","Female")], string='Gender', readonly=False, store=True)
    job_users          = fields.Char(string='Job',readonly=False, store=True,)
    address            = fields.Char(string='Address', readonly=False, store=True,)
    # recharge_ids       = fields.One2many('recharge','user_id', string='Recharge')
    bukti_transfer_binary = fields.Binary(string='Proof Of Payments')
    identitas_url_binary = fields.Binary(string='Id Photo')
    # vdociper_currenttime_id = fields.One2many('vdochiper.currenttime', 'user_id', string='Current time video')