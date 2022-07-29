from odoo import fields, models, api, _
from odoo.exceptions import UserError

class UpdateAddressWizard(models.TransientModel):
    _name = 'update.address.wizard'

    partner_address_id = fields.Many2one('partner.address', string='Alamat', required=True, )

    @api.onchange('partner_address_id')
    def _onchange_partner_address_id(self):
        res = {}
        ctx = self.env.context
        res['domain'] = {'partner_address_id': [('partner_id', '=', ctx.get('partner_id'))]}
        return res

    def action_update_address(self):
        print('action_update_address')
        ctx = self.env.context
        self.env['account.move'].browse(ctx.get('move_id')).write({'partner_address_id': self.partner_address_id.id})

    def acton_reset_address(self):
        ctx = self.env.context
        self.env['account.move'].browse(ctx.get('move_id')).write({'partner_address_id': False})
