from odoo import api, fields, models, _
import datetime

class Hr_contract_detail(models.Model):
    _name = 'hr.contract.detail'

    schedule_id 			= fields.Many2one(comodel_name='resource.calendar', string='Schedule')
    contract_id				= fields.Many2one(comodel_name='hr.contract', string='Contract')
    start_date	 			= fields.Date("Starting Date")
    end_date	 			= fields.Date("End Date")
