from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError, AccessError, ValidationError
from . import terbilang


class uudpPencairan(models.Model):
    _name = 'uudp.pencairan'
    _order = 'name desc'
    _inherit = ['mail.thread']

    #########################
    #Fungsi message discuss #
    #########################

    def post_mesages_pencairan(self,state):
        ir_model_data_sudo = self.env['ir.model.data'].sudo()

        user_pencairan    = ir_model_data_sudo.get_object('vit_uudp', 'group_user_uudp_pencairan')
        manager_pencairan = ir_model_data_sudo.get_object('vit_uudp', 'group_manager_uudp_pencairan')

        user_pencairan_partner_ids     = user_pencairan.users.mapped('partner_id')
        manager_pencairan_partner_ids  = manager_pencairan.users.mapped('partner_id')

        user_pencairan_partners    =  map(lambda x:x['id'],user_pencairan_partner_ids)
        manager_pencairan_partners =  map(lambda x:x['id'],manager_pencairan_partner_ids)

        receivers = user_pencairan_partners + manager_pencairan_partners

        subject = _("UUDP Pencairan")
        body = 'UUDP Pencairan ' +str(state)
        messages = self.message_post(body=body, subject=subject)
        messages.update({'needaction_partner_ids' : [(6, 0, receivers)]})

        #kirim messages juga ke pengaju bahwa ajuan telah masuk ke tahap pencairan

        if self.type == 'once':
            for uudp in self.uudp_ids:

                subject = _("Pencairan")
                body = 'Pencairan ' +str(state)
                messages = uudp.message_post(body=body, subject=subject)
                messages.update({'needaction_partner_ids' : [(6, 0, [uudp.user_id.partner_id.id])]})

        else:
            subject = _("Pencairan")
            body = 'Pencairan ' +str(state)
            messages = self.ajuan_id.message_post(body=body, subject=subject)
            messages.update({'needaction_partner_ids' : [(6, 0, [self.ajuan_id.user_id.partner_id.id])]})

        return True


    name                   = fields.Char(string="Nomor Pencairan", readonly=True, default="New")
    tgl_pencairan          = fields.Date(string="Tanggal Pencairan", required=True, default=fields.Datetime.now, track_visibility='onchange',)
    user_id                = fields.Many2one("res.users", string="Kasir", default=lambda self: self.env.user)
    uudp_ids               = fields.Many2many("uudp", string="Detail Kasbon", track_visibility='onchange',)
    state                  = fields.Selection([('draft', 'Draft'),('confirm_once', 'Confirm'),('confirm_parsial', 'Confirm'),('posted', 'Posted'),('done', 'Done'),('cancel', 'Cancelled'),('refuse','Refused')], default='draft', required=True, index=True, track_visibility='onchange',)
    journal_id             = fields.Many2one("account.journal", string="Journal", required=True, track_visibility='onchange')
    coa_kredit             = fields.Many2one("account.account", string="Account", related="ajuan_id.coa_debit", help="Credit Account", track_visibility='onchange')
    journal_entry_id       = fields.Many2one("account.move", string="Journal Entry", track_visibility='onchange',)
    company_id             = fields.Many2one("res.company", string="Company", default=lambda self: self.env['res.company']._company_default_get())
    type                   = fields.Selection([('parsial', 'Parsial'), ('once', 'At Once'),],string='Type Pencairan', required=True)
    journal_entry_ids      = fields.One2many("account.move", string="Journal Entries", inverse_name="uudp_pencairan_id", track_visibility='onchange',)
    ajuan_id               = fields.Many2one('uudp', string="Ajuan", track_visibility='onchange',)
    cara_bayar             = fields.Selection('Cara Bayar',related="ajuan_id.cara_bayar")
    nominal_ajuan          = fields.Float(String="Nominal Ajuan", related="ajuan_id.total_ajuan")
    notes                  = fields.Text(string="Notes", track_visibility='onchange',)
    sisa_pencairan_parsial = fields.Float(string="Sisa Pencairan Parsial")
    total_pencairan        = fields.Float(string="Total Pencairan", compute="get_total_pencairan")
    bank_statement_id      = fields.Many2one('account.bank.statement', string='Bank Statement')
    category_id            = fields.Many2one('uudp.category', string='Category',related="ajuan_id.category_id")
    is_reconciled          = fields.Boolean(string='Reconciled')
    # entry_ids              = fields.One2many('account.move',  related='bank_statement_id.move_line_ids',string='Entry Lines')
    
    
    @api.onchange('ajuan_id')
    def _onchange_ajuan_id(self):
        if self.ajuan_id.state == 'confirm_finance':
            if self.ajuan_id.id not in self.uudp_ids.mapped('id'):
                self.uudp_ids = [(4,self.ajuan_id.id)]

    
    def button_reconcile(self):
        account_id = False
        if self.ajuan_id.type == 'pengajuan':
            account_id = self.ajuan_id.coa_debit.id
        elif self.ajuan_id.type == 'reimberse':
            penyelesaian_id = self.env['uudp'].sudo().search([('reimburse_id','=',self.ajuan_id.id)],limit=1)
            account_id  = penyelesaian_id.ajuan_id.coa_debit.id if penyelesaian_id else False
            if self.bank_statement_id.state == 'open':
                self.bank_statement_id.button_post()
            return {
                "type": "ir.actions.client",
                "tag": "bank_statement_reconciliation_view",
                "context": {
                    "is_uudp": True,
                    "is_reimburse":True,
                    "reimburse_id":self.ajuan_id.id,
                    "account_id": account_id if account_id else self.coa_kredit.id,
                    "coa_debit_ids": [{"account_id":{"id":line.coa_debit.id,"name":line.coa_debit.name,'uudp_id':line.uudp_id.id},"amount":-abs(line.sub_total)} for line in self.ajuan_id.uudp_ids],
                    "statement_line_ids": self.bank_statement_id.line_ids.ids,
                    "company_ids": self.bank_statement_id.mapped("company_id").ids,
                },
            }
            
        
        if self.bank_statement_id.state == 'open':
            self.bank_statement_id.sudo().write({'state':'posted'})
        
        if self.bank_statement_id.state == 'posted':
            return {
                "type": "ir.actions.client",
                "tag": "bank_statement_reconciliation_view",
                "context": {
                    "is_uudp": True,
                    "account_id": account_id,
                    "statement_line_ids": self.bank_statement_id.line_ids.ids,
                    "company_ids": self.bank_statement_id.mapped("company_id").ids,
                },
            }
			
    
    def button_journal_entries(self):
        entry_ids = []
        for move in self.bank_statement_id.line_ids.move_id:
            entry_ids.append(move.id)
            
        for move in self.journal_entry_ids:
            entry_ids.append(move.id)
            
        return {
            'name': _('Journal Entries'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', entry_ids)],
            'context': {
                'journal_id': self.bank_statement_id.journal_id.id,
            }
        }
        
    def _filter_journal(self):
        domain = []
        if self.ajuan_id and self.cara_bayar:
            if self.cara_bayar == 'cash':
                domain += [('type','=','cash')]
            else:
                domain += [('type','=','bank')]
        return domain
    
    @api.onchange('ajuan_id')
    def _onchange_journal(self):
        res = {}
        payment_type = 'bank' if self.cara_bayar == 'setor_tunai' else 'cash'
        res['domain'] = {'journal_id': [('type', '=', payment_type)]}
        return res
    
    def action_post_statement(self):
        if self.bank_statement_id and self.bank_statement_id.state == 'open':
            self.bank_statement_id.button_post()
            if self.bank_statement_id.state == 'posted':
                return {
						"type": "ir.actions.client",
						"tag": "bank_statement_reconciliation_view",
						"context": {
							"is_uudp": True,
							"pencairan_id":self.id,
							"statement_line_ids": self.bank_statement_id.line_ids.ids,
							"company_ids": self.bank_statement_id.mapped("company_id").ids,
						},
					}
        elif self.bank_statement_id and self.bank_statement_id.state == 'posted':
            return {
                    "type": "ir.actions.client",
                    "tag": "bank_statement_reconciliation_view",
                    "context": {
                        "is_uudp": True,
                        "pencairan_id":self.id,
                        "statement_line_ids": self.bank_statement_id.line_ids.ids,
                        "company_ids": self.bank_statement_id.mapped("company_id").ids,
                    },
                }
    
    
    # @api.onchange('uudp_ids')
    # def onchange_uudp_ids(self):
    #     import pdb;pdb.set_trace()
    #     if self.uudp_ids:
    #         active_form = self._context.get('params', False)
    #         if active_form :
    #             exist = self.env['uudp.pencairan'].search([('id','=',active_form['id'])])
    #             todelete = exist.uudp_ids.filtered(lambda x: x.id not in tuple(self.uudp_ids.ids))
    #             for del in todelete :
    #                 del.write({'pencairan_id' : False, 'tgl_pencairan' : False, 'type_pencairan' : False})

    @api.depends('uudp_ids.state','journal_entry_ids.state')
    def get_total_pencairan(self):
        for rec in self:
            total = 0
            if rec.uudp_ids:
                for u in rec.uudp_ids:
                    total += u.total_ajuan
                rec.total_pencairan = total

            elif rec.journal_entry_ids:
                for u in rec.journal_entry_ids:
                    for l in u.line_ids:
                        total += l.credit
                rec.total_pencairan = total
            else:
                rec.total_pencairan = 0


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('uudp.pencairan') or '/'
        vals['name'] = seq
        if vals.get('ajuan_id'):
            ajuan_id = self.env['uudp'].browse(vals.get('ajuan_id'))
            if ajuan_id:
                ajuan_id.sudo().write({'kasir_id':self.env.user.id})
        return super(uudpPencairan, self).create(vals)

    # @api.multi
    def button_confirm(self):
        self.ensure_one()
        if self.type == 'parsial':
            self.ajuan_id.write({'type_pencairan':'parsial','pencairan_id':self.id})
            # self.post_mesages_pencairan('Confirmed')
            for uudps in self.uudp_ids :
                uudps.write({'tgl_pencairan': self.tgl_pencairan})
            return self.write({'state' : 'confirm_parsial'})
        elif self.type == 'once':
            for ajuan in self.uudp_ids:
                datas = {'type_pencairan':'once'} 
                # ketika confirm langsung assign
                # if ajuan.cara_bayar == 'cash' :
                datas.update({'total_pencairan'      : ajuan.total_ajuan,
                            'pencairan_id'          : self.id,
                            'tgl_pencairan'         : self.tgl_pencairan,
                            'terbilang'             : terbilang.terbilang(int(round(ajuan.total_ajuan,0)), "IDR", "id"),})    

                ajuan.write(datas)
            # self.post_mesages_pencairan('Confirmed')
            return self.write({'state' : 'confirm_once'})

    # @api.multi
    def button_cancel(self):
        self.ensure_one()
        if self.type == 'parsial':
            if self.bank_statement_id:
                self.bank_statement_id.button_reopen()
                self.bank_statement_id.unlink()
            if self.journal_entry_ids and not self.user_has_groups('base.group_system'):
                raise UserError(_('Pencairan parsial tidak bisa dicancel ketika ajuan sudah pernah dicairkan'))
            elif self.journal_entry_ids and self.user_has_groups('base.group_system'):
                for journal in self.journal_entry_ids:
                    journal.button_draft()
                    journal.with_context(force_delete=True).unlink()
            # self.post_mesages_pencairan('Cancelled')
        elif self.type == 'once':
            if self.uudp_ids:
                for u in self.uudp_ids:
                    if u.state not in ('confirm_accounting','done') :
                        u.write({'type_pencairan':False, 'pencairan_id'  : False, 'tgl_pencairan':False})
        # self.post_mesages_pencairan('Cancelled')
        return self.write({'state' : 'cancel'})


    # @api.multi
    def button_force_cancel(self):
        self.ensure_one()
        if self.type == 'parsial':
            import logging;
            _logger = logging.getLogger(__name__)
            _logger.warning('='*40)
            _logger.warning('message')
            _logger.warning('='*40)
            # self.post_mesages_pencairan('Back to Confirm Parsial')
        elif self.type == 'once':
            raise UserError(_('Pencairan once tidak bisa force cancel !'))
        return self.write({'state' : 'confirm_parsial'})

    # @api.multi
    def button_set_to_draft(self):
        self.ensure_one()
        self.ajuan_id.write({'type_pencairan' : False,'pencairan_id':False, 'tgl_pencairan':False})
        return self.write({'state' : 'draft'})

    # @api.multi
    def button_refuse(self):
        self.ensure_one()
        if self.type == 'parsial':
            if self.journal_entry_ids:
                raise UserError(_('Pencairan parsial tidak bisa direfuse ketika ajuan sudah pernah dicairkan'))
        elif self.type == 'once':
            if self.uudp_ids:
                for u in self.uudp_ids:
                    u.write({'state' : 'refuse'})

        self.post_mesages_pencairan('Refused')
        return self.write({'state' : 'refuse'})

    # @api.multi
    def button_done_once(self):
        self.ensure_one()
        total_ajuan = 0
        now = datetime.datetime.now()
        if self.uudp_ids:
            for ajuan in self.uudp_ids:
                tgl_pencairan = self.tgl_pencairan
                if ajuan.tgl_pencairan :
                    tgl_pencairan = ajuan.tgl_pencairan
                #  tansfer tidak langsung create jurnal
                if ajuan.cara_bayar == 'setor_tunai' :
                    datas = {'total_pencairan'          : ajuan.total_ajuan,
                                'state'                 : 'confirm_accounting',
                                'pencairan_id'          : self.id,
                                'tgl_pencairan'         : tgl_pencairan,
                                'terbilang'             : terbilang.terbilang(int(round(ajuan.total_ajuan,0)), "IDR", "id"),}
                    ajuan.write(datas)
                    continue 
                account_move = self.env['account.move']
                reference =  self.name + ' - ' + ajuan.name
                journal_exist = account_move.sudo().search([('ref','=',reference)])
                if not journal_exist :
                #  tansfer langsung create jurnal     
                    account_move_line = []
                    total_kredit = 0
                    # not_confirmed_accounting = ajuan.uudp_ids.filtered(lambda x: x.state != 'confirm_accounting')
                    # if not_confirmed_accounting :
                    #     raise AccessError(_('Ada ajuan yang belum confirm accounting !') )
                    employee = ajuan.employee_id.id
                    # partner = ajuan.responsible_id.partner_id.id
                    for juan in ajuan.uudp_ids :
                        if juan.partner_id :
                            employee = juan.employee_id.id
                        tag_id = False
                        if juan.store_id and juan.store_id.account_analytic_tag_id :
                            tag_id = [(6, 0, [juan.store_id.account_analytic_tag_id.id])]
                        if ajuan.type == 'pengajuan' :
                            debit = ajuan.coa_debit
                            if not debit :
                                raise AccessError(_('Debit acount pada ajuan %s belum diisi !') % (ajuan.name) )
                        else :
                            debit = juan.coa_debit
                            if not debit :
                                raise AccessError(_('Debit Account lines pada ajuan %s belum diisi !') % (ajuan.name) )
                        #account debit
                        if juan.total > 0.0 :
                            for line in juan.uudp_ids:
                                account_move_line.append((0, 0 ,{
                                                                'account_id'       : line.account_id.id,
                                                                'employee_id'       : employee,
                                                                # 'partner_id'        : partner,
                                                                'analytic_account_id' : ajuan.department_id.analytic_account_id.id or False,
                                                                'analytic_tag_ids'  : tag_id,
                                                                'name'              : line.description,
                                                                'debit'             : line.total,
                                                                'date'              : tgl_pencairan,
                                                                'date_maturity'     : tgl_pencairan}))
                        elif juan.total < 0.0 :
                            account_move_line.append((0, 0 ,{'account_id'       : debit.id,
                                                            # 'partner_id'        : partner,
                                                            'employee_id'        : employee,
                                                            'analytic_account_id' : ajuan.department_id.analytic_account_id.id or False,
                                                            'analytic_tag_ids'  : tag_id,
                                                            'name'              : juan.description,
                                                            'credit'             : -juan.total,
                                                            'date'              : tgl_pencairan,
                                                            'date_maturity'     : tgl_pencairan}))
                    if not self.coa_kredit :
                        raise AccessError(_('Credit account pada pencairan %s belum diisi !') % (self.name) )
                    #account credit bank / hutang
                    notes = ajuan.notes
                    if not notes :
                        notes= self.coa_kredit.name
                    account_move_line.append((0, 0 ,{'account_id'       : self.coa_kredit.id,
                                                    'employee_id'        : ajuan.employee_id.id,
                                                    # 'partner_id'        : ajuan.responsible_id.partner_id.id,
                                                    'analytic_account_id' : ajuan.department_id.analytic_account_id.id or False,
                                                    'name'              : notes,
                                                    'credit'            : ajuan.total_ajuan,
                                                    'date'              : tgl_pencairan,
                                                    'date_maturity'     : tgl_pencairan}))

                    data={"journal_id"  : self.journal_id.id,
                          "ref"         : self.name + ' - ' + ajuan.name,
                          "date"        : tgl_pencairan,
                          "company_id"  : self.company_id.id,
                          "narration"   : self.notes,
                          "terbilang"   : terbilang.terbilang(int(round(ajuan.total_ajuan,0)), "IDR", "id"),
                          "line_ids"    : account_move_line,}

                    journal_entry = self.env['account.move'].create(data)
                    journal_entry.post()
                    # if ajuan.state not in ('confirm_accounting','done') :
                    #     raise AccessError(_('Ajuan %s belum confirm accounting !') % (ajuan.name))
                    ajuan.write({'total_pencairan'      : ajuan.total_ajuan,
                                    'state'             : 'done',
                                    'journal_entry_id'  : journal_entry.id,
                                    'pencairan_id'      : self.id,
                                    'terbilang'         : terbilang.terbilang(int(round(ajuan.total_ajuan,0)), "IDR", "id"),})

        # self.post_mesages_pencairan('Done')
        return self.write({'state': 'done'})

    # @api.multi
    # def button_done_once(self):
    #     self.ensure_one()
    #     for ajuan in self.uudp_ids:
    #         ajuan.write({'total_pencairan'      : ajuan.total_ajuan,
    #                             'state'         : 'confirm_accounting',
    #                             'pencairan_id'  : self.id,
    #                             'tgl_pencairan': self.tgl_pencairan,
    #                             'terbilang'     : terbilang.terbilang(int(round(ajuan.total_ajuan,0)), "IDR", "id"),})

    #     self.post_mesages_pencairan('Done')
    #     return self.write({'state': 'done'})

    # @api.multi
    def button_done_parsial(self):
        self.ensure_one()
        # if not self.journal_entry_ids:
        #     raise AccessError(_('Ajuan belum pernah dicairkan!') )
        self.ajuan_id.write({'state':'done','total_pencairan' : self.ajuan_id.pencairan_id.total_pencairan})
        # self.post_mesages_pencairan('Done')
        return self.write({'state' : 'done'})

    # @api.multi
    def unlink(self):
        for ttf in self:
            if ttf.state != 'draft':
                raise UserError(_('Data yang bisa dihapus hanya yang berstatus draft !'))
        return super(uudpPencairan, self).unlink()