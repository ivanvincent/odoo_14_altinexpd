from odoo import api, fields, models

class PartnerDivisi(models.Model):
	_name = 'res.partner.divisi'
	_inherit = ['mail.thread', 'mail.activity.mixin' ]
	_order = 'name'
	_description = 'Divisi Customer'

	name = fields.Char(string='Divisi Customer', required=True, translate=True)
	description = fields.Text("Deskripsi")
	code = fields.Char("Code")

class PartnerGroup(models.Model):
	_name = 'res.partner.group'
	_inherit = ['mail.thread', 'mail.activity.mixin' ]
	_order = 'name'
	_description = 'Group Customer'
	
	name = fields.Char(string='Group Customer', required=True, translate=True)
	description = fields.Text("Deskripsi")
	code = fields.Char("Code")
	delivery_days = fields.Float(string='Delivery Lead Time')
	divisi_id = fields.Many2one('res.partner.divisi', string="Division" )

	customer_id = fields.Many2one('res.partner', string="Customer" )

#class PartnerJalur(models.Model):
#	_name = 'res.partner.jalur'
#	_inherit = ['mail.thread', 'mail.activity.mixin' ]
#	_order = 'name'
#	_description = 'Jalur Customer'

#	name = fields.Char(string='Customer Jalur', required=True, translate=True)
#	description = fields.Text("Deskripsi")
#	code = fields.Char("Code")
#	group_id = fields.Many2one('res.partner.group', string="Group" )
#	divisi_name = fields.Char('Division', related='group_id.divisi_id.name')


class PartnerCabang(models.Model):
	_name = 'res.partner.cabang'
	_order = 'name'
	_description = 'Cabang Customer'

	name = fields.Char(string='Cabang', required=True, translate=True)

class PartnerWilayah(models.Model):
	_name = 'res.partner.wilayah'
	_order = 'name'
	_description = 'Wilayah Customer'

	name = fields.Char(string='Wilayah', required=True, translate=True)

class PartnerType(models.Model):
	_name = 'res.partner.type'
	_order = 'name'
	_description = 'Type Customer'

	name = fields.Char(string='Customer Type', required=True, translate=True)
	description = fields.Text("Deskripsi")
	code = fields.Text("Code")

class PartnerLocationType(models.Model):
	_name = 'res.partner.location.type'
	_order = 'name'
	_description = 'Location Type Customer'

	name = fields.Char(string='Customer Location Type', required=True, translate=True)
	description = fields.Text("Deskripsi")
	code = fields.Text("Code")

class Partner(models.Model):
	_inherit = 'res.partner'


	#@api.onchange('custom_jalur_id')
	#def onchange_custom_jalur_id(self):
		
	#	old_group_id = self.custom_group_id
	#	new_group_id = self.custom_jalur_id.group_id.id

	#	if new_group_id != old_group_id:
	#		self.custom_group_id = new_group_id

	#@api.onchange('custom_group_id')
	#def onchange_custom_group_id(self):

	#	old_div_id = self.custom_div_id
	#	new_div_id = self.custom_group_id.divisi_id.id

	#	if new_div_id != old_div_id:
	#		self.custom_div_id = new_div_id


	kode_customer = fields.Char(string='Kode Customer', index=True, readonly=False)
	kext_customer = fields.Char(string='Kode External')

	kode_supplier = fields.Char(string='Kode Supplier')
	kext_supplier = fields.Char(string='Kode External')

	cabang = fields.Many2one('res.partner.cabang', string='Cabang')
	wilayah = fields.Many2one('res.partner.wilayah', string='Wilayah')
	customer_lead = fields.Float(string='Delivery Lead Time')
	group =	fields.Many2one('crm.team', string='Group')
	product_ids = fields.Many2many('product.product', 'res_partner_product_product_rel',  'partner_id', 'product_id', string="Products",domain="[('sale_ok','=',True)]")
	fax_no = fields.Char("Fax")
	partner_tax_type=fields.Selection([('pkp','PKP'),('non_pkp','Non PKP')],"Taxable Type")
	vat = fields.Char('NPWP Number')

	custom_jalur_id = fields.Many2one("res.partner.jalur","Route")
	custom_type_id = fields.Many2one("res.partner.type","Partner Type")
	custom_loc_type_id = fields.Many2one("res.partner.location.type","Partner Loc.Type")
	custom_group_id = fields.Many2one("res.partner.group","Partner Grouping")
	
	custom_div_id = fields.Many2one("res.partner.divisi","Partner Division")

	custom_acc_id =fields.Selection([	('indomaret','Indomaret'),
										('alfagroup','Alfa Group'),
										('lainnya','Lainnya')
									],"Partner Account",default="lainnya")
	kode_mkt = fields.Selection([("cash","Cash"),("card","Card")], string='Payment Method')


	def _get_name(self):
		name = super(Partner, self)._get_name()
		if self.kode_customer:
			if name[0:1] != '[':
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

# class ProductProduct(models.Model):
#     _inherit = 'product.product'

    # partner_id = fields.Many2one('res.partner', string="Customer") 