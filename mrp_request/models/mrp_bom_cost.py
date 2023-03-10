from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpBomCost(models.Model):
	_name = "mrp.bom.cost"
	_description ="Mrp Bom Variable Cost"

	name 		= fields.Many2one('mrp.bom.cost.parameter', string='Parameter Cost',)
	bom_id 		= fields.Many2one("mrp.bom", "Bom ID",)
	amount 		= fields.Float(string='Qty',)
	amount_tot 	= fields.Float(string='Qty Total', compute='_compute_tot_amount')
	amount_cost	= fields.Float(string='Total Price', compute='_compute_tot_amount')
	price_unit	= fields.Float(string='Price Std',)
	keterangan 	= fields.Char(string='Keterangan',)

	def _compute_tot_amount(self):
		for rec in self:
			rec.amount_tot = rec.bom_id.product_qty * rec.amount
			rec.amount_cost = rec.amount_tot * rec.price_unit

class ProductTextileBomCostParameter(models.Model):
	_name = "mrp.bom.cost.parameter"
	_description = "Mrp Bom Variable Cost"

	name 		= fields.Char(string='Parameter Name')
	code 		= fields.Char(string='Code',)
	active 		= fields.Boolean(string='active', default=True)
	account_id  = fields.Many2one('account.account', string='Account')