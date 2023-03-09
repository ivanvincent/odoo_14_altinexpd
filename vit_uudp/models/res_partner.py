from odoo import api, fields, models


class PartnerAccount(models.Model):
	_name = 'res.partner.account'
	_description = 'Customer Account'
	_inherit = ['mail.thread', 'mail.activity.mixin' ]
	_order = 'name'

	name = fields.Char(string='Account', required=True, track_visibility="onchange" )


#class Partner(models.Model):
#	_inherit = 'res.partner'

#	kode_customer = fields.Char(string='Kode Customer', index=True, readonly=False)
#	kode_supplier = fields.Char(string='Kode Supplier')
#	cabang = fields.Many2one('res.partner.cabang', string='Cabang')
#	wilayah = fields.Many2one('res.partner.wilayah', string='Wilayah')
#	customer_lead = fields.Float(string='Delivery Lead Time')
#	group =	fields.Many2one('crm.team', string='Group')
#	product_ids = fields.Many2many('product.product', 'res_partner_product_product_rel',  'partner_id', 'product_id', string="Products",domain="[('sale_ok','=',True)]")
#	fax_no = fields.Char("Fax")
#	partner_tax_type=fields.Selection([('pkp','PKP'),('non_pkp','Non PKP')],"Taxable Type")
#	vat = fields.Char('NPWP Number')
	
#	custom_group_id = fields.Many2one("res.partner.group","Partner Grouping")
#	custom_type_id = fields.Many2one("res.partner.type","Partner Type")
#	custom_loc_type_id = fields.Many2one("res.partner.location.type","Partner Loc.Type")
#	custom_div_id = fields.Many2one("res.partner.divisi","Partner Division")
#	custom_jalur_id = fields.Many2one("res.partner.jalur","Jalur")
	
	
	def _get_name(self):
		name = super(Partner, self)._get_name()
		if self.kode_customer:
			name = '['+self.kode_customer+'] '+name
		
		return name

	@api.model
	def create(self, vals):
		if not vals.get('kode_customer',True):
			if vals.get('customer') and not vals.get('parent_id'):
				vals['kode_customer'] = self.env['ir.sequence'].next_by_code('sequence.kode.customer')
			if vals.get('customer') and vals.get('parent_id'):
				vals['kode_customer'] = self.browse(vals.get('parent_id')).kode_customer

		result = super(Partner, self).create(vals)
		return result