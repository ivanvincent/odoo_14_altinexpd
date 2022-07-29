from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
import requests
import logging
_logger = logging.getLogger(__name__)
import pytz
from pytz import timezone
from dateutil.relativedelta import relativedelta
import datetime
from datetime import datetime, timedelta

from odoo.exceptions import Warning

class Estimate(models.Model):
    _name = 'estimate'
    _description = 'Estimate'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]
    _order = 'estimate_date DESC, id DESC'

    STATE = [('draft','Draft'),
             ('confirm','Confirm'),
             ('done','Done'),
             ('cancel','Cancelled')]


    @api.onchange("product_qty","price")
    def onchange_product_qty(self):
        if self.product_qty and self.product_qty:
            self.subtotal = self.product_qty*self.product_qty
        else:
            self.subtotal = 0

    state = fields.Selection(STATE, string="State", default="draft", track_visibility="onchange" )
    sequence = fields.Integer(string="Seq")
    user_id = fields.Many2one('res.users', string="Estimator", default=lambda self: self.env.uid )

    name = fields.Char(readonly="1")
    template = fields.Char(readonly="1")

    estimate_type = fields.Selection([('mt','MT'),('gt','GT'),('ro','RO'),('po','PO'),('to','TO')], string="Type")
    estimate_date = fields.Date(string="Estimate Date", default=fields.Date.today())
    commitment_date = fields.Date(string="Delivery Date")

    customer_id = fields.Many2one('res.partner', string="Customer")
    cust_int_cd = fields.Char(string="Cust. Int")
    cust_ext_cd = fields.Char(string="Cust. Ext")
    address = fields.Char(string="Address")
    city = fields.Char(string="City")

    account_id = fields.Selection([ ('indomaret','Indomaret'),
									('alfagroup','Alfa Group'),
									('lainnya','Lainnya')
                                ], string="Account")
    divisi_id = fields.Many2one('res.partner.divisi', string="Division" )
    group_id = fields.Many2one('res.partner.group', string="Group" )
    route_id = fields.Many2one('res.partner.jalur', string="Route" )
    route_jwk = fields.Char(string="JWK")
    cluster_id = fields.Many2one('res.partner.cluster', string="Cluster" )

    product_id = fields.Many2one('product.product', string="Product")
    prod_int_cd = fields.Char(string="Prod. Int")
    prod_ext_cd = fields.Char(string="Prod. Ext")

    sellingout_qty = fields.Float(string="Sellingout")
    sellingout_stock = fields.Float(string="Stock")
    sellingout_pkm = fields.Float(string="PKM")

    history_w01 = fields.Float(string="Hist_W01")
    history_w02 = fields.Float(string="Hist_W02")
    history_w03 = fields.Float(string="Hist_W03")
    history_w04 = fields.Float(string="Hist_W04")

    last_order_qty = fields.Float(string="Last Order")
    history_qty = fields.Float(string="History")
    product_qty = fields.Float(string="Quantity", track_visibility="onchange")
    revised_qty = fields.Float(string="Revised", track_visibility="onchange")
    product_uom_id = fields.Many2one('uom.uom', string="UoM")
    price = fields.Float(string="Price")
    taxes = fields.Float(string="Taxes")
    discount = fields.Float(string="Discount")
    subtotal = fields.Float(string="Subtotal")

    remark = fields.Text(string="Remark")


    so_created = fields.Boolean(string="SO Created", default=False)
    so_number = fields.Many2one('sale.order', string="SO Reff")
    so_date = fields.Datetime('SO Date', related='so_number.date_order', store=True)
    so_pricelist = fields.Many2one('product.pricelist', related='so_number.pricelist_id', store=True)

    order_qty = fields.Float(string="Qty. Ordered")
    deliver_qty = fields.Float(string="Qty. Delivered")
    return_qty = fields.Float(string="Qty. Return")

    def get_sequence(self):
        pref = '%(y)s/EST/%(month)s/'
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', 'Estimate Data'),
            ('code', '=', 'estimate'),
            ('prefix', '=', pref),
        ], limit=1)
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': 'Estimate Data',
                'code': 'estimate',
                'implementation': 'standard',
                'prefix': pref,
                'padding': 6,
            })
        return sequence_id.next_by_id() 

    @api.model
    def create(self, vals):
        vals['name'] = self.get_sequence()
        return super(Estimate, self).create(vals)

    def unlink(self):
        for obj in self:
            if obj.state != 'draft':
                raise Warning('Delete not allowed !')
        return super(Estimate, self).unlink()

    def action_confirm(self):
        for me in self:
            me.write({
                'state': 'confirm'
            })

    def action_validate(self):
        for me in self:

            #partner = self.env['res.partner'].search([('id','=',me.customer_id.id)])
            #if partner:
            #    partner.write(  {'custom_jalur_id': me.route_id.id} )

            so_line_vals = []

            so_line_vals.append((0,0,{
                'type': me.estimate_type,
                'route_id': me.route_id.id,
                'product_id': me.product_id.id,
                'product_uom_qty': me.product_qty,
                'product_uom': me.product_id.uom_id.id
            }))
            if so_line_vals:

                vdate_order      = datetime.strptime(me.estimate_date.strftime('%Y-%m-%d')+' 08:00:00', '%Y-%m-%d %H:%M:%S') -timedelta(hours=7)
                vcommitment_date = datetime.strptime(me.commitment_date.strftime('%Y-%m-%d')+' 08:00:00', '%Y-%m-%d %H:%M:%S') -timedelta(hours=7)

                vals = {
                        'date_order': vdate_order,
                        'commitment_date': vcommitment_date,
                        'partner_id': me.customer_id.id,
                        'custom_city': me.customer_id.city,
                        'custom_cluster_id': me.customer_id.cluster_id.id,
                        'custom_div_id': me.divisi_id.id,
                        'custom_group_id': me.group_id.id,
                        'custom_jalur_id': me.route_id.id,
                        'custom_jalur_jwk': me.route_jwk,
                        'order_line': so_line_vals
                }
                _logger.info("SO Vals ==> %s" % (vals))

                so_id = self.env['sale.order'].create(vals)
                so_id.sudo().action_confirm()

                me.write({
                    'so_number': so_id.id,
                    'state': 'done'
                })

    def action_todraft(self):
        for me in self:
            me.write({
                'state': 'draft'
            })

    def action_cancel(self):
        for me in self:
            if me.so_number:

                so = self.env['sale.order'].search([('id','=',me.so_number.id)])
                if so:
                    for sp in so.picking_ids:
                        sp.action_cancel()

                    so.action_cancel()
                    for ol in so.order_line:
                        if ol.product_id == me.product_id:
                            ol.unlink()

                    if so.order_line:
                        so.action_draft()
                        so.action_confirm()

            me.write({
                'state': 'cancel'
            })

    
