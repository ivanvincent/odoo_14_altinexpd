from odoo import models, fields, api

class PurchaseOrderOffer(models.Model):
    _name = 'purchase.order.offer'

    partner_id = fields.Many2one('res.partner', string='Vendor')
    purchase_id = fields.Many2one('purchase.order', string='Purchase')
    image = fields.Binary(string='Image', store=False,)

    def action_set(self):
        if self.partner_id:
            self.purchase_id.partner_id = self.partner_id.id