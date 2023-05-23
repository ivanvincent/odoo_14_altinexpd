from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError
import datetime
from . import terbilang
from ast import literal_eval

class pencairanWizard(models.TransientModel):
	_name = 'pencairan.wizard'

	def _get_active_uudp(self):
		context = self.env.context
		if context.get('active_model') == 'uudp.pencairan':
			return context.get('active_id', False)
		return False

	def _get_active_company(self):
		context = self.env.context
		if context.get('active_model') == 'uudp.pencairan':
			if context.get('active_id', False) :	
				return self.env['uudp.pencairan'].browse(context.get('active_id')).company_id.id

	uudp_pencairan_id = fields.Many2one(comodel_name='uudp.pencairan', 
						  required=False,
					      string='UUDP',
					      default=_get_active_uudp)
	nominal = fields.Float(string="Nominal Pencairan", required=True)
	debit_account_id = fields.Many2one("account.account", string="Different Account", help="Akun di sisi debet (lawan bank/cash)")
	debit_account_notes = fields.Text("Notes", help="Label pada account move line bank/credit")
	company_id = fields.Many2one("res.company", string="Company",default=_get_active_company)
	date = fields.Date(string="Tanggal Pencairan", required=True, default=fields.Datetime.now)
	notes = fields.Text("Notes", help="Label pada account move line bank/credit")
 
 
	@api.model
	def default_get(self,fields):
		res = super(pencairanWizard,self).default_get(fields)
		pencairan_id = self._context.get('active_id')
		pencairan_id = self.env['uudp.pencairan'].browse(pencairan_id)
		if pencairan_id:
			res['nominal'] = pencairan_id.ajuan_id.total_ajuan
		return res

	def action_pencairan(self):
		nominal = self.nominal
		sisa_pencairan = self.uudp_pencairan_id.sisa_pencairan_parsial
		not_confirmed_accounting = self.uudp_pencairan_id.uudp_ids.filtered(lambda x: x.state != 'confirm_accounting')
		# if not_confirmed_accounting :
		# 	raise AccessError(_('Ada ajuan yang belum confirm accounting !') )
		now = datetime.datetime.now()
		if nominal <= 0:
			raise UserError(_('Nominal pencairan tidak boleh 0!'))

		if not self.uudp_pencairan_id.sisa_pencairan_parsial and not self.uudp_pencairan_id.journal_entry_ids and nominal > self.uudp_pencairan_id.ajuan_id.total_ajuan:
			raise UserError(_('Nominal pencairan tidak boleh melebihi total ajuan!'))

		if self.uudp_pencairan_id.journal_entry_ids and nominal > sisa_pencairan:
			raise UserError(_('Nominal pencairan tidak boleh melebihi sisa nominal ajuan yang belum dicairkan!'))

		# self._cr.execute("SELECT description FROM uudp_detail WHERE uudp_id=%s" , ( [(self.uudp_pencairan_id.ajuan_id.id)] ))
		# descriptions = self._cr.dictfetchall()
		# des = []
		# for d in descriptions:
		# 	des.append(str(d['description']))

		# all_desciptions = ' '.join(des)
		if not self.uudp_pencairan_id.coa_kredit :
			raise UserError(_('Credit account belum diisi !'))		
		
		account_move_line = []
		bank_cash_line_ids = []
		debt = self.uudp_pencairan_id.ajuan_id.coa_debit
		if self.debit_account_id :
			debt = self.debit_account_id 
		label_debit = self.debit_account_notes
		if not label_debit :
			label_debit = debt.name
		label_credit = self.notes
		if not label_credit :
			label_credit = self.uudp_pencairan_id.coa_kredit.name
		
  		# #account credit
		account_move_line.append((0, 0 ,{'account_id' 	: self.uudp_pencairan_id.coa_kredit.id, 
										'employee_id'	: self.uudp_pencairan_id.ajuan_id.employee_id.id, 
										# 'partner_id'	: self.uudp_pencairan_id.ajuan_id.responsible_id.partner_id.id, 
										# 'analytic_account_id':self.uudp_pencairan_id.ajuan_id.department_id.analytic_account_id.id, 
										'name' 			: label_credit, 
										'credit' 		: self.nominal, 'date_maturity':self.date}))

		for line in self.uudp_pencairan_id.ajuan_id.uudp_ids:
			#account debit
			account_move_line.append((0, 0 ,{'account_id' 	: line.coa_debit.id, 
											'employee_id'	: self.uudp_pencairan_id.ajuan_id.employee_id.id,
											# 'partner_id'	: self.uudp_pencairan_id.ajuan_id.responsible_id.partner_id.id,
											########################################################################
											### 
											### coment dulu karena analytic_account_id belum ad di department_id
											### 
											########################################################################
											# 'analytic_account_id':self.uudp_pencairan_id.ajuan_id.department_id.analytic_account_id.id,
											'name' 			: label_debit, 
											'debit' 		: line.total, 
											'date_maturity' :self.date}))   
   
		bank_cash_line_ids += [(0,0,{"date":self.date,"partner_id":self.uudp_pencairan_id.ajuan_id.responsible_id.partner_id.id,'employee_id':self.uudp_pencairan_id.ajuan_id.employee_id.id,"payment_ref":label_credit,"credit":self.uudp_pencairan_id.ajuan_id.total_ajuan})]
		



		#create journal entry
		data={"uudp_pencairan_id": self.uudp_pencairan_id.id,
			  "journal_id":self.uudp_pencairan_id.journal_id.id,
			  "ref":self.uudp_pencairan_id.name,
			  "date":self.date,
			  "company_id":self.uudp_pencairan_id.company_id.id,
			  "terbilang": terbilang.terbilang(int(round(self.nominal,0)), "IDR", "id"),
			  "line_ids":account_move_line,}


		journal_entry = self.env['account.move'].create(data)
		if journal_entry:
			journal_entry.post()
			total = 0
			sisa = 0
			for journal in self.uudp_pencairan_id.journal_entry_ids:
				total += journal.amount_total
			sisa = self.uudp_pencairan_id.ajuan_id.total_ajuan - total


		# 	########################################################################
		# 	### 
		# 	### coment dulu pengurangan pencairan harus saat reconcile
		# 	### 
		# 	########################################################################
		# 	# self.uudp_pencairan_id.write({'sisa_pencairan_parsial':sisa})
		# 	# self.uudp_pencairan_id.ajuan_id.write({'total_pencairan':total})

		# 	if total == self.uudp_pencairan_id.ajuan_id.total_ajuan:
		# 		# self.uudp_pencairan_id.ajuan_id.write({'state':'done'})
		# 		self.uudp_pencairan_id.write({'state':'posted'})
		# 		# self.uudp_pencairan_id.write({'state':'done'})

		bank_cash_values = {
			"journal_id": self.uudp_pencairan_id.journal_id.id,
			"operation_type":'payment',
			"date":self.date,
			"line_ids":bank_cash_line_ids
   
		}
  
		statement_id = self.env['account.bank.statement'].create(bank_cash_values)
		if statement_id:
			self.uudp_pencairan_id.write({"bank_statement_id":statement_id.id})
			for line in statement_id.line_ids:
				line.onchange_credit()
    
			# self.uudp_pencairan_id.action_post_statement()
			# statement_id._end_balance()
			# statement_id._check_balance_end_real_same_as_computed()
			# statement_id.button_post()

			# if statement_id.state == 'posted':
			# 	return {
			# 			"type": "ir.actions.client",
			# 			"tag": "bank_statement_reconciliation_view",
			# 			"context": {
			# 				"is_uudp": True,
			# 				"pencairan_id":self.uudp_pencairan_id.id,
			# 				"statement_line_ids": statement_id.line_ids.ids,
			# 				"company_ids": statement_id.mapped("company_id").ids,
			# 			},
			# 		}

  
		# return journal_entry

  
	# def create_bank_statement(self):
		

