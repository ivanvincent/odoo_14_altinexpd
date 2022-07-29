from odoo import api, fields, models, _
from odoo.exceptions import UserError
# from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons import decimal_precision as dp

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	is_free_product = fields.Boolean("Free Product",help="Tick this checkbox if this line is for free product")
	product_uom_qty = fields.Float(string='Ordered Quantity', digits=dp.get_precision('Sale Product Unit of Measure'), required=True, default=1.0)
	price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Sale Price Unit'), default=0.0)
	
	#@api.multi
	# @api.onchange('product_id')
	# def product_id_change(self):
	# 	existings = {}
	# 	if self.product_id:
	# 		for line in self.order_id.order_line:
	# 			c = existings.get(line.product_id.id,0)

	# 			if c==0 and line.price_unit > 0.0:
	# 				existings.update({line.product_id.id:c+1})
	# 			else:
	# 				if self.price_unit>0.0 and not self.is_free_product:
	# 					raise UserError(_('You can not have same product named  %s in one order unless one of the price is 0'%line.product_id.name))
	# 				else:
	# 					self.price_unit=0.0

	# 	if self.order_id.partner_id:
	# 		self.customer_lead = self.product_id.product_tmpl_id.sale_delay + self.order_id.partner_id.customer_lead
	# 	result = super(SaleOrderLine, self).product_id_change()
	# 	value = result.get('value',result)
	# 	if value in (True,False):
	# 		value = {}
	# 	value.update({'price_unit':0.0})
	# 	result.update({'value':value})
	# 	return result


class SaleOrder(models.Model):
	_inherit = "sale.order"

	# @api.model
	# def load(self, fields, data):
	# 	""" Overridden for better performances when importing a list of account
	# 	with opening debit/credit. In that case, the auto-balance is postpone
	# 	until the whole file has been imported.
	# 	"""
		
	# 	rslt = super(SaleOrder, self).load(fields, data)
	# 	print ("fields ==============",fields)
	# 	print ("data ==============",data)
	# 	# if 'import_file' in self.env.context:
	# 	# 	companies = self.search([('id', 'in', rslt['ids'])]).mapped('company_id')
	# 	# 	for company in companies:
	# 	# 		company._auto_balance_opening_move()
	# 	return rsltch

	@api.model
	def create(self,vals):
		if vals.get('partner_id',False):
			partner = self.env['res.partner'].browse(vals.get('partner_id'))

			if partner:
				payment_term_id = partner.property_payment_term_id and partner.property_payment_term_id.id or False
				
				# type_id = partner.custom_type_id.id or False
				# lokasi_id = partner.custom_loc_type_id.id or False
				divisi_id = partner.custom_div_id.id or False
				group_id = partner.custom_group_id.id or False
				jalur_id = partner.custom_jalur_id.id or False

				vals.update({'payment_term_id': payment_term_id,
							# 'custom_type_id': type_id,
							# 'custom_loc_type_id': lokasi_id,
							#'custom_div_id': divisi_id,
							#'custom_group_id': group_id,
							# 'custom_jalur_id': jalur_id
							})
		res = super(SaleOrder,self).create(vals)
		return res

	client_order_ref = fields.Char(string='PO. Customer', copy=False)
	#any_quick_leadtime = fields.Boolean("Is Urgent Order?",compute='_compute_urgent_lines',store=True)

	custom_div_id = fields.Many2one("res.partner.divisi","Division", store=True)
	custom_group_id = fields.Many2one("res.partner.group","Grouping", store=True)
	custom_jalur_id = fields.Many2one("res.partner.jalur","Route", store=True)

	# custom_type_id = fields.Many2one("res.partner.type","Partner Type", store=True)
	# custom_loc_type_id = fields.Many2one("res.partner.location.type","Partner Location Type", store=True)
	# canvasser_pick_id = fields.Many2one("stock.picking","Canvasser Picking")
	# lpb = fields.Char("LPB")

	state = fields.Selection([
		('draft', 'Quotation'),
		('sent', 'Quotation Sent'),
		('pmc', 'Confirm Leadtime'),
		('sale', 'Sales Order'),
		('done', 'Locked'),
		('cancel', 'Cancelled'),
		], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')

	#@api.depends('order_line', 'order_line.customer_lead')
	#def _compute_urgent_lines(self):
	#	for order in self:
	#		for line in order.order_line:
	#			if line.customer_lead<3:
	#				order.any_quick_leadtime=True

	#@api.onchange('partner_id')
	#def _onchange_picking_type(self):
	#	if self.partner_id:
	#		self.custom_div_id = self.partner_id.custom_div_id.id or False
	#		self.custom_group_id = self.partner_id.custom_group_id.id or False
	#		self.custom_jalur_id = self.partner_id.custom_jalur_id.id or False
	# 		self.custom_type_id = self.partner_id.custom_type_id.id or False
	# 		self.custom_loc_type_id = self.partner_id.custom_loc_type_id.id or False