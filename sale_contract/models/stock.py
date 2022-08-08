# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import psycopg2
from functools import partial
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, Warning
import odoo.addons.decimal_precision as dp
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	contract_id = fields.Many2one('sale.contract', string='No. Sales Forcast')
	
	# @api.multi
	def create_invoice(self):
		res = super(StockPicking, self).create_invoice()
		for picking in self :
			if picking.sale_id :
				picking.sale_id.contract_id.is_invoiced()
		return res
