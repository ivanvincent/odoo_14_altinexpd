from odoo import models, fields

class Accessories(models.Model):
	_name = 'accessories'

	name  = fields.Char('Name')
	state = fields.Boolean('State')

class HangTag(models.Model):
	_name = 'hang.tag'

	name  = fields.Char('Name')	
	state = fields.Boolean('State')

class SaleContractPacking(models.Model):
	_name = 'sale.contract.packing'

	name  = fields.Char('Name')	
	state = fields.Boolean('State')