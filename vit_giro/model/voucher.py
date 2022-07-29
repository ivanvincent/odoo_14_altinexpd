import time
import logging

from collections import namedtuple
import json
import time

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
# from odoo.addons.procurement.models import procurement
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp

from odoo import netsvc


_logger = logging.getLogger(__name__)

####################################################################################
# periodic read dari ca_pembayaran
# if exists create payment voucher for the invoice
####################################################################################


class AccountVoucher(models.Model):
    _inherit = "account.voucher"
    
    ####################################################################################
    # create payment
    # invoice_id: yang mau dibayar
    # journal_id: payment method
    ####################################################################################
    @api.model
    def create_payment(self, inv, partner_id, amount, journal, type, name, company_id):
        voucher_lines = []
        
        # cari move_line yang move_id nya = invoice.move_id
        move_lines = self.env['account.move.line'].search([('move_id.id', '=', inv.move_id.id)])
        move_line = move_lines[0]  # yang AR saja
        
        #payment supplier
        if type == 'payment':
            line_amount = amount
            line_type = 'dr'
            journal_account = journal.default_credit_account_id.id
        #receive customer
        else:
            line_amount = amount
            line_type = 'cr'
            journal_account = journal.default_debit_account_id.id
            
        
        voucher_lines.append((0, 0, {
            'move_line_id': move_line.id,
            'account_id': move_line.account_id.id,
            'quantity': 1,
            # 'amount_unreconciled': line_amount,
            'reconcile': True,
            'price_unit': line_amount,
            # 'type': line_type,
            'name': move_line.name,
            'company_id': company_id
        }))
        
        voucher_id = self.env['account.voucher'].create({
            'partner_id' : partner_id,
            'amount' 		: amount,
            'account_id'	: journal_account,
            'journal_id'	: journal.id,
            'reference' 	: 'Payment giro ' + name,
            'name' 			: 'Payment giro ' + name,
            'company_id' 	: company_id,
            'voucher_type'	: type,
            'line_ids'		: voucher_lines
        })
        _logger.info("   created payment id:%d" % (voucher_id) )
        return voucher_id
    
    ####################################################################################
    # set done
    ####################################################################################
    @api.model
    def payment_confirm(self, vid):
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate('account.voucher', vid, 'proforma_voucher')
        _logger.info("   confirmed payment id:%d" % (vid) )
        return True
    
    
    ####################################################################################
    # find invoice by number
    ####################################################################################
    def find_invoice_by_number(self, number):
        invoice_obj = self.env['account.move']
        invoice = invoice_obj.search([('number' ,'=', number)])
        return invoice
    
    ####################################################################################
    # find journal by code
    ####################################################################################
    def find_journal_by_code(self, code):
        journal_obj = self.env['account.journal']
        journal = journal_obj.search([('code', '=', code)])
        return journal