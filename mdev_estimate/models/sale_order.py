
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    custom_city = fields.Char(string="City")
    custom_cluster_id = fields.Many2one('res.partner.cluster', string="Cluster" )
    custom_jalur_jwk = fields.Char(string="JWK")

    @api.model
    def create(self, values):
        res = super(SaleOrder, self).create(values)

        for order in self:
            res['custom_city'] = order.custom_city or False
            res['custom_cluster_id'] = order.custom_cluster_id.id or False
            #djoyo 200812
            res['custom_div_id'] = order.custom_div_id.id or False
            res['custom_group_id'] = order.custom_group_id.id or False
            res['custom_jalur_id'] = order.custom_jalur_id.id or False
            res['custom_jalur_jwk'] = order.custom_jalur_jwk or False

            #_logger.info("Estimate SaleOrder: Create ==> %s " % (res))

        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        if self.partner_id:
            values = {
                'custom_city': self.partner_id.city or False,
                'custom_cluster_id': self.partner_id.cluster_id.id or False,
                #djoyo 200812
                'custom_div_id': self.partner_id.custom_div_id.id or False,
                'custom_group_id': self.partner_id.custom_group_id.id or False,
                'custom_jalur_id': self.partner_id.custom_jalur_id.id or False,
            }
            #_logger.info("Estimate SaleOrder: OnChange ==> %s " % (values))

            self.update(values)
            return res

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({'custom_city': self.custom_city})
        res.update({'custom_cluster_id': self.custom_cluster_id.id})
        #djoyo 200812
        res.update({'custom_div_id': self.custom_div_id.id})
        res.update({'custom_group_id': self.custom_group_id.id})
        res.update({'custom_jalur_id': self.custom_jalur_id.id})
        res.update({'custom_jalur_jwk': self.custom_jalur_jwk})

        #_logger.info("Estimate SaleOrder: Prepare Invoice ==> %s " % (res))

        return res

    def action_confirm(self):
        
        #update 200729
        #res = super(SaleOrder, self).action_confirm()

        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            #update 200729
            #'date_order': fields.Datetime.now()
        })
        self._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()


        for rec in self:
            for pick_rec in rec.picking_ids:
                pick_rec.write({
                                'custom_city': self.custom_city or False,
                                'custom_cluster_id': self.custom_cluster_id.id or False,
                                'custom_div_id': self.custom_div_id.id or False,
                                'custom_group_id': self.custom_group_id.id or False,
                                'custom_jalur_id': self.custom_jalur_id.id or False,
                                'custom_jalur_jwk': self.custom_jalur_jwk or False,
                                })
                #_logger.info("Estimate SaleOrder: Action Confirm ==> %s " % (res))

        return True