class EditAjuanWizard(models.TransientModel):
	_name = 'edit.ajuan.wizard'


	def _get_default_date(self):
		context = self.env.context
		if context.get('active_model') == 'uudp':
			return context.get('active_id', False)
		return False

	date = fields.Date("Date",default=_get_default_date)

EditAjuanWizard()

class PencairanMultiWizard(models.TransientModel):

	_name = 'pencairan.multi.wizard'



	journal_id 	  = fields.Many2one('account.journal', string='Journal',required=True, )
	coa_debit 	  = fields.Many2one('account.account', string='COA Debit',domain=[('user_type_id', '=', 5), ('reconcile', '=', True)])
	type 		  = fields.Selection([("pengajuan","Pengajuan"),("reimberse","Reimberse")], string='Type',compute="_get_type",store=True,)
	pengajuan_ids = fields.Many2many(comodel_name='uudp', relation='uudp_pencairan_multi_wizard_rel',string='Pengajuan',domain=[('type', '!=', 'penyelesaian'), ('pencairan_id', '=', False)])
	pencairan_ids = fields.Many2many(comodel_name='uudp.pencairan', relation='uudp_pencairan_ids_multi_wizard_rel',string='pencairan')
	
 
	@api.depends('pengajuan_ids')
	@api.depends_context('pengajuan')
	def _get_type(self):
		for line in self:
			if line.pengajuan_ids:
				line.type = line.pengajuan_ids[0].type
			else:
				line.type = 'pengajuan'
 
	@api.model
	def default_get(self,fields):
		res = super(PencairanMultiWizard,self).default_get(fields)
		ajuan_ids = self._context.get('active_ids')
		active_model = self._context.get('active_model')

		if active_model == 'uudp' and ajuan_ids:
			ajuan_ids = self.env['uudp'].browse(ajuan_ids)
			same_journal = all(ajuan.journal_id == ajuan_ids[0].journal_id for ajuan in ajuan_ids)
			if ajuan_ids.filtered(lambda m: m.pencairan_id):
				raise UserError('Pastikan memilih ajuan yang belum di ajukan pencairan')
			if ajuan_ids.filtered(lambda l:l.type != 'penyelesaian'):
				res['journal_id'] = ajuan_ids[0].journal_id.id
				res['pengajuan_ids'] = [(6,0,ajuan_ids.ids)]
			
		return res

 

	def action_pencairan(self):
		statement_id = self.env['account.bank.statement']
		statement_lines = []
		pencairan_ids = []
  
		for line in self.pengajuan_ids:
			
			if line.total_ajuan == 0.00:
				raise UserError('Mohon maaf ajuan %s total ajuan masih 0'%(line.name))
			elif line.state != 'confirm_finance':
				raise UserError('Mohon maaf ajuan %s belum di confirm finance'%(line.name))
			elif line.bank_statement_id:
				raise UserError('Mohon maaf ajuan %s sudah terbentuk bank statement'%(line.name))
		
			elif not self.journal_id:
				raise UserError('Mohon maaf Journal harus di isi')
		
			uudp_pencairan_id = self.env['uudp.pencairan'].create({
				"journal_id":self.journal_id.id,
				"type":'parsial',
				"ajuan_id":line.id,
			})
   

			line.sudo().write({"coa_debit":self.coa_debit.id})
			uudp_pencairan_id._onchange_ajuan_id()
   
			statement_lines += [(0,0,{"account_id":line.coa_debit.id,"date":line.date,'pencairan_id':uudp_pencairan_id.id,'employee_id':line.employee_id.id,"payment_ref":uudp_pencairan_id.name,"credit":line.total_ajuan})]
			
			if uudp_pencairan_id:
				self.pencairan_ids = [(4,uudp_pencairan_id.id)]
				uudp_pencairan_id.button_confirm()
				movelines =[]
				tes = []
			
				# movelines +=[(0, 0 ,{'account_id' 	: self.journal_id.payment_credit_account_id.id, 
				# 					'employee_id'	: uudp_pencairan_id.ajuan_id.employee_id.id, 
				# 					'name' 			: line.name, 
				# 					'credit' 		: uudp_pencairan_id.ajuan_id.total_ajuan, 
				# 					'date_maturity':uudp_pencairan_id.tgl_pencairan})]
				# for ajuan_line in uudp_pencairan_id.ajuan_id.uudp_ids:
				# 	movelines +=[(0, 0 ,{'account_id' 	: ajuan_line.coa_debit.id, 
				# 							'employee_id'	: uudp_pencairan_id.ajuan_id.employee_id.id,
				# 							'name' 			: line.name, 
				# 							'debit' 		: ajuan_line.total, 
				# 							'date_maturity' :uudp_pencairan_id.tgl_pencairan})] 
				# movelines +=[(0, 0 ,{'account_id' 	: self.journal_id.default_account_id.id, 
				# 					'employee_id'	: uudp_pencairan_id.ajuan_id.employee_id.id, 
				# 					'name' 			: line.name, 
				# 					'credit' 		: uudp_pencairan_id.ajuan_id.total_ajuan, 
				# 					'date_maturity':uudp_pencairan_id.tgl_pencairan})]
				# movelines +=[(0, 0 ,{'account_id' 	: uudp_pencairan_id.ajuan_id.coa_debit.id, 
				# 						'employee_id'	: uudp_pencairan_id.ajuan_id.employee_id.id,
				# 						'name' 			: uudp_pencairan_id.name, 
				# 						'debit' 		: uudp_pencairan_id.ajuan_id.total_ajuan, 
				# 						'date_maturity' :uudp_pencairan_id.tgl_pencairan})] 
				# #create journal entry
				# move={"uudp_pencairan_id": uudp_pencairan_id.id,
				# "journal_id":self.journal_id.id,
				# "ref":uudp_pencairan_id.name,
				# "date":uudp_pencairan_id.tgl_pencairan,
				# "company_id":uudp_pencairan_id.company_id.id,
				# "terbilang": terbilang.terbilang(int(round(uudp_pencairan_id.ajuan_id.total_ajuan,0)), "IDR", "id"),
				# "line_ids":movelines,}

				# journal_entry = self.env['account.move'].create(move)
				# if journal_entry:
				# 	journal_entry.post()
				# 	uudp_pencairan_id.write({"state":'posted'})


		statement_id = self.env['account.bank.statement'].create({
			"journal_id": self.journal_id.id,
			"operation_type":'payment',
			"date":fields.Date.today(),
			"line_ids":statement_lines,
			"move_line_ids": movelines
		})

		if statement_id:
			for line in self.pencairan_ids:
				line.write({'bank_statement_id':statement_id.id})
			for line in statement_id.line_ids:
				line.onchange_credit()
			coa_debit_ids = []
			if self.pengajuan_ids.filtered(lambda x: not x.ajuan_id and x.type == 'reimberse'):
				# statement_id.button_post()
				action = self.env.ref('vit_uudp.action_uudp_pencairan_parsial').sudo().read()[0]
				action['domain'] = [('id','in',[x.id for x in self.pengajuan_ids.mapped('pencairan_id')])]
				action['context'] = {}
				return action
   			
      		# for ajuan in self.pengajuan_ids.filtered(lambda x: not x.ajuan_id and x.type == 'reimberse'):
			# 	for line in ajuan.uudp_ids:
			# 		coa_debit_ids.append({"account_id":{"id":line.coa_debit.id,"name":line.coa_debit.name},"amount":-abs(line.sub_total),"uudp_id":line.uudp_id.id })
				
			return {
				'type'     : 'ir.actions.act_window',
				'name'     : 'Bank Statement',
				'res_model': 'account.bank.statement',
				'view_mode': 'form',
				'res_id'   :  statement_id.id,
				'context'  : {'account_id':uudp_pencairan_id.ajuan_id.coa_debit.id,
                  'is_reimburse':True if self.type == 'reimberse' else False,
                  'is_uudp':True,'payment_type':'outbound',
                  'statement_line_ids':statement_id.line_ids.ids,
                  'coa_debit_ids': coa_debit_ids,
                  'is_multi':True
                  },
				'target'   : 'current',
			}
			
				
			
