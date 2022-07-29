from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
import requests
import logging
_logger = logging.getLogger(__name__)
import pytz
from pytz import timezone
from dateutil.relativedelta import relativedelta
import xlrd
from odoo.exceptions import Warning

class Partner(models.Model):
	_inherit = 'res.partner'

	customer_type = fields.Selection([('mt','MT'),('gt','GT'),('po','PO'),('ro','RO'),('to','TO')], default="mt", string="Customer Type")
	estimate_tmpl = fields.Selection([	('alfamart','ALFAMART'),
										('indomaret','INDOMARET'),
										('lainnya','LAINNYA'),
										], default="lainnya", string="Estimate Template" )


class PartnerProduct(models.Model):
    _name = 'res.partner.product'
    _description = 'Partners Product'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]

    name = fields.Char(readonly="1")

    customer_id = fields.Many2one('res.partner', required=True, string="Customer", track_visibility="onchange" )
    cust_int_code = fields.Char('Int. Code', related="customer_id.kode_customer", store=True )
    cust_ext_code = fields.Char('Ext. Code', related="customer_id.kext_customer", store=True )
    cust_address = fields.Char('Address', related="customer_id.street", store=True )
    cust_city = fields.Char('City', related="customer_id.city", store=True )
    cust_cluster = fields.Char('Cluster', related="customer_id.cluster_id.name", store=True )
    cust_type = fields.Selection('Type', related="customer_id.customer_type", store=True )
    cust_ltime = fields.Float('Lead Time', related='customer_id.customer_lead', store=True )

    cust_acc = fields.Selection('Account', related="customer_id.custom_acc_id", store=True )
    cust_div = fields.Many2one(comodel_name='res.partner.divisi', related='customer_id.custom_div_id', store=True)
    cust_group = fields.Many2one(comodel_name='res.partner.group', related='customer_id.custom_group_id', store=True)
    group_delivery = fields.Float('Delivery', related='customer_id.custom_group_id.delivery_days', store=True )

    product_id = fields.Many2one('product.product', required=True, string="Product", track_visibility="onchange" )
    prod_categ = fields.Char('Category', related="product_id.categ_id.name", store=True )
    prod_int_code = fields.Char('Int. Code', related="product_id.default_code", store=True )
    prod_uom_code = fields.Char('Default UoM', related="product_id.uom_id.name", store=True )

    ext_code = fields.Char(string="Ext. Code", track_visibility="onchange" )

    schedule = fields.Selection([	('0','Default'),
                                    ('1','Senin'),
                                    ('2','Selasa'),
                                    ('3','Rabu'),
                                    ('4','Kamis'),
                                    ('5','Jumat'),
                                    ('6','Sabtu'),
                                    ('7','Minggu')
                                ], default='0', string="Schedule" )

    product_active = fields.Boolean("Active", default="true", track_visibility="onchange" )

    quantity = fields.Float(string="Quantity", track_visibility="onchange" )

    is_ord_qty = fields.Boolean("Is Default Order", default="true" )
    ord_qty = fields.Float(string="Default Qty.", track_visibility="onchange" )

    is_min_qty = fields.Boolean("Is Minimum Order", default="true", track_visibility="onchange" )
    min_qty = fields.Float(string="Minimum Qty.", track_visibility="onchange" )

    is_max_qty = fields.Boolean("Is Maximum Order", default="true", track_visibility="onchange" )
    max_qty = fields.Float(string="Maximum Qty.", track_visibility="onchange" )

    remark = fields.Text(string="Remark")

    def name_get(self):
        result = []
        for record in self:
            if record.customer_id:
                if record.product_id:
                    display_name = record.customer_id.name + ' / ' + record.product_id.name
                else:
                    display_name = record.customer_id.name
            else:
                display_name = ""
            result.append((record.id, display_name))
        return result


class ResPartnerJalurLine(models.Model):
    _inherit = "res.partner.jalur.line"
    _description = "Customer Grouping"

    cust_int_code = fields.Char('Int.Code', related='jalur_line_id.kode_customer', store=True)
    cust_ext_code = fields.Char('Ext.Code', related='jalur_line_id.kext_customer', store=True)
    cust_city = fields.Char('City', related='jalur_line_id.city', store=True)
    cust_phone = fields.Char('Phone', related='jalur_line_id.phone', store=True)
    cust_mobile = fields.Char('Mobile', related='jalur_line_id.mobile', store=True)
    cust_email = fields.Char('Email', related='jalur_line_id.email', store=True)
    cust_type = fields.Selection('Type', related="jalur_line_id.customer_type", store=True )
    cust_cluster = fields.Char('Cluster', related='jalur_line_id.cluster_id.name', store=True)
    cust_ltime = fields.Float('Cust. Delivery', related='jalur_line_id.customer_lead', store=True)

    account_id = fields.Selection('Account', related="jalur_line_id.custom_acc_id", store=True )

    divisi_id = fields.Many2one(comodel_name='res.partner.divisi', related='jalur_line_id.custom_div_id', store=True)

    group_id = fields.Many2one(comodel_name='res.partner.group', related='jalur_line_id.custom_group_id', store=True)
    group_delivery = fields.Float('Group Delivery', comodel_name='res.partner.group', related='jalur_line_id.custom_group_id.delivery_days', store=True)

    salesperson = fields.Char('Salesperson', related='jalur_id.salesperson_id.name', store=True)
