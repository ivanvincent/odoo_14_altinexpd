from odoo import fields, models, api, _
from odoo.exceptions import UserError

class ReimburseWizard(models.TransientModel):

    _name = 'reimburse.wizard'
    
    
    ajuan_id        = fields.Many2one('uudp', string='Pengajuan',domain=[('type', '=', 'pengajuan')])
    penyelesaian_id = fields.Many2one('uudp', string='Penyelesaian',domain=[('type', '=', 'penyelesaian')])
    lebih_bayar     = fields.Float(string='Lebih Bayar')
    cara_bayar      = fields.Selection([("cash","Cash"),("transfer","Transfer")], string='Cara Bayar',default="cash")
    journal_id      = fields.Many2one("account.journal", string="Journal", track_visibility='onchange',domain=lambda self: self._filter_journal())# default=_default_journal)
    line_ids        = fields.One2many('reimburse.line.wizard', 'wizard_id', string='Details')
    
    
    @api.model
    def default_get(self,fields):
        res = super(ReimburseWizard,self).default_get(fields)
        context = self._context
        if context.get('default_penyelesaian_id'):
            ajuan_id = self.env['uudp'].browse(context.get('default_penyelesaian_id'))
            if ajuan_id.uudp_ids:
                res['line_ids'] = [
                (0,0,{"product_id":line.product_id.id,
                      "account_id":line.coa_debit.id,
                      "total":  line.sub_total - sum(line.uudp_id.ajuan_id.uudp_ids.filtered(
                        lambda x:x.template_id.id == line.template_id.id
                        and x.product_id.id == line.product_id.id 
                        and x.coa_debit == line.coa_debit).mapped('sub_total')),
                      "description":line.description
                        }) for line in ajuan_id.uudp_ids.filtered(lambda x:x.is_different)]
        return res
    
    
    
    def _filter_journal(self):
        domain = []
        if self.ajuan_id and self.cara_bayar:
            if self.cara_bayar == 'cash':
                domain += [('type','=','cash')]
            else:
                domain += [('type','=','bank')]
        return domain

    def action_create_reimburse(self):
        if not self.penyelesaian_id.reimburse_id:
            if not self.line_ids:
                raise UserError('Mohon maaf biaya / product harus di isi')
            reimburse_id = self.env['uudp'].create({
                'type':'reimberse',
                'employee_id':self.ajuan_id.employee_id.id,
                'department_id':self.ajuan_id.department_id.id,
                'cara_bayar':self.cara_bayar,
                'journal_id':self.journal_id.id,
                'date': fields.Date.today(),
                'end_date': fields.Date.today(),
                'uudp_ids':[(0,0,{'product_id':line.product_id.id,  'qty':1,'description':line.description,'coa_debit':line.account_id.id,'unit_price':line.total}) for line in self.line_ids]
            })
            
            if reimburse_id:
                self.penyelesaian_id.write({'reimburse_id':reimburse_id.id})
                self.penyelesaian_id.write_state_line('confirm')
                self.penyelesaian_id.write({'state':'confirm'})
                
                

class ReimburseLineWizard(models.TransientModel):

    _name = 'reimburse.line.wizard'
    
    
    wizard_id   = fields.Many2one('reimburse.wizard', string='Wizard')
    product_id  = fields.Many2one("product.product", string="Product", track_visibility='onchange',domain=[('can_be_expensed', '=', True)])
    description = fields.Char(string="Description", required=True, track_visibility='onchange',)
    total       = fields.Float(string='Total')
    account_id  = fields.Many2one('account.account', string="Account", track_visibility='onchange')
    