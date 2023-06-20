from odoo import api, exceptions, fields, models, _

class ResPartnerJalur(models.Model):
    _name = "res.partner.jalur"
    _description = "Partner Jalur"
    _inherit = ['mail.thread', 'mail.activity.mixin' ]
    _order = 'code, name, id'
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
        ('name_uniq', 'unique (name)', 'The name must be unique !')
    ]

    def _def_domain_plate_number(self):
        category = self.env['account.asset.category'].search([('name','ilike','kendaraan')])
        domain = [('category_id','in', category.ids)]
        return domain
    #divisi2_id = fields.Many2one("res.partner.divisi2", "Divisi 2")
    spv_id = fields.Many2one("res.partner", "Supervisor", domain="[('is_spv','=',True)]")
    code = fields.Char('Code', required=True, index=True)
    name = fields.Char('Name', required=True, index=True)
    description = fields.Text("Deskripsi")
    plate_number_id = fields.Many2one(
        'account.asset.asset',
        string='Mobil',
        domain= _def_domain_plate_number
    )
    # plate_number = fields.Char(string='Mobil')

    #djoyo
    salesperson_id = fields.Many2one("hr.employee", "Supervisor", track_visibility='onchange' )
    
    account_id = fields.Many2one("res.partner.account", "Partner Account",)
    #  track_visibility='onchange'
    divisi1_id = fields.Many2one("res.partner.divisi1", "Partner Divisi 1", track_visibility='onchange' )
    divisi2_id = fields.Many2one("res.partner.divisi2", "Partner Divisi 2", track_visibility='onchange' )
    group_id = fields.Many2one("res.partner.group", "Partner Group", track_visibility='onchange' )
    divisi_id = fields.Many2one("res.partner.divisi", "Partner Division", track_visibility='onchange' )
    #divisi_name = fields.Char('Division', related='group_id.divisi_id.name', store=True)

    def name_get(self):
        result = []
        for record in self:
            if record.code:
                display_name = '[' + record.code + '] ' + record.name
            else:
                display_name = record.name
            result.append((record.id, display_name))
        return result


class ResPartnerJalurLine(models.Model):
    _name = "res.partner.jalur.line"
    _description = "Partner Jalur JWK"
    _inherit = ['mail.thread', 'mail.activity.mixin' ]

    name = fields.Char(readonly="1")
    active = fields.Boolean("Active", default="true", track_visibility="onchange" )

    jalur_line_id = fields.Many2one("res.partner", "Customer", required=True)
    jalur_id = fields.Many2one("res.partner.jalur", "Route", required=True)
    jwk = fields.Selection([
        ('1', 'Senin'),
        ('2', 'Selasa'),
        ('3', 'Rabu'),
        ('4', 'Kamis'),
        ('5', 'Jumat'),
        ('6', 'Sabtu'),
        ('7', 'Minggu')
    ], string='JWK', track_visibility='onchange')
    jam = fields.Float("Jam", default=0, track_visibility='onchange' )

    #cust_int_code = fields.Char('Int.Code', related='jalur_line_id.kode_customer', store=True)
    #cust_ext_code = fields.Char('Ext.Code', related='jalur_line_id.kext_customer', store=True)
    #cust_city = fields.Char('City', related='jalur_line_id.city', store=True)
    #cust_phone = fields.Char('Phone', related='jalur_line_id.phone', store=True)
    #cust_mobile = fields.Char('Mobile', related='jalur_line_id.mobile', store=True)
    #cust_email = fields.Char('Email', related='jalur_line_id.email', store=True)
    #cust_type = fields.Selection('Type', related="jalur_line_id.customer_type", store=True )
    #cust_cluster = fields.Char('Cluster', related='jalur_line_id.cluster_id.name', store=True)
    #cust_ltime = fields.Float('Lead Time', related='jalur_line_id.customer_lead', store=True)

    #salesperson = fields.Char('Salesperson', related='jalur_id.salesperson_id.name', store=True)
    #group_name = fields.Char('Partner Group', related='jalur_id.group_id.name', store=True)
    #group_delivery = fields.Float('Delivery', related='jalur_id.group_id.delivery_days', store=True)
    #divisi_name = fields.Char('Partner Division', related='jalur_id.divisi_id.name', store=True)

    def name_get(self):
        result = []
        for record in self:
            if record.jalur_id:
                display_name = record.jalur_line_id.name+' / '+record.jalur_id.name+' / '+dict(self._fields['jwk'].selection).get(self.jwk)
            else:
                display_name = record.jalur_line_id.name+' / '+record.jalur_id.name
            result.append((record.id, display_name))
        return result

    @api.onchange('jalur_id')
    @api.depends('jalur_id')
    def _jalur(self):
        res = {}
        res['domain'] = {'jalur_id': [('divisi2_id', '=', self.jalur_line_id.divisi2_id.id)]}
        print("res=>", res)
        return res


class ResPartnerRegion(models.Model):
    _name = "res.partner.region"
    _description = "Partner Region"
    _order = 'code, name, id'
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
        ('name_uniq', 'unique (name)', 'The name must be unique !')
    ]

    code = fields.Char('Code', required=True, index=True)
    name = fields.Char('Name', required=True, index=True)

    def name_get(self):
        result = []
        for record in self:
            if record.code:
                display_name = '[' + record.code + '] ' + record.name
            else:
                display_name = record.name
            result.append((record.id, display_name))
        return result

class ResPartnerCluster(models.Model):
    _name = "res.partner.cluster"
    _description = "Partner Cluster"
    _order = 'code, name, id'
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
        ('name_uniq', 'unique (name)', 'The name must be unique !')
    ]

    code = fields.Char('Code', required=True, index=True)
    name = fields.Char('Name', required=True, index=True)

    def name_get(self):
        result = []
        for record in self:
            if record.code:
                display_name = '[' + record.code + '] ' + record.name
            else:
                display_name = record.name
            result.append((record.id, display_name))
        return result

class ResPartnerKategori1(models.Model):
    _name = "res.partner.kategori1"
    _description = "Partner Kategori 1"
    _order = 'code, name, id'
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
        ('name_uniq', 'unique (name)', 'The name must be unique !')
    ]

    code = fields.Char('Code', required=True, index=True)
    name = fields.Char('Name', required=True, index=True)

    def name_get(self):
        result = []
        for record in self:
            if record.code:
                display_name = '[' + record.code + '] ' + record.name
            else:
                display_name = record.name
            result.append((record.id, display_name))
        return result

class ResPartnerKategori2(models.Model):
    _name = "res.partner.kategori2"
    _description = "Partner Kategori 2"
    _order = 'code, name, id'
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
        ('name_uniq', 'unique (name)', 'The name must be unique !')
    ]

    code = fields.Char('Code', required=True, index=True)
    name = fields.Char('Name', required=True, index=True)
    kategori1_id = fields.Many2one("res.partner.kategori1", "Kategori 1")

    def name_get(self):
        result = []
        for record in self:
            if record.code:
                display_name = '[' + record.code + '] ' + record.name
            else:
                display_name = record.name
            result.append((record.id, display_name))
        return result

class ResPartnerKategori3(models.Model):
    _name = "res.partner.kategori3"
    _description = "Partner Kategori 3"
    _order = 'code, name, id'
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
        ('name_uniq', 'unique (name)', 'The name must be unique !')
    ]

    code = fields.Char('Code', required=True, index=True)
    name = fields.Char('Name', required=True, index=True)
    kategori2_id = fields.Many2one("res.partner.kategori2", "Kategori 2")

    def name_get(self):
        result = []
        for record in self:
            if record.code:
                display_name = '[' + record.code + '] ' + record.name
            else:
                display_name = record.name
            result.append((record.id, display_name))
        return result

class ResPartnerKategori4(models.Model):
    _name = "res.partner.kategori4"
    _description = "Partner Kategori 4"
    _order = 'code, name, id'
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
        ('name_uniq', 'unique (name)', 'The name must be unique !')
    ]

    code = fields.Char('Code', required=True, index=True)
    name = fields.Char('Name', required=True, index=True)
    kategori3_id = fields.Many2one("res.partner.kategori3", "Kategori 3")

    def name_get(self):
        result = []
        for record in self:
            if record.code:
                display_name = '[' + record.code + '] ' + record.name
            else:
                display_name = record.name
            result.append((record.id, display_name))
        return result

class ResPartnerDivisi1(models.Model):
    _name = "res.partner.divisi1"
    _description = "Partner Divisi 1"
    _order = 'code, name, id'
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
        ('name_uniq', 'unique (name)', 'The name must be unique !')
    ]

    code = fields.Char('Code', required=True, index=True)
    name = fields.Char('Name', required=True, index=True)

    def name_get(self):
        result = []
        for record in self:
            if record.code:
                display_name = '[' + record.code + '] ' + record.name
            else:
                display_name = record.name
            result.append((record.id, display_name))
        return result

class ResPartnerDivisi2(models.Model):
    _name = "res.partner.divisi2"
    _description = "Partner Divisi 2"
    _order = 'code, name, id'
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
        ('name_uniq', 'unique (name)', 'The name must be unique !')
    ]

    code = fields.Char('Code', required=True, index=True)
    name = fields.Char('Name', required=True, index=True)
    divisi1_id = fields.Many2one("res.partner.divisi1", "Divisi 1")
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")

    def name_get(self):
        result = []
        for record in self:
            if record.code:
                display_name = '[' + record.code + '] ' + record.name
            else:
                display_name = record.name
            result.append((record.id, display_name))
        return result

class ResPartnerDc1(models.Model):
    _name = "res.partner.dc1"
    _description = "Partner DC 1"
    _order = 'code, name, id'
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
        ('name_uniq', 'unique (name)', 'The name must be unique !')
    ]

    code = fields.Char('Code', required=True, index=True)
    name = fields.Char('Name', required=True, index=True)

    def name_get(self):
        result = []
        for record in self:
            if record.code:
                display_name = '[' + record.code + '] ' + record.name
            else:
                display_name = record.name
            result.append((record.id, display_name))
        return result

class ResPartnerKelompok(models.Model):
    _name = "res.partner.kelompok"
    _description = "Partner Kelompok"
    _order = 'code, name, id'
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
        ('name_uniq', 'unique (name)', 'The name must be unique !')
    ]

    code = fields.Char('Code', required=True, index=True)
    name = fields.Char('Name', required=True, index=True)

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_sales = fields.Boolean("Sales", )
    is_spv = fields.Boolean("Supervisor", )
    is_sopir = fields.Boolean("Sopir", )
    is_kenek = fields.Boolean("Kenek", )
    region_id = fields.Many2one("res.partner.region", "Region")
    cluster_id = fields.Many2one("res.partner.cluster", "Cluster")
    kategori1_id = fields.Many2one("res.partner.kategori1", "Kategori 1")
    kategori2_id = fields.Many2one("res.partner.kategori2", "Kategori 2")
    kategori3_id = fields.Many2one("res.partner.kategori3", "Kategori 3")
    kategori4_id = fields.Many2one("res.partner.kategori4", "Kategori 4")
    divisi1_id = fields.Many2one("res.partner.divisi1", "Divisi 1")
    divisi2_id = fields.Many2one("res.partner.divisi2", "Divisi 2")
    dc1_id = fields.Many2one("res.partner.dc1", "DC 1")
    kelompok_id = fields.Many2one("res.partner.kelompok", "Kelompok")
    jalur_id = fields.One2many('res.partner.jalur.line', 'jalur_line_id', string='Jalur Lines', track_visibility='onchange')
    jalur_sales = fields.One2many('res.partner.jalur.line', 'jalur_line_id', string='Jalur Lines', track_visibility='onchange')

    @api.onchange('kategori1_id')
    @api.depends('kategori1_id')
    def _kategori1_id(self):
        res = {}
        res['domain'] = {'kategori2_id': [('kategori1_id', '=', self.kategori1_id.id)]}
        return res

    @api.onchange('kategori2_id')
    @api.depends('kategori2_id')
    def _kategori2_id(self):
        res = {}
        res['domain'] = {'kategori3_id': [('kategori2_id', '=', self.kategori2_id.id)]}
        return res

    @api.onchange('kategori3_id')
    @api.depends('kategori3_id')
    def _kategori3_id(self):
        res = {}
        res['domain'] = {'kategori4_id': [('kategori3_id', '=', self.kategori3_id.id)]}
        return res

    @api.onchange('divisi1_id')
    @api.depends('divisi1_id')
    def _divisi(self):
        res = {}
        res['domain'] = {'divisi2_id': [('divisi1_id', '=', self.divisi1_id.id)]}
        return res
