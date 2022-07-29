from odoo import api, fields, models

class AccountInvoice(models.Model):
	_inherit = "account.invoice"
	
	custom_group_id = fields.Many2one("res.partner.group","Partner Grouping", store=True)
	custom_type_id = fields.Many2one("res.partner.type","Partner Type", store=True)
	custom_loc_type_id = fields.Many2one("res.partner.location.type","Partner Loc.Type", store=True)
	custom_div_id = fields.Many2one("res.partner.divisi","Partner Division", store=True)
	custom_jalur_id = fields.Many2one("res.partner.jalur","Partner Jalur", store=True)