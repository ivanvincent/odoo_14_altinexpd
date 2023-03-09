from odoo import fields, models, api, _
from odoo.exceptions import UserError

class PenyelesaianWizard(models.TransientModel):

    _name = 'penyelesaian.wizard'
    
    
    
    
    penyelesaian_id   = fields.Many2one('uudp', string='Penyelesaian',domain=[('type', '=', 'penyelesaian')])
    ajuan_id          = fields.Many2one('uudp', string='No Kasbon',domain=[('type', '=', 'pengajuan')],related="penyelesaian_id.ajuan_id")
    type              = fields.Selection(selection=lambda self: self._get_selection(), string='Type')
    sisa_penyelesaian = fields.Float(string='Sisa Penyelesaian')
    journal_id        = fields.Many2one('account.journal', string='Journal')
    line_ids          = fields.One2many('penyelesaian.line.wizard', 'wizard_id', 'Detail')
    cara_bayar        = fields.Selection([("cash","Cash"),("transfer","Transfer")], string='Cara Bayar',default="cash")
    
    
    def _get_selection(self):
        context = self._context.get('default_sisa_penyelesaian') or self._context.get('sisa_penyelesaian')
        if context is not None and context == 0:
            return [("selesai","Close")]
        elif context is not None and context > 0:
            return [("kembali","Kembalikan"),("bebankan","Di Bebankan")]
        elif context is not None and context < 0:
            return [("bebankan","Di Bebankan"),("reimburse","Reimburse")]
    
    
    @api.model
    def default_get(self,fields):
        res = super(PenyelesaianWizard,self).default_get(fields)
        context = self._context
        
        if context.get('default_penyelesaian_id') and not context.get('default_type'):
            ajuan_id = self.env['uudp'].browse(context.get('default_penyelesaian_id'))
            line_ids = []
            if ajuan_id.uudp_ids:
                for line in ajuan_id.uudp_ids.filtered(lambda x:x.is_different):
                    total_ajuan =  sum(line.uudp_id.ajuan_id.uudp_ids.filtered(lambda x:x.template_id.id == line.template_id.id and x.product_id.id == line.product_id.id  and x.coa_debit == line.coa_debit).mapped('sub_total'))
                    line_ids += [(0,0,{
                        "account_id":line.coa_debit.id,
                        "uudp_line_id":line.id,
                        "product_id":line.product_id.id,
                        "total": line.sub_total - total_ajuan ,
                        "description":line.description
                        }) 
                    ]
                    
                res['line_ids'] = line_ids
                res['sisa_penyelesaian'] = ajuan_id.sisa_penyelesaian
        if context.get('default_penyelesaian_id') and context.get('default_type') == 'receipt':
            ajuan_id = self.env['uudp'].browse(context.get('default_penyelesaian_id'))
            line_ids = []
            if ajuan_id.uudp_ids and not ajuan_id.journal_entry_id and not ajuan_id.bank_statement_id:
                for line in ajuan_id.uudp_ids.filtered(lambda x:x.is_different):
                    total_ajuan =  sum(line.uudp_id.ajuan_id.uudp_ids.filtered(lambda x:x.template_id.id == line.template_id.id and x.product_id.id == line.product_id.id  and x.coa_debit == line.coa_debit).mapped('sub_total'))
                    
                    line_ids += [(0,0,{
                        "account_id":ajuan_id.ajuan_id.coa_debit.id,
                        "uudp_line_id":line.id,
                        "product_id":line.product_id.id,
                        # "total":  abs(ajuan_id.sisa_penyelesaian),
                        "total": total_ajuan - line.sub_total ,
                        # "total":  abs(ajuan_id.sisa_penyelesaian),
                        "description":line.description
                        }) 
                    ]
                    
                res['line_ids'] = line_ids
                res['sisa_penyelesaian'] = ajuan_id.sisa_penyelesaian
            elif ajuan_id.uudp_ids and ajuan_id.journal_entry_id and not ajuan_id.bank_statement_id:
                line_ids += [(0,0,{
                    "account_id":ajuan_id.ajuan_id.coa_debit.id,
                    # "uudp_line_id":line.id,
                    "product_id":ajuan_id.uudp_ids[0].product_id.id,
                    # "total":  abs(ajuan_id.sisa_penyelesaian),
                    "total": ajuan_id.sisa_penyelesaian ,
                    # "total":  abs(ajuan_id.sisa_penyelesaian),
                    # "description":line.description
                    }) 
                ]
                    
                res['line_ids'] = line_ids
                res['sisa_penyelesaian'] = ajuan_id.sisa_penyelesaian
        
        return res
    
    
    @api.onchange('type')
    def onchange_type(self):
        import logging
        if self.type == 'bebankan' and self.sisa_penyelesaian > 0:
            line_ids = []
            self.line_ids = False
            for line in  self.penyelesaian_id.uudp_ids.filtered(lambda x:x.is_different):
                total_ajuan =  sum(line.uudp_id.ajuan_id.uudp_ids.filtered(lambda x:x.template_id.id == line.template_id.id and x.product_id.id == line.product_id.id  and x.coa_debit == line.coa_debit).mapped('sub_total'))
                line_ids += [(0,0,{
                    "account_id":line.coa_debit.id,
                    "uudp_line_id":line.id,
                    "product_id":line.product_id.id,
                    "total": total_ajuan - line.sub_total ,
                    "description":line.description
                    }) 
                ]
            self.write({"line_ids":line_ids})
        elif self.type == 'kembali' and self.sisa_penyelesaian > 0:
            line_ids = []
            self.line_ids = False
            # for line in  self.penyelesaian_id.uudp_ids.filtered(lambda x:x.is_different):
            #     total_ajuan =  sum(line.uudp_id.ajuan_id.uudp_ids.filtered(lambda x:x.template_id.id == line.template_id.id and x.product_id.id == line.product_id.id  and x.coa_debit == line.coa_debit).mapped('sub_total'))
            line_ids += [(0,0,{
                "account_id":self.ajuan_id.coa_debit.id,
                # "uudp_line_id":line.id,
                "product_id":self.penyelesaian_id.uudp_ids[0].product_id.id,
                "total": self.sisa_penyelesaian,
                # "description":line.description
                }) 
            ]
            self.write({"line_ids":line_ids})
    
    def _check_account_beban(self):
        
        for line in self.line_ids:
            if line.account_id.id == self.ajuan_id.coa_debit.id:
                return True
                

    def validation_check(self):
        # if self.type == 'kembali' and self.sisa_penyelesaian != self.penyelesaian_id.sisa_penyelesaian:
        #     raise UserError('Sisa Penyelesaian harus sama dengan yang akan dikembalikan !!!')

        if self.type == 'kembali' and sum(self.line_ids.mapped('total')) > self.sisa_penyelesaian:
            raise UserError('Mohon maaf jumlah yg di  akan kembalikan melebihi sisa penyelesaian')
        elif self.type == 'reimburse' and abs(self.sisa_penyelesaian) != sum(self.line_ids.mapped('total')):
            raise UserError('Sisa Penyelesaian harus sama dengan yang akan direimburse !!!')
    
        elif self.type == 'bebankan' and sum(self.line_ids.mapped('total')) > self.sisa_penyelesaian:
            raise UserError('Mohon maaf jumlah yg di  akan dibebankan melebihi sisa penyelesaian !!!')
        elif self.type == 'bebankan' and self._check_account_beban():
            raise UserError('Mohon account tidak sesuai !!!')
                
            
                    
    
    
    def create_journal_beban(self):
        move_line = []
        for line in self.line_ids:
            move_line += [(0,0,{
                'account_id'       : line.account_id.id,
                'employee_id'       : self.ajuan_id.employee_id.id, 
                # 'analytic_tag_ids' : tag_id,
                'name'             : self.penyelesaian_id.name, 
                'analytic_account_id': self.ajuan_id.department_id.analytic_account_id.id,
                'credit'            : line.total, 
                'date_maturity'    : fields.Date.today()
            })]
        move_line += [(0,0,{
            'account_id'       : self.ajuan_id.coa_debit.id,
            'employee_id'       : self.ajuan_id.employee_id.id, 
            # 'analytic_tag_ids' : tag_id,
            'name'             : self.penyelesaian_id.name, 
            'analytic_account_id': self.ajuan_id.department_id.analytic_account_id.id,
            'debit'            : sum(self.line_ids.mapped('total')), 
            'date_maturity'    : fields.Date.today()
        })]
        
        account_move = self.env['account.move'].sudo().create({
            "journal_id":self.journal_id.id,
            "ref": self.penyelesaian_id.name + ' - '+ self.ajuan_id.name ,
            "uudp_penyelesaian_id":self.penyelesaian_id.id,
            "date":fields.Date.today(),
            # "narration" : self.notes,
            "company_id":self.env.company.id,
            "line_ids":move_line
        })
        
        if account_move:
            account_move.post()
            
            move_line = []
            for line in self.penyelesaian_id.uudp_ids:
                move_line += [(0,0,{
                    'account_id'       : line.coa_debit.id,
                    'employee_id'       : self.ajuan_id.employee_id.id, 
                    # 'analytic_tag_ids' : tag_id,
                    'name'             : line.description, 
                    'analytic_account_id': self.ajuan_id.department_id.analytic_account_id.id,
                    'debit'            : line.sub_total, 
                    'date_maturity'    : fields.Date.today()
                })]
            move_line += [(0,0,{
                'account_id'       : self.ajuan_id.coa_debit.id,
                'employee_id'       : self.ajuan_id.employee_id.id, 
                # 'analytic_tag_ids' : tag_id,
                'name'             : self.penyelesaian_id.name, 
                'analytic_account_id': self.ajuan_id.department_id.analytic_account_id.id,
                'credit'            : sum(self.penyelesaian_id.uudp_ids.mapped('sub_total')), 
                'date_maturity'    : fields.Date.today()
            })]
            
            account_move = self.env['account.move'].sudo().create({
                "journal_id":self.journal_id.id,
                "uudp_penyelesaian_id":self.penyelesaian_id.id,
                "ref": self.penyelesaian_id.name + ' - '+ self.ajuan_id.name ,
                "date":fields.Date.today(),
                # "narration" : self.notes,
                "company_id":self.env.company.id,
                "line_ids":move_line
            })
            
            account_move.post()
            
            
            if self.sisa_penyelesaian < 0:
                self.penyelesaian_id.write({"journal_entry_id":account_move.id,"sisa_penyelesaian":self.penyelesaian_id.sisa_penyelesaian + sum(self.line_ids.mapped('total'))})
            elif self.sisa_penyelesaian > 0:
                self.penyelesaian_id.write({"journal_entry_id":account_move.id,"sisa_penyelesaian":self.penyelesaian_id.sisa_penyelesaian - sum(self.line_ids.mapped('total'))})
            
            
            if not self.ajuan_id.category_id.is_purchase and self.penyelesaian_id.sisa_penyelesaian == 0.00:
                self.penyelesaian_id.ajuan_id.write({'selesai':True,'sisa_penyelesaian':0.00})
                self.penyelesaian_id.write({'state':'done',"journal_id":self.journal_id.id})
                
    
    def create_reimburse(self):
        self.ensure_one()
        uudp_ids = []
        for line in self.line_ids:
            uudp_ids +=[(0,0,{
                'product_id':line.product_id.id,
                'qty':1,
                'description':line.description,
                'coa_debit':line.account_id.id,
                'unit_price':line.total})]
            
            
        reimburse_id = self.env['uudp'].create({
                'type':'reimberse',
                'employee_id':self.ajuan_id.employee_id.id,
                'coa_debit':self.ajuan_id.coa_debit.id,
                'department_id':self.ajuan_id.department_id.id,
                'cara_bayar':self.cara_bayar,
                'journal_id':self.journal_id.id,
                'date': fields.Date.today(),
                'end_date': fields.Date.today(),
                'uudp_ids': uudp_ids
            })
            
        if reimburse_id:
            self.penyelesaian_id.write({'reimburse_id':reimburse_id.id,"journal_id":self.journal_id.id})
            
            
    def create_statement_in(self):
        account_move_line = []
        today=fields.Date.today()
        total_debit = 0
        # for ajuan in self.penyelesaian_id.uudp_ids:
        #     employee = self.ajuan_id.employee_id
        #     tag_id = False
        #     ajuan_total = ajuan.sub_total
        #     if ajuan.sub_total > 0.0 :
        #         account_move_line.append((0, 0 ,{'account_id'        : ajuan.coa_debit.id,
        #                                         'employee_id'        : employee.id, 
        #                                         'analytic_tag_ids'   : tag_id,
        #                                         'name' : self.penyelesaian_id.name, 
        #                                         'analytic_account_id': self.ajuan_id.department_id.analytic_account_id.id,
        #                                         'debit'             : ajuan.sub_total, 
        #                                         'date_maturity'      : today})) #,
        #     total_debit += ajuan_total    
        # account_move_line.append((0, 0 ,{'account_id' : self.ajuan_id.coa_debit.id, 
        #                                 'employee_id': employee.id, 
        #                                 'analytic_account_id':self.ajuan_id.department_id.analytic_account_id.id,
        #                                 'name' : self.penyelesaian_id.name, 
        #                                 'credit' : total_debit, 
        #                                 'date_maturity':today})) #, 

        #create journal entry
        # journal_id = self.ajuan_id.pencairan_id.journal_id
        # if not journal_id :
        #     journal_id = self.env['account.move'].sudo().search([('ref','ilike','%'+self.ajuan_id.name+'%')],limit=1)
        #     if not journal_id :
        #         raise UserError(_('Journal pencairan tidak ditemukan !'))
        #     journal_id = journal_id.journal_id
        # data={
        #     "journal_id":journal_id.id,
        #     "ref": self.ajuan_id.name + ' - '+ self.penyelesaian_id.name ,
        #     "date":today,
        #     # "narration" : self.notes,
        #     "uudp_penyelesaian_id":self.penyelesaian_id.id,
        #     "company_id":self.env.company.id,
        #     "line_ids":account_move_line,}

        # journal_entry = self.env['account.move'].create(data)
        # if journal_entry:
        #     journal_entry.post()
        total = sum(self.line_ids.mapped('total'))
        if not self.penyelesaian_id.bank_statement_id and self.penyelesaian_id.sisa_penyelesaian:
            bank_cash_values = {
                "journal_id": self.journal_id.id,
                "operation_type":'receipt',
                "date":today,
                "state":'open',
                "line_ids":[(0,0,{
                            "account_id":self.ajuan_id.coa_debit.id,
                            "date":today,
                            'employee_id':self.ajuan_id.employee_id.id,
                            "payment_ref":"Penyelesaian %s"%(self.ajuan_id.name),
                            "debit":total})]
    
            }
    
            statement_id = self.env['account.bank.statement'].create(bank_cash_values)
            if statement_id:
                for line in statement_id.line_ids:
                    line.onchange_credit()
                    line.move_id.write({"uudp_penyelesaian_id":self.penyelesaian_id.id,"ref":self.penyelesaian_id.name})
                    
            self.penyelesaian_id.write({"bank_statement_id":statement_id.id})
            # self.penyelesaian_id.bank_statement_id.button_post()
            
            return {
				'type'     : 'ir.actions.act_window',
				'name'     : 'Bank Statement',
				'res_model': 'account.bank.statement',
				'view_mode': 'form',
				'res_id'   :  statement_id.id,
				'context'  : {'account_id':self.ajuan_id.coa_debit.id,
                                'is_uudp':True,
                                "is_penyelesaian": True,
                                "penyelesaian_id":self.penyelesaian_id.id,
                                "company_ids": statement_id.mapped("company_id").ids,
                                'payment_type':'inbound','statement_line_ids':statement_id.line_ids.ids},
				'target'   : 'current',
			}
			
            
            
    def action_submit(self):
        self.ensure_one()
        self.validation_check()
        if self.type == 'bebankan':
            self.create_journal_beban()
        elif self.type == 'reimburse':
            self.create_reimburse()
        elif self.type == 'kembali':
            return self.create_statement_in()
        else:
            move_line = []
            for line in self.penyelesaian_id.uudp_ids:
                move_line += [(0,0,{
                    'account_id'       : line.coa_debit.id,
                    'employee_id'       : self.ajuan_id.employee_id.id, 
                    # 'analytic_tag_ids' : tag_id,
                    'name'             : self.penyelesaian_id.name, 
                    'analytic_account_id': self.ajuan_id.department_id.analytic_account_id.id,
                    'debit'            : line.sub_total, 
                    'date_maturity'    : fields.Date.today()
                })]
            move_line += [(0,0,{
            'account_id'       : self.ajuan_id.coa_debit.id,
            'employee_id'       : self.ajuan_id.employee_id.id, 
            # 'analytic_tag_ids' : tag_id,
            'name'             : self.penyelesaian_id.name, 
            'analytic_account_id': self.ajuan_id.department_id.analytic_account_id.id,
            'credit'            : sum(self.penyelesaian_id.uudp_ids.mapped('sub_total')), 
            'date_maturity'    : fields.Date.today()
            })]
            
            account_move = self.env['account.move'].sudo().create({
            "journal_id":self.journal_id.id,
            "ref": self.penyelesaian_id.name + ' - '+ self.ajuan_id.name ,
            "uudp_penyelesaian_id":self.penyelesaian_id.id,
            "date":fields.Date.today(),
            # "narration" : self.notes,
            "company_id":self.env.company.id,
            "line_ids":move_line
            })
        
            if account_move:
                account_move.post()
                self.penyelesaian_id.write({"journal_entry_id":account_move.id})
                self.penyelesaian_id.ajuan_id.write({'selesai':True})
                self.penyelesaian_id.write({'state':'done',"journal_id":self.journal_id.id})
       
           
            
                
            
                



class PenyelesaianLineWizard(models.TransientModel):

    _name = 'penyelesaian.line.wizard'
    
    wizard_id    = fields.Many2one('penyelesaian.wizard', string='Wizard')
    uudp_line_id = fields.Many2one('uudp.detail', string='UUDP Detail')
    product_id   = fields.Many2one('product.product', string='Product',domain=[('can_be_expensed', '=', True)])
    description  = fields.Char(string='Description')
    account_id   = fields.Many2one('account.account', string='Account')
    total        = fields.Float(string='Total')
    
    
 
    