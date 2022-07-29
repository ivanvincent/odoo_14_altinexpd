from odoo import fields, models, api, _
from odoo.exceptions import UserError

class SetKontrabonWizard(models.TransientModel):
    _name = 'set.kontrabon.wizard'
    

    kontrabon_id = fields.Many2one('kontrabon.order', string='Kontrabon',domain=[('state', 'in', ('draft','confirm'))])
    invoice_ids  = fields.Many2many(comodel_name='account.move', relation='account_move_kontrabon_wizard_rel', string='Invoice',domain=[('kontrabon_id', '=', False)])
    
    
    @api.model
    def default_get(self,fields):
        res = super(SetKontrabonWizard,self).default_get(fields)
        active_ids = self._context.get('active_ids')
        move_ids = self.env['account.move'].browse(active_ids)
        if move_ids:
            same_partner = all(move.partner_id == move_ids[0].partner_id for move in move_ids)
            if not same_partner:
                raise UserError('Pastikan memilih vendor yang mana')
            elif move_ids.filtered(lambda m: m.kontrabon_id):
                raise UserError('Pastikan memilih vendor yang belum di set kontrabon')
            else:
                res['invoice_ids'] = [(6,0,move_ids.ids)]
        return res
    

    def process(self):
        if self.kontrabon_id:
            kontra = self.kontrabon_id
            if self.kontrabon_id.partner_id.id == self.invoice_ids.mapped('partner_id')[0].id if self.invoice_ids.mapped('partner_id') else False:
                for move in self.invoice_ids:
                    move.write({'kontrabon_id' : kontra.id})
                inv_ids_old = [inv.id for inv in kontra.inv_ids]
                kontra.write({
                    'inv_ids': [(6, 0, inv_ids_old + self.invoice_ids.ids)]
                })
                action = self.env.ref('tj_kontrabon.action_kontrabon_order_list').read()[0]
                action['domain'] = [('id','=',self.kontrabon_id.id)]
                action['context'] = {}
                return action
                    
            else:
                raise UserError('Mohon maaf partner tidak sama dengan kontrabon yg akan di update')
        else:
            kontrabon_id = self.env['kontrabon.order'].create({
                "type_kontra": "in_invoice",
                "tanggal":fields.Date.today(),
                "partner_id":self.invoice_ids.mapped('partner_id')[0].id if self.invoice_ids.mapped('partner_id') else False,
                "inv_ids": [(6,0,self.invoice_ids.ids)]
            })
            
            for move in self.invoice_ids:
                move.write({'kontrabon_id' : kontrabon_id.id})
                
            action = self.env.ref('tj_kontrabon.action_kontrabon_order_list').read()[0]
            action['domain'] = [('id','=',kontrabon_id.id)]
            action['context'] = {}
            return action
                
                