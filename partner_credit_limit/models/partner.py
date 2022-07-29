# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import time
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_supplier              = fields.Boolean(string='Is Supplier',default=False)
    over_credit              = fields.Boolean('Allow Over Credit?')
    credit_check             = fields.Boolean('Active Credit', help='Activate the credit limit feature')
    credit_warning           = fields.Monetary('Warning Amount')
    credit_blocking          = fields.Monetary('Blocking Amount')
    amount_due               = fields.Monetary('Due Amount', compute='_compute_amount_due')
    total_overdue            = fields.Integer(string='Overdue',compute="_invoice_overdue",help="Number of invoices that are past due, the due date has passed")
    outstanding_receivable   = fields.Monetary(compute='_compute_sisa_limit', string='Outstanding Receiveable', store=False)
    outstanding_payable      = fields.Monetary(compute='_compute_sisa_limit', string='Outstanding Payable', store=False)
    outstanding_credit_limit = fields.Monetary(compute='_compute_sisa_limit', string='Remaining Limit', store=False)
    is_group_company         = fields.Boolean(string='Is Group company',default=False)
    is_over_limit            = fields.Boolean(compute='_compute_sisa_limit',string='Over Limit' ,store=True,)
    group_partner_id         = fields.Many2one('res.partner', string='Group Of Company')
    partner_group_ids        = fields.One2many('res.partner', 'group_partner_id', string='Members of Group', domain=[('active', '=', True)])
    status_customer          = fields.Selection([("piutang_lancar","Piutang Lancar"),("piutang_macet","Piutang Macet"),("piutang_grup_perusahaan","Piutang Grup Perusahaan")], string='Status Kelompok pelanggan', default="piutang_lancar")

    
    
    
    @api.depends('credit')  
    def _compute_sisa_limit(self):
        for partner in self:
        # for partner in self.filtered('id'):
            domain = [
                ('partner_id', '=', partner.id),
            ]
            partner.outstanding_credit_limit = partner.credit_limit - partner.credit
            partner.is_over_limit = partner.credit > partner.credit_limit
    
    
    
    def action_overdue_invoice(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("partner_credit_limit.action_overdue_invoice")
        action['domain'] = [
            ('partner_id', '=', self.id),
            ('invoice_date_due', '<', time.strftime('%Y-%m-%d')),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
        ]
        # action['context'] = {'default_move_type':'out_invoice', 'move_type':'out_invoice', 'journal_type': 'sale', 'search_default_unpaid': 1}
        return action
    
    def _invoice_overdue(self):
        for partner in self.filtered('id'):
            domain = [
                ('partner_id', '=', partner.id),
                ('invoice_date_due', '<', time.strftime('%Y-%m-%d')),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ('not_paid', 'partial')),
            ]
            
            overdue = self.env['account.move'].search_count(domain)
            partner.total_overdue = overdue

    @api.depends('credit', 'debit')
    def _compute_amount_due(self):
        for rec in self:
            rec.amount_due = rec.credit - rec.debit

    @api.constrains('credit_warning', 'credit_blocking')
    def _check_credit_amount(self):
        for credit in self:
            if credit.credit_warning > credit.credit_blocking:
                raise ValidationError(_('Warning amount should not be greater than blocking amount.'))
            if credit.credit_warning < 0 or credit.credit_blocking < 0:
                raise ValidationError(_('Warning amount or blocking amount should not be less than zero.'))


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    
    group_partner_id    = fields.Many2one('res.partner', string='Group Of Company', related='partner_id.group_partner_id', store=True,)    