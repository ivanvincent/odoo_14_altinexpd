from odoo import api, fields, models, _

invoice_ids_global = []
import ast

class efaktur(models.Model):
    _name = 'vit.efaktur'    

    invoice_ids_global = []


    name = fields.Char("eFaktur Number")
    year = fields.Integer(string="Year", required=False, )
    
    # invoice_ids = fields.One2many(comodel_name="account.move",
    #                               inverse_name="efaktur_id",
    #                               string="Invoices", required=False, )
    invoice_ids = fields.Many2many(comodel_name="account.move", string="Invoices", domain=[('state', '=', 'posted')])
    is_update_context = fields.Boolean(string="bool", compute="_compute_is_update")

    amount_dpp = fields.Float(
        string='Total DPP',
        store=True,
        compute="_compute_amount_invoices"
    )
    amount_ppn = fields.Float(
        string='Total PPN',
        store=True,
        compute="_compute_amount_invoices"
    )
    state = fields.Selection(
        string='State',
        default='draft',
        selection=[('draft', 'Draft'), ('validate', 'Validate'), ('done', 'Done'), ('cancel', 'Cancel')]
    )

    ids_temporary = fields.Char(string='Ids Temporary', compute="_compute_ids_temporary")

    @api.depends('invoice_ids')
    def _used(self):
        for efaktur in self:
            if efaktur.invoice_ids:
                efaktur.is_used = True
            else:
                efaktur.is_used = False

    @api.depends('invoice_ids')
    def _compute_amount_invoices(self):
        for rec in self:
            print("================")
            print(rec.invoice_ids.mapped('amount_untaxed'))
            rec.amount_dpp = sum(rec.invoice_ids.mapped('amount_untaxed'))
            rec.amount_ppn = sum(rec.invoice_ids.mapped('amount_tax'))

    is_used = fields.Boolean(string="Is Used", compute="_used", store=True )

    def action_efaktur_validate(self):
        if not self.invoice_ids:
            raise ValidationError('Invoice belum di isi')
        for invoice in self.invoice_ids:
            invoice.efaktur_masukan = self.name
        self.state = 'validate'

    def action_efaktur_done(self):
        # for invoice in self.invoice_ids:
        #     invoice.efaktur_id = self.id
        self.state = 'done'

    def action_efaktur_cancel(self):
        for invoice in self.invoice_ids:
            invoice.efaktur_masukan = ''
        self.state = 'cancel'

    def action_efaktur_draft(self):
        self.state = 'draft'

    # def write(self, val):
    #     res = super(efaktur, self).write(val)
    #     parameterObj = self.env['ir.config_parameter']
    #     inv_ids_a = ast.literal_eval(parameterObj.get_param('invoice_ids_temporary'))
    #     inv_ids = val.get('invoice_ids')
    #     if inv_ids and inv_ids[0][0] == 6:
    #         inv_ids_b = inv_ids[0][2]
    #         idsDeleted = list(set(inv_ids_a) - set(inv_ids_b))
    #         moveObj = self.env['account.move'].search([('id','in', inv_ids[0][2]) , ('efaktur_id','!=', self.id)])
    #         for a in moveObj:
    #             a.write({'efaktur_id':self.id})
    #         if len(idsDeleted) > 0:
    #             for b in idsDeleted:
    #                 self.env['account.move'].browse(b).write({'efaktur_id':False})
    #     return res

    def _compute_ids_temporary(self):
        parameterObj = self.env['ir.config_parameter']
        if parameterObj.get_param('invoice_ids_temporary'):
            parameterObj.set_param('invoice_ids_temporary', str(self.invoice_ids.ids))
        else:
            parameterObj.set_param('invoice_ids_temporary', '[]')
        self.ids_temporary = False


class AccountTax(models.Model):
    _inherit = 'account.tax'

    is_efaktur = fields.Boolean(
        string='Included in Efaktur',
    )

    tax_type = fields.Selection(
        string='Tax Type',
        default='ppn',
        selection=[('ppn', 'PPN'), ('pph', 'PPH')]
    )