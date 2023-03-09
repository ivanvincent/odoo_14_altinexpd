from sys import intern
from odoo import api, fields, models, exceptions, _
import datetime
from ast import literal_eval
from odoo.exceptions import UserError, AccessError, ValidationError
from . import terbilang
import json
import logging
_logger = logging.getLogger(__name__)

class uudp(models.Model):
    _name = 'uudp'
    _order = 'name desc'
    _inherit = ['mail.thread','mail.activity.mixin']

    
    def action_create_pencairan(self):
        if not self.pencairan_id:
            pencairan_id = self.env['uudp.pencairan'].create({
				"journal_id":self.journal_id.id,
				"type":'parsial',
				"ajuan_id":self.id,
			})
            movelines =[]
            
            if pencairan_id:
                pencairan_id.button_confirm()
                movelines +=[(0, 0 ,{'account_id' 	: self.journal_id.payment_credit_account_id.id, 
									'employee_id'	: pencairan_id.ajuan_id.employee_id.id, 
									'name' 			: self.name, 
									'credit' 		: pencairan_id.ajuan_id.total_ajuan, 
									'date_maturity':pencairan_id.tgl_pencairan})]
                for ajuan_line in pencairan_id.ajuan_id.uudp_ids:
                    movelines +=[(0, 0 ,{'account_id' 	: ajuan_line.coa_debit.id, 
											'employee_id'	: pencairan_id.ajuan_id.employee_id.id,
											'name' 			: self.name, 
											'debit' 		: ajuan_line.total, 
											'date_maturity' :pencairan_id.tgl_pencairan})] 
                	#create journal entry
                move    = { "uudp_pencairan_id": pencairan_id.id,
                            "journal_id":self.journal_id.id,
                            "ref":pencairan_id.name,
                            "date":pencairan_id.tgl_pencairan,
                            "company_id":pencairan_id.company_id.id,
                            "terbilang": terbilang.terbilang(int(round(pencairan_id.ajuan_id.total_ajuan,0)), "IDR", "id"),
                            "line_ids":movelines,
                            }
                journal_entry = self.env['account.move'].create(move)
                statement_lines = [(0,0,{"date":self.date,'employee_id':self.employee_id.id,"payment_ref":pencairan_id.name,"credit":self.total_ajuan})]
                
                if journal_entry:
                    journal_entry.post()
                    pencairan_id.write({"state":'posted'})
                
                statement_id = self.env['account.bank.statement'].create({
                    "journal_id": self.journal_id.id,
                    "operation_type":'payment',
                    "date":fields.Date.today(),
                    "line_ids":statement_lines
                })
                if statement_id:
                    for line in self.pencairan_ids:
                        line.write({'bank_statement_id':statement_id.id})
                    for line in statement_id.line_ids:
                        line.onchange_credit()
            

    #########################
    #Fungsi message discuss #
    #########################
    def post_mesages_uudp(self,state):
        ir_model_data_sudo = self.env['ir.model.data'].sudo()

        uudp_user    = ir_model_data_sudo.get_object('vit_uudp', 'group_user_uudp_user')
        uudp_manager = ir_model_data_sudo.get_object('vit_uudp', 'group_user_uudp_manager')
        hrd          = ir_model_data_sudo.get_object('hr','group_hr_manager')
        finance      = ir_model_data_sudo.get_object('account','group_account_manager')

        uudp_user_partner_ids     = uudp_user.users.mapped('partner_id')
        uudp_manager_partner_ids  = uudp_manager.users.mapped('partner_id')
        hrd_partner_ids           = hrd.users.mapped('partner_id')
        finance_ids               = finance.users.mapped('partner_id')

        uudp_user_partners    =  map(lambda x:x['id'],uudp_user_partner_ids)
        uudp_manager_partners =  map(lambda x:x['id'],uudp_manager_partner_ids)
        hrd_partners          =  map(lambda x:x['id'],hrd_partner_ids)
        finance_partners      =  map(lambda x:x['id'],finance_ids)

        receivers = False

        if self.type == 'pengajuan':
            if self.need_driver == True:
                receivers = uudp_user_partners + uudp_manager_partners + hrd_partners + finance_partners
            else:
                receivers = uudp_user_partners + uudp_manager_partners + finance_partners
        else:
            receivers = uudp_user_partners + finance_partners

        subject = _("UUDP")
        body = 'UUDP '+ str(self.type) + ' ' +str(state)
        messages = self.message_post(body=body, subject=subject)
        messages.update({'needaction_partner_ids' : [(6, 0, receivers)]})
        return True

    ##########################################################################
    #Fungsi write untuk update data state detail berdasarkan state parentnya #
    ##########################################################################

    def write_state_line(self, state):
        line = self.env['uudp.detail'].search([('uudp_id','=',self.id)])
        if line:
            for l in line:
                l.write({'state' : state})

    #######################################################################################################################
    # Fungsi pengecekan total pengajuan UUDP (untuk cek total penyelesaian agar tidak lebih dari pengajuan)               #
    #                                                                                                                     #
    # Di action write terdapat banyak pengecekan, ini untuk mengecek detail penyelesaian, apakah record ada yg diupdate,  #
    # delete ataupun dicreate, semua total nya selanjutnya dijumlah dan dibandingkan dengan total pengajuan uudp          #
    #######################################################################################################################

    def check_total_uudp(self, action, total_ajuan, uudp_id, uudp_detail):
        if action == 'create':

            total = 0
            for i in uudp_detail:
                total += i[2]['total']
            if total > total_ajuan:
                return True
            return False

        elif action == 'write':

            total = 0

            #cari dulu uudp pengajuan nya
            uudp_pengajuan = self.env['uudp'].sudo().search([('id','=',uudp_id)])

            #lalu cari total uudp pengajuannya
            nominal_uudp = self.env['uudp.detail'].sudo().search([('uudp_id','=',uudp_pengajuan.ajuan_id.id)])
            for n in nominal_uudp:
                total += n.sub_total

            nominal_noupdate = 0
            nominal_update = 0
            nominal_create = 0
            total_nominal = 0
            product = self.env['product.product']
            product_uudp = False
            for line in uudp_detail:

                #kode 0 berarti record baru
                #kode 1 berarti record diupdate
                #kode 2 berarti record didelete
                #kode 4 berarti record tidak diupdate ataupun didelete

                if line[0] == 4 :
                    uudp_line = line[1]
                    uudp_noupdate = self.env['uudp.detail'].sudo().search([('uudp_id','=',uudp_id),('id','=',uudp_line)])
                    for k in uudp_noupdate:
                        nominal_noupdate = nominal_noupdate + k.total

                if line[0] == 0 :
                    nominal_create = nominal_create + line[2]['total']
                    if 'product_id' in line[2] :
                        uudp_exist = product.browse(line[2]['product_id']).name
                        if uudp_exist in ('Piutang UUDP','PIUTANG UUDP') :
                            product_uudp = line[2]['total']
                if line[0] == 1 and 'total' in line[2]:
                    nominal_update = nominal_update + line[2]['total']
                    if 'product_id' in line[2] :
                        uudp_exist = product.browse(line[2]['product_id']).name
                        if uudp_exist in ('Piutang UUDP','PIUTANG UUDP') :
                            product_uudp = line[2]['total']

                if line[0] == 1 and 'total' not in line[2]:
                    line_id = line[1]
                    uudp_update = self.env['uudp.detail'].sudo().search([('uudp_id','=',uudp_id),('id','=',line_id)])
                    for uu in uudp_update:
                        nominal_update = nominal_update + uu.total

                total_nominal = nominal_noupdate + nominal_create + nominal_update
            if uudp_pengajuan.state != 'draft' and uudp_pengajuan.type == 'penyelesaian':
                total_awal = sum(uudp_pengajuan.uudp_ids.mapped('sub_total'))
                if total_nominal > total_awal :
                    sisa_awal = uudp_pengajuan.sisa_penyelesaian
                    sisa_sekarang = uudp_pengajuan.total_ajuan_penyelesaian - total_nominal
                    if product_uudp :
                        if round(product_uudp,2) > round(sisa_awal,2) :
                            raise UserError(_('Selain status draft, sisa penyelesaian (%s lebih besar dari %s) harus sama dengan lines Piutang UUDP !')%(product_uudp , sisa_awal))
                        elif round(product_uudp,2) < round(sisa_awal,2) :
                            raise UserError(_('Selain status draft, sisa penyelesaian (%s lebih kecil dari %s) harus sama dengan lines Piutang UUDP !')%(product_uudp , sisa_awal))
                    else :
                        raise UserError(_('Selain status draft, sisa penyelesaian (%s) tidak bisa dikurangi (%s) !')%(sisa_awal,sisa_sekarang))
            if round(total_nominal,2) > round(total,2):
                #raise UserError(_('Total Nominal %s lebih besar dari total penyelesaian %s')%(total_nominal,total))
                return True
            return False

    #######################################################
    # Default journal untuk uudp berdasarkan company user #
    #######################################################

    def _default_journal(self):
        return self.env.context.get('default_journal_id') or self.env['account.journal'].search([('name', 'ilike', 'Miscellaneous Operation'),
                                                                                              ('company_id','=',self.env['res.company']._company_default_get().id)], limit=1)

    ################################################################
    # Proteksi tidak bisa membuat pengajuan untuk penerima yg sama # 
    # ketika ajuan sebelumnya belum selesai                        #
    ################################################################

    def check_unfinished_submission(self, user_id):
        myajuan = self.env['uudp'].search([('employee_id','=',user_id),
                                            ('type','=','pengajuan'),
                                            ('id','!=',self.id),
                                            ('state', 'not in', ['refuse','cancel'])],
                                             limit=10, order='id desc')
        
        import logging;
        _logger = logging.getLogger(__name__)
        _logger.warning('='*40)
        _logger.warning(self._origin.category_id.is_urgent)
        _logger.warning(myajuan)
        _logger.warning('='*40)
        
        if myajuan and not self._origin.category_id.is_urgent:
            amount = len(myajuan)
            if amount >= 1:
                for m in myajuan:
                    unfinished = self.env['uudp'].search([('ajuan_id','=',m.id),('type','=','penyelesaian'),('state','=','done')])
                    if not unfinished:
                        raise ValidationError(_("Anda tidak bisa membuat pengajuan untuk penerima yg sama (%s), ketika ajuan sebelumnya (%s) belum penyelesaian (3)!") % (m.employee_id.name, m.name))
        elif myajuan and self.category_id.is_rute_sale:
            if len(myajuan) >=1:
                if self.driver_id.id in [x.driver_id.id for x in myajuan.mapped('driver_id')] or self.driver_id.id in [x.helper_id.id for x in myajuan.mapped('helper_id')] or self.driver_id.id in [x.sales_id.id for x in myajuan.mapped('sales_id')]:
                    for ajuan in myajuan:
                        unfinished = self.env['uudp'].search([('ajuan_id','=',m.id),('type','=','penyelesaian'),('state','=','done')])
                        raise ValidationError(_("Anda tidak bisa membuat pengajuan untuk driver (%s), ketika ajuan sebelumnya (%s) belum penyelesaian (3)!") % (m.driver_id.name, m.name))
                    
                for ajuan in myajuan:
                    unfinished = self.env['uudp'].search([('ajuan_id','=',m.id),('type','=','penyelesaian'),('state','=','done')])
                    # rute_id = ajuan.rute_id.id
                
                # for ajuan in myajuan:
                    
        
        
        return True

    def _subscribe_assigned_to_user(self, subtype_ids=None):
        """If the responsible user, subscribe it."""
        for rec in self:
            if not rec.employee_id:
                continue
            rec.message_subscribe(
                partner_ids=[rec.employee_id.id], subtype_ids=subtype_ids)

       
    @api.onchange('company_id')
    def onchange_comp_ids(self):
        if self.company_id :
            return {'domain':{'company_id':[('id','in',self.env.user.company_ids.ids)]}}


    name = fields.Char(string="Code", default="New", readonly=True)
    user_id = fields.Many2one("res.users", string="Admin", default=lambda self: self.env.user, store=True, required=True, track_visibility='onchange',)
    department_id = fields.Many2one("hr.department", string="Department", track_visibility='onchange',)
    company_id = fields.Many2one("res.company", string="Company",default=lambda self: self.env['res.company']._company_default_get(), required=True)
    type = fields.Selection([('pengajuan', 'Pengajuan'), 
                             ('penyelesaian', 'Penyelesaian'), 
                             ('reimberse', 'Reimberse'),],string='Type', required=True, track_visibility='onchange',)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting Department'),
                              ('confirm_department', 'Confirmed Department'),
                              ('confirm_department1', 'Waiting HRD'),
                              ('confirm_department2', 'Waiting KND'),
                              ('confirm_hrd', 'Confirmed HRD'),
                              ('confirm_knd', 'Confirmed KND'),
                              ('pending', 'Pending'),
                              ('confirm_finance', 'Confirmed Finance'),
                              ('confirm_accounting', 'Confirmed Accounting'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled'),
                              ('refuse','Refused')], default='draft', required=True, index=True, track_visibility='onchange',)
    uudp_ids   = fields.One2many("uudp.detail", inverse_name="uudp_id", track_visibility='onchange',)
    # uudp_lines = fields.One2many("uudp.detail", compute="_compute_lines",)
    coa_debit = fields.Many2one("account.account", string="Debit Account",)
    
    coa_kredit = fields.Many2one("account.account", string="Credit Account",default=lambda self:self._get_default_coa_kredit())
    ajuan_id = fields.Many2one('uudp', string="Kasbon", domain="[('type','=','pengajuan')]")
    total_ajuan = fields.Float(string="Total Ajuan", track_visibility='onchange',)
    total_ajuan_penyelesaian = fields.Float(string="Nominal Kasbon", related="ajuan_id.total_pencairan", readonly=True, track_visibility='onchange',)
    need_driver = fields.Boolean(string="Perjalanan Dinas?", track_visibility='onchange',)
    need_driver_penyelesaian = fields.Boolean(string="Penyelesaian Perjalanan Dinas?", related="ajuan_id.need_driver",store=True)
    selesai = fields.Boolean(string="Selesai ?")
    is_selesai = fields.Char(string="Selesai",compute="_get_status_ajuan")
    journal_id = fields.Many2one("account.journal", string="Journal", track_visibility='onchange',domain=lambda self: self._filter_journal())# default=_default_journal)
    journal_entry_id = fields.Many2one("account.move", string="Journal Entry")
    difference = fields.Many2one("account.account", string="Difference Account", track_visibility='onchange')
    difference_notes = fields.Char("Difference Notes", track_visibility='onchange')
    responsible_id = fields.Many2one("res.users", string="Responsible", track_visibility='onchange')
    cara_bayar = fields.Selection([('cash', 'Cash'), 
                                   ('setor_tunai', 'Setor Tunai'),],string='Cara Bayar',default="cash" ,track_visibility='onchange',)
    bank_id = fields.Many2one("res.bank", string="Bank", track_visibility='onchange',)
    date_start = fields.Date(string='From', default=fields.Date.today(),help="Tanggal Berangkat perjalan dinas")
    date_end = fields.Date(string='To',default=fields.Date.today(),help="Tanggal Selesai perjalan dinas")
    kasir_id = fields.Many2one('res.users', string='Kasir')
    no_rekening = fields.Char(string="Nomor Rekening", track_visibility='onchange',)
    atas_nama = fields.Char(string="Atas Nama", track_visibility='onchange',)
    notes = fields.Text(string="Notes", track_visibility='onchange')
    total_pencairan = fields.Float(string="Nominal Kasbon", track_visibility='onchange',)
    type_pencairan = fields.Selection([('once', 'Once'), 
                                       ('parsial', 'Parsial'),],string='Type Pencairan')
    date = fields.Datetime(string="Required Date", required=True, default=fields.Datetime.now, track_visibility='onchange',)
    terbilang = fields.Char(string='Terbilang', translate=True, readonly=True, states={'draft': [('readonly', False)]})
    is_user_pencairan = fields.Boolean(compute="check_validity")
    pencairan_id = fields.Many2one("uudp.pencairan","Pencairan")
    tgl_pencairan = fields.Date("Tanggal Pencairan",)# related="pencairan_id.tgl_pencairan", store=True)
    sisa_penyelesaian = fields.Float("Sisa Penyelesaian", compute="_get_sisa_penyelesaian", store=True,track_visibility='onchange',)
    total_penyelesaian= fields.Float("Total Penyelesaian", compute="_get_sisa_penyelesaian", store=True,track_visibility='onchange',)
    end_date          = fields.Datetime(string="End Date",  track_visibility='onchange',)
    by_pass_selisih   = fields.Boolean("By Pass Different Amount",  track_visibility='onchange')
    selesai_id        = fields.Many2one('uudp','Selesai ID',compute="search_input_penyelesaian")
    penyelesaian_id   = fields.Many2one('uudp','Penyelesaian')# store ke db
    tgl_penyelesaian  = fields.Date("Tgl Penyelesaian")
    is_po             = fields.Boolean(string='Pembelian ?',default=False,)
    order_id          = fields.Many2one('purchase.order', string='Purchase Order',domain=[('state', '=', 'purchase')])
    order_line        = fields.One2many( related="order_id.order_line",string="Purchase Order Lines")
    picking_ids       = fields.Many2many('stock.picking', compute='_compute_picking', string='No Penerimaan', copy=False)
    bop_type          = fields.Selection([("customer","Selling"),("drop","Drop"),('kombinasi','Kombinasi')], string='Bop Type')
    order_amount_total= fields.Monetary(string='Nominal PO',related="order_id.amount_total")
    currency_id       = fields.Many2one(related="order_id.currency_id", string='Currency')
    employee_id       = fields.Many2one('hr.employee', string='Yang Mengajukan')
    credit_limit      = fields.Float(string='Credit Limit',related="employee_id.credit_limit")
    sisa_limit        = fields.Float(string='Sisa Limit',related="employee_id.sisa_limit")
    job_id            = fields.Many2one(string='Position',related="employee_id.job_id")
    emp_barcode       = fields.Char(string='NIP',related="employee_id.barcode")
    category_id       = fields.Many2one('uudp.category', string='Category',domain=lambda self:self._check_allowed_category())
    allow_limit       = fields.Boolean(string='Allow Limit ?',related="category_id.is_limit")
    category_name     = fields.Char(string='Category Name',related='category_id.name',store=True,)
    description       = fields.Html('Description')
    pr_ids            = fields.Many2many(comodel_name='purchase.request', relation='uudp_purchase_request_rel',string='Purchase Request')
    pr_line_ids       = fields.Many2many(comodel_name='purchase.request.line', string='Purchase Request Details',compute="_get_purchase_request")
    bank_statement_id = fields.Many2one('account.bank.statement', string='Bank Statement')
    is_reconciled     = fields.Boolean(string='Reconciled ?')
    is_rute_sale      = fields.Boolean(string='Route Sale ?',related="category_id.is_rute_sale",store=True,)
    # rute_id           = fields.Many2one('rute.sale', string='Rute Sale')
    warehouse_id      = fields.Many2one('stock.warehouse', string='Stock Point')
    warehouse_ids     = fields.Many2many(comodel_name='stock.warehouse', relation='uudp_stock_warehouse_ids_res',string='Stock Point')
    jalur_ids          = fields.Many2many( comodel_name='res.partner.jalur', relation='uudp_res_partner_jalur_ids_rel', string='Jalur' )
    vehicle_id        = fields.Many2one('fleet.vehicle', string='No Pol')
    model_id          = fields.Many2one(related='vehicle_id.model_id', string='Vehicle')
    km_awal           = fields.Float(string='KM Awal')
    km_akhir          = fields.Float(string='KM Akhir')
    is_shipment       = fields.Boolean(string='Is Shipment ?')
    do_id             = fields.Many2one('do.head.office', string='Shipment')
    shipment          = fields.Char(string='No Shipment')
    jalur_id          = fields.Many2one('res.partner.jalur', string='Jalur')
    # allow_expense     = fields.Float(related='rute_id.jalur_id.allow_expense', string='Allow Expense')
    sales_id          = fields.Many2one(comodel_name='hr.employee', string='Sales',domain=lambda self:self._get_domain_sales())
    driver_id         = fields.Many2one(comodel_name='hr.employee',string='Driver',store=True,domain=lambda self:self._get_domain_driver())
    helper_id         = fields.Many2one(comodel_name='hr.employee', string='Helper',store=True,domain=lambda self:self._get_domain_helper())
    pic_user          = fields.Many2one('res.users',compute='get_user', string='Pengaju User', store=False)
    reimburse_id      = fields.Many2one('uudp', string='Reimburse',domain=[('type', '=', 'reimburse')])
    need_approve      = fields.Boolean(string='Need Approve',compute="_need_approve",store=True,)
    knd_approved      = fields.Boolean(string='Approved ?')
    bill_id           = fields.Many2one('account.move', string='Vendor Bill')
    aging_kasbon      = fields.Char(string='Aging',compute='_get_status_ajuan')
    vehicle_type      = fields.Selection([("double","Double"),("fuso","Fuso")], string='Tipe Mobil',default="double")
    template_comb_id  = fields.Many2one('expense.template.combine', string='Template')
    no_do             = fields.Char(string="No Do")
    # template_id       = fields.Char(string='Template',related='')

    employee_id_domain = fields.Char(
        compute="_get_employee",
        readonly=True,
        store=False,
    )
    
    
    
    @api.onchange('template_comb_id')
    def get_template_combine(self):
        expense = []
        self.uudp_ids = False
        self.warehouse_ids = [(6,0,self.template_comb_id.warehouse_ids.ids)]
        self.jalur_ids = [(6,0,self.template_comb_id.jalur_ids.ids)]
        if self.state == 'draft' and self.type == 'pengajuan' and self.bop_type == 'kombinasi' and self.is_rute_sale:
            for template in self.template_comb_id.line_ids:
                expense += [(0,0,{
                    'product_id':template.product_id.id,
                    'exp_id':template.expense_id.id,
                    'coa_debit':template.account_id.id,
                    'unit_price':template.nominal
                })]
        
            self.uudp_ids = expense
    
    
    
    def set_template_combine(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Set Template Kombinasi'),
            'res_model': 'expense.template.combine.wizard',
            'view_mode': 'form',
            'context': {'default_warehouse_ids':[(6,0,self.warehouse_ids.ids)],
                        'default_ajuan_id':self.id,
                        'default_jalur_ids':[(6,0,self.jalur_ids.ids)],
                        'default_uudp_line_ids':[(6,0,self.uudp_ids.ids)]},
            'target': 'new',
        }
       
    
    
    def _get_status_ajuan(self):
        for line in self:
            today=  fields.Datetime.today()
            line.is_selesai = 'Selesai' if line.selesai else ''
            try:
                if line.type != 'penyelesaian' and not line.tgl_penyelesaian:
                    aging = today - line.end_date
                    line.is_selesai = 'Selesai' if line.selesai else ''
                    line.aging_kasbon = str(aging.days) + '  Hari' if aging.days > 0 else False if line.type == 'pengajuan' and not line.seleai else False
                elif line.type != 'penyelesaian' and line.tgl_penyelesaian:
                    aging = line.tgl_penyelesaian - line.date
                    line.is_selesai = 'Selesai' if line.selesai else ''
                    line.aging_kasbon = str(aging.days) + '  Hari' if aging.days > 0 else False if line.type == 'pengajuan' and not line.seleai else False
                else:
                    line.aging_kasbon = ''
            except Exception as error:
                line.aging_kasbon = False 
                
    @api.depends('sales_id','driver_id','helper_id')
    def _get_employee(self):
        for line in self:
            if line.is_rute_sale:
                employee_ids = line.sales_id + line.driver_id + line.helper_id
                line.employee_id_domain = json.dumps(
                    [('id', 'in', employee_ids.ids)]
                )
            else:
                line.employee_id_domain = json.dumps([('id','!=',False)])
    
    
    def name_get(self):
        res = []
        for line in self:
            if self._context.get('penyelesaian'):
                res.append((line.id, line.name + ' | ' + line.employee_id.name if line.employee_id else ''))
            else:
                res.append((line.id, line.name))
        return res
    
    
    def _get_domain_driver(self):
        domain = []
        ir_config          = self.env['ir.config_parameter'].sudo()
        domain_driver_ids  = ir_config.get_param('domain_driver_ids')
        if domain_driver_ids:
            domain += [('job_id','in', literal_eval(domain_driver_ids))]
        return domain
        
    def _get_domain_sales(self):
        domain = []
        ir_config          = self.env['ir.config_parameter'].sudo()
        domain_sales_ids  = ir_config.get_param('domain_sales_ids')
        if domain_sales_ids:
            domain += [('job_id','in', literal_eval(domain_sales_ids))]
        return domain
    
    def _get_domain_helper(self):
        domain = []
        ir_config          = self.env['ir.config_parameter'].sudo()
        domain_helper_ids  = ir_config.get_param('domain_helper_ids')
        if domain_helper_ids:
            domain += [('job_id','in', literal_eval(domain_helper_ids))]
        return domain
    
    
    
    
    # def _compute_lines(self):
    #     for line in self:
    #         if line.uudp_ids:
    #             line.uudp_ids = self.env['uudp.detail'].search([('uudp_id', '=', line.id)])
    #         else:
    #             line.uudp_ids = False
    
    def _compute_picking(self):
        for line in self:
            pickings = self.env['stock.picking']
            for x in line.order_id.order_line:
                moves = x.move_ids | x.move_ids.mapped('returned_move_ids')
                pickings |= moves.mapped('picking_id')
            line.picking_ids = pickings
    

        
    # @api.onchange('rute_id')
    # def get_picking_rute(self):
    #     self.warehouse_id = self.rute_id.warehouse_id.id
    #     self.jalur_id = self.rute_id.jalur_id.id
    
    @api.onchange('warehouse_id')
    def get_std_time(self):
        if self.category_id.is_rute_sale and self.warehouse_id.std_time > 0:
            self.end_date = fields.Datetime.add(self.date,days=self.warehouse_id.std_time)
        
    @api.onchange('warehouse_ids')
    def get_end_date(self): 
        if self.category_id.is_rute_sale and self.warehouse_ids and self.type == 'pengajuan':
            std_time = sum(self.warehouse_ids.mapped('std_time'))
            if std_time:
                self.end_date = fields.Datetime.add(self.date,days=std_time)
        
   
    
    def _need_approve(self):
        for line in self:
            if line.type == 'penyelesaian':
                line.need_approve = True if line.uudp_ids.filtered(lambda x:x.product_id.need_approve_knd).mapped('product_id') else False
            else:
                line.need_approve = False
    
    
    # @api.onchange('rute_id')
    # def onchange_rute(self):
    #     self.sales_id = self.rute_id.sales_id.id
    #     self.driver_id = self.rute_id.driver_id.id
    #     self.helper_id = self.rute_id.helper_id.id
                
    # @api.onchange('jalur_id')
    # def onchange_jalur(self):
    #     if self.uudp_ids and self.state == 'draft':
    #         self.uudp_ids = False
    #     elif not self.uudp_ids:
    #         expense = []
    #         if self.jalur_id.expense_template_ids:
    #             for template in self.jalur_id.expense_template_ids:
    #                 expense += [(0,0,{
    #                     'product_id':template.product_id.id,
    #                     'exp_id':template.expense_id.id,
    #                     'coa_debit':template.account_id.id,
    #                     'template_id':template.id,
    #                     'description':template.description,
    #                     'unit_price':template.nominal
    #                 })]
    #             self.uudp_ids = expense
            

                
    
    # @api.onchange('jalur_ids')
    # def onchange_jalur_ids(self):
    #     expense = []
    #     if self.state == 'draft' and self.type == 'pengajuan' and self.bop_type != 'drop' and self.is_rute_sale and not self.template_comb_id:
    #         for jalur in self.jalur_ids:
    #             for template in jalur.expense_template_ids.filtered(lambda x:x.id not in [template.id for template in self.uudp_ids.mapped('template_id')]):
    #                 expense += [(0,0,{
    #                     'product_id':template.product_id.id,
    #                     'coa_debit':template.account_id.id,
    #                     'template_id':template.id,
    #                     'exp_id':template.expense_id.id,
    #                     'description':template.description,
    #                     'unit_price':template.nominal
    #                 })]
    #         for line in self.uudp_ids:
    #             if line.template_id.jalur_id.id not in self.jalur_ids.mapped('id'):
    #                 expense += [(3,line.id,0)]
    #                 # line.unlink()
                        
    #         if len(expense) > 0:
    #             self.uudp_ids = expense
                
    @api.onchange('warehouse_ids')
    def onchange_warehouse_ids(self):
        expense = []
        if self.state == 'draft' and self.type == 'pengajuan' and (self.bop_type == 'drop' or self.bop_type == 'kombinasi') and self.is_rute_sale and not self.template_comb_id:
            for warehouse in self.warehouse_ids:
                for template in warehouse.expense_template_ids.filtered(lambda x:x.id not in [template.id for template in self.uudp_ids.mapped('template_id')]):
                    expense += [(0,0,{
                        'product_id':template.product_id.id,
                        'coa_debit':template.account_id.id,
                        'exp_id':template.expense_id.id,
                        # 'template_id':template.id,
                        'description':template.description,
                        'unit_price':template.nominal if self.vehicle_type == 'double' else template.nominal_fuso
                    })]
            # for line in self.uudp_ids:
            #     if line.template_id.warehouse_id.id not in self.warehouse_ids.mapped('id'):
            #         expense += [(3,line.id,0)]
                    # line.unlink()
                        
            if len(expense) > 0:
                self.uudp_ids = expense
        
        
        
        
     
            
                    
    
    
    def _check_allowed_category(self):
        domain = []
        if not self.env.user.has_group('base.group_system') and self.env.user.has_group('vit_uudp.group_user_uudp_user'):
            domain += [('id','in',self.env.user.allowed_category.ids)]
        return domain
            
    
    @api.depends('employee_id')
    def get_user(self):
        for pengaju in self:
            user_id = self.env['res.users'].search([('tag_employee_id','=',pengaju.employee_id.id)],limit=1)
            pengaju.pic_user = user_id.id if user_id else False 
    
    
    def _get_purchase_request(self):
        for pengajuan in self:
            if pengajuan.pr_ids:
                pengajuan.pr_line_ids = [(4,line.id)  for request in pengajuan.pr_ids  for line in request.line_ids.filtered(lambda l:not l.ajuan_id and not l.purchase_state)]
            else:
                pengajuan.pr_line_ids = []
    
    
    @api.onchange('need_driver')
    def onchange_need_driver(self):
        if self.need_driver:
            self.end_date = fields.Date.add(self.date_end,days=7)
    
    @api.onchange('date')
    def onchange_date(self):
        if self.category_id.is_rute_sale and (self.end_date and self.warehouse_id and self.warehouse_id.std_time):
            self.end_date = fields.Date.add(self.date,days=self.warehouse_id.std_time)
            
    
         
    @api.onchange('date_end')
    def onchange_date_end(self):
        if self.need_driver:
            self.end_date = fields.Date.add(self.date_end,days=7)
            
    
    
    
    def _filter_journal(self):
        domain = []
        if self.ajuan_id and self.cara_bayar:
            if self.cara_bayar == 'cash':
                domain += [('type','=','cash')]
            else:
                domain += [('type','=','bank')]
        return domain
    
    def _get_default_coa_kredit(self):
        ir_config             = self.env['ir.config_parameter'].sudo()
        uudp_credit_account_id = ir_config.get_param('uudp_credit_account_id')
        if uudp_credit_account_id:
            uudp_credit_account_id = self.env['account.account'].browse(int(uudp_credit_account_id))
            return uudp_credit_account_id
        else:
            return False
        

    @api.depends('uudp_ids.qty','uudp_ids.unit_price','uudp_ids.sub_total')
    def _get_sisa_penyelesaian(self):
        for rec in self:
            total = 0
            for u in rec.uudp_ids:
                    
                total += (u.unit_price*u.qty)
            rec.sisa_penyelesaian = rec.ajuan_id.total_pencairan-total
            rec.total_penyelesaian = total if rec.type == 'penyelesaian' else 0

    @api.depends('is_user_pencairan')
    def check_validity(self):
        for rec in self:
            user_login = self.env.user.id
            res_user = self.env['res.users'].sudo().search([('id', '=',user_login)])
            if res_user.has_group('vit_uudp.group_user_uudp_pencairan') or res_user.has_group('vit_uudp.group_manager_uudp_pencairan'):
                rec.is_user_pencairan = True
            else:
                rec.is_user_pencairan = False

    def search_input_penyelesaian(self):
        #import pdb;pdb.set_trace()
        
        for rec in self:
            penyelesaian_exist = self.env['uudp'].sudo().search([('ajuan_id', '=',rec.id),('state','!=','refuse')],limit=1)
            
            
            if penyelesaian_exist :
                rec.penyelesaian_id = penyelesaian_exist.id
                rec.selesai_id = penyelesaian_exist.id
                self.env.cr.execute("update uudp set penyelesaian_id=%s, tgl_penyelesaian=%s where id = %s",
                        ( penyelesaian_exist.id, penyelesaian_exist.date, rec.id,))
            else:
                rec.selesai_id = False
                rec.penyelesaian_id = False
    
    
    def button_journal_entries(self):
        if self.type == 'penyelesaian':
            entry_ids = []
            move_ids = self.env['account.move'].search([('uudp_penyelesaian_id','=',self.penyelesaian_id.id)])
            return {
                'name': _('Journal Entries'),
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('uudp_penyelesaian_id', '=', self.id)],
                # 'domain': [('uudp_penyelesaian_id', '=', self.id)],
                
                # 'context': {
                #     'default_order':'name asc',
                #     'journal_id': self.bank_statement_id.journal_id.id,
                # }
            }
    

    @api.model
    def _get_identifier(self, type):
        result = ""
        ir_config = self.env['ir.config_parameter'].sudo()
        if type == "pengajuan":
            ajuan_sequence_id = ir_config.get_param('ajuan_sequence_id')
            ajuan_sequence_id = self.env['ir.sequence'].browse(int(ajuan_sequence_id))
            result = self.env['ir.sequence'].get('uudp_pengajuan_sequence') if not ajuan_sequence_id else ajuan_sequence_id.next_by_id()
            
        elif type == "penyelesaian":
            penyelesaian_sequence_id = ir_config.get_param('penyelesaian_sequence_id')
            penyelesaian_sequence_id = self.env['ir.sequence'].browse(int(penyelesaian_sequence_id))
            result = self.env['ir.sequence'].get('uudp_penyelesaian_sequence') if not penyelesaian_sequence_id else penyelesaian_sequence_id.next_by_id()
            
        else:
            reimburse_sequence_id = ir_config.get_param('reimburse_sequence_id')
            reimburse_sequence_id = self.env['ir.sequence'].browse(int(reimburse_sequence_id))
            result = self.env['ir.sequence'].get('uudp_reimburse_sequence') if not reimburse_sequence_id else reimburse_sequence_id.next_by_id()
        return result

    @api.model
    def create(self, vals):

        
        
        if vals['type'] == 'pengajuan':
            user_id = vals['employee_id']
            category = vals.get('category_id')
            category_id = self.env['uudp.category'].browse(category)
            if category_id and category_id.is_rute_sale and not vals.get('bop_type'):
                raise UserError('Mohon tentukan Tipe Biaya Operasional !!!')
                
            self.check_unfinished_submission(user_id)
            
            
                

        if vals['type'] == 'penyelesaian':
            ajuan_id = self.env['uudp'].browse(vals.get('ajuan_id'))
            if vals.get('end_date') and  vals.get('date') and vals.get('end_date') < vals.get('date') and not ajuan_id.category_id.is_purchase:
                raise UserError('Mohon maaf penyelesaian tidak bisa dilakukan karena melebihi batas realisasi')

            action = 'create'
            total_ajuan = vals['total_ajuan'] if 'total_ajuan' in vals else 0
            uudp_detail = vals['uudp_ids'] if 'uudp_ids' in vals else False

            # error = self.check_total_uudp(action, total_ajuan, False, uudp_detail)
            
            # if error and not self.ajuan_id.category_id.name.lower() == 'pembelian':
            #     raise ValidationError(_("Total penyelesaian melebihi total pengajuan!"))


        # seq = self.env['ir.sequence'].next_by_code('uudp') or '/'
        vals['name'] = self._get_identifier(vals['type'])

        res = super(uudp, self).create(vals)
        res._subscribe_assigned_to_user()
        total = 0
        coaDebit = False
        # import pdb;pdb.set_trace()
        uudpLine = self.env['uudp.detail'].search([('uudp_id','=',res.id)])
        if uudpLine:
            for g in uudpLine:
                total += g.sub_total
        if res.type != 'penyelesaian':
            res.write({'total_ajuan': total})
        if res.type == 'reimberse':
            res.write({'total_pencairan':total})
        return res

    @api.model
    def write(self, vals, context=None):
        if context != None:
            if 'employee_id' in context:
                user_id = context['employee_id']
                if self.type == 'pengajuan' :
                    self.check_unfinished_submission(user_id)

            action = 'write'
            uudp_id = vals[0]
            error = False
            this_uudp = self.env['uudp'].search([('id','=',uudp_id)])
            
          

            # protek hanya user accounting yg bisa edit ketika status selain draft
            if this_uudp.state != 'draft':
                if not self.env.user.has_group('account.group_account_manager') :
                    raise ValidationError(_("Data yang bisa di edit hanya yang berstatus 'Draft' !"))

            # import pdb;pdb.set_trace()
            if 'uudp_ids' in context and this_uudp.type == 'penyelesaian':
                uudp_detail = context['uudp_ids']

                error = self.check_total_uudp(action, False, uudp_id, uudp_detail)
                
            # if error and not self.ajuan_id.category_id.name.lower() == 'pembelian':
            #     raise ValidationError(_("Total penyelesaian melebihi total pengajuan!"))
            # else:
            for tu in this_uudp:
                total = 0
                res = tu.write(context)
                sub = self.env['uudp'].search([('id','=',uudp_id)])
                sub._subscribe_assigned_to_user()
                get_total = self.env['uudp.detail'].search([('uudp_id','=',tu.id)])
                for g in get_total:
                    total += g.sub_total
                if tu.type != 'penyelesaian':
                    res = tu.write({'total_ajuan':total})
                if tu.type == 'reimberse':
                    res = tu.write({'total_pencairan':total})

                if res:
                    return True
                else:
                    return False
        return super(uudp, self).write(vals)
    
    def action_open_reimburse(self):
        if self.type == 'penyelesaian' and self.sisa_penyelesaian < 0 and not self.reimburse_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Pengajuan Reimburse',
                'res_model': 'reimburse.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context':{'default_ajuan_id':self.ajuan_id.id,'default_journal_id':self.ajuan_id.pencairan_id.journal_id.id,'default_penyelesaian_id':self.id ,'default_lebih_bayar':abs(self.sisa_penyelesaian)}
            }
            
            
    def button_tekor(self):
            if self.type == 'penyelesaian' and self.sisa_penyelesaian < 0 and not self.reimburse_id:
                account_move = self.env['account.move']
                account_move_line = []
                total_debit = 0.0
                employee = self.ajuan_id.employee_id.id
                for line in self.uudp_ids.filtered(lambda x:x.is_different):
                    
                    ajuan = sum(line.uudp_id.ajuan_id.uudp_ids.filtered(
                        lambda x:x.product_id.id == line.product_id.id 
                        and x.coa_debit == line.coa_debit).mapped('sub_total'))
                    ajuan_total = line.sub_total - ajuan
                    total_debit += ajuan_total 
                    account_move_line.append((0, 0 ,{'account_id'        : line.coa_debit.id,
                                                    'employee_id'        : employee, 
                                                    'analytic_tag_ids'   : False,
                                                    'name'               : line.description, 
                                                    'analytic_account_id': self.department_id.analytic_account_id.id,
                                                    'credit'             : ajuan_total, 
                                                    'date_maturity'      : self.date})) #,
                    
                    
                
                account_move_line.append((0, 0 ,{'account_id' : 1570, 
                                    'employee_id': employee, 
                                    'analytic_account_id':self.department_id.analytic_account_id.id,
                                    # 'name' : self.notes, 
                                    'debit' : total_debit, 
                                    'date_maturity':self.date})) #, 
                
                journal_id = self.ajuan_id.pencairan_id.journal_id
                if not self.journal_entry_id:
                        data={"journal_id":journal_id.id,
                        "ref": self.ajuan_id.name + ' - '+ self.name ,
                        "date":self.date,
                        "narration" : self.notes,
                        "company_id":self.company_id.id,
                        "line_ids":account_move_line,}
                        journal_entry = self.env['account.move'].create(data)
                        journal_entry.post()
                        self.journal_entry_id =  journal_entry.id



    def button_confirm(self):
        if self.type == 'pengajuan':
            if (self.sisa_limit < 1 or self.sisa_limit < sum(self.uudp_ids.mapped('total'))) and self.category_id.is_limit and not self.category_id.is_urgent:
                raise UserError('Mohon maaf limit tidak mencukupi untuk pengajuan')
    
        if self.type == 'reimberse':
            attachment = self.env['ir.attachment'].search([('res_model','=','uudp'),('res_id','=',self.id)])
            if not attachment:
                raise UserError(_('Attachment masih kosong, silahkan lampirkan file / dokumen pendukung untuk melanjutkan.'))
       
        if self.type == 'penyelesaian' and (self.order_id  and self.category_id.is_purchase) and len(self.picking_ids) <=0:
            raise UserError('Belum Ada Penerimaan untuk po %s'%(self.order_id.name))
        elif self.type == 'penyelesaian' and (self.order_id  and self.category_id.is_purchase) and len(self.picking_ids) > 0:
            for picking in self.picking_ids:
                if picking.state != 'done':
                    raise UserError('Penerimaan %s Belum Di validate'%(picking.name))
        elif self.type == 'penyelesaian' and self.is_rute_sale:
            if self.km_awal < 1:
                    raise UserError('KM awal tidak boleh nol !!!')
            elif self.km_akhir < 1:
                    raise UserError('KM akhir tidak boleh nol !!!')
            
            

        self.write_state_line('confirm')
        self.write({'state' : 'confirm'})
        
                
        if self.type == 'pengajuan' and self.is_rute_sale:
            self.write({"state":"confirm_finance","total_ajuan":sum(self.uudp_ids.mapped('sub_total'))})
        
        if self.pr_ids:
            for pr in self.pr_ids:
                pr.sudo().write({"ajuan_id":self.id})
        # if self.rute_id:
        #     self.rute_id.sudo().write({'ajuan_id':self.id})
        
        # self.post_mesages_uudp('Confirmed')

    def button_pending(self):
        self.write_state_line('pending')
        # self.post_mesages_uudp('Pending')
        return self.write({'state' : 'pending'})

    def button_re_confirm_department(self):
        if self.type != 'penyelesaian' and self.env.user.id != self.department_id.manager_id.user_id.id:
            raise UserError(_('Hanya manager department yang bisa confirm pengajuan'))
        elif self.type == 'penyelesaian' and self.env.user.id != self.ajuan_id.department_id.manager_id.user_id.id:
            raise UserError(_('Hanya manager department sesuai ajuan yang bisa confirm penyelesaian'))
        else:
            if self.type == 'penyelesaian' :
                self.write({'department_id' : self.ajuan_id.department_id.id})
            self.write_state_line('confirm_department')
            # self.post_mesages_uudp('Confirmed by Manager')
            return self.write({'state' : 'confirm_department'})

    def button_confirm_department(self):
        if not self.env.user.has_group('account.group_account_manager') :
            #cek apakah user yg login adalah manager department atau bukan, jika bukan akan muncul warning ketika button confirm ditekan
            if self.type != 'penyelesaian' and self.env.user.id != self.department_id.manager_id.user_id.id:
                raise UserError(_('Hanya manager department yang bisa confirm pengajuan'))
            elif self.type == 'penyelesaian' and self.env.user.id != self.ajuan_id.department_id.manager_id.user_id.id:
                raise UserError(_('Hanya manager department sesuai ajuan yang bisa confirm penyelesaian'))

        if self.need_driver:
            self.write_state_line('confirm_department1')
            # self.post_mesages_uudp('Confirmed by Manager')
            return self.write({'state' : 'confirm_department1'})
        elif self.ajuan_id and self.ajuan_id.need_driver:
            self.write_state_line('confirm_department1')
            # self.post_mesages_uudp('Confirmed by Manager')
            return self.write({'state' : 'confirm_department1'})
        else:
            if self.type == 'penyelesaian' :
                self.write({'department_id' : self.ajuan_id.department_id.id})
            self.write_state_line('confirm_department')
            # self.post_mesages_uudp('Confirmed by Manager')
            return self.write({'state' : 'confirm_department'})

    
    def check_account_expense(self):
        for line in self.uudp_ids:
            if line.coa_debit.user_type_id.name != 'Expenses':
                raise UserError("Account %s isn't type expenses"%(line.coa_debit.name))
    
    def button_done_finance(self):
        if self.type == 'penyelesaian':
            employee = self.ajuan_id.employee_id.id
            if self.is_rute_sale:
                create_vehicle = self.env['fleet.vehicle.log.fuel'].sudo().create({
                    "vehicle_id":self.vehicle_id.id,
                    "odometer_before":self.km_awal,
                    "odometer_last":self.km_akhir,
                    "price_per_liter":self.vehicle_id.fuel_price,
                })

                # create_vehicle.action_post()
                self.check_account_expense()
                
            # partner = self.ajuan_id.responsible_id.partner_id.id
            total_ajuan = 0
            now = datetime.datetime.now()
            total_ajuan = self.total_ajuan
            # pencairan_id = self.env['uudp.pencairan'].search([('ajuan_id','=',self.ajuan_id.id)],limit=1)
            if self.description == '<p><br></p>' and self.need_driver_penyelesaian:
                raise UserError('Mohon maaf harus mengisi dulu formulir hasil perjalan dinas')
            
            if self.reimburse_id and self.reimburse_id.state != 'done':
                raise UserError('Mohon maaf proses reimburse %s belum selesai'%(self.reimburse_id.name))
            
            if self.order_id and not self.bill_id and self.journal_entry_id:
                self.button_reconcile_bill()
            # if self.order_id and not self.bill_id and (self.reimburse_id and self.reimburse_id.state == 'done'):
                # self.button_validate_po()
            
            
            if self.uudp_ids:
                account_move_line = []
                bank_cash_line_ids = []
                total_debit = 0.0
                if self.sisa_penyelesaian > 0:
                    return {
                            'type': 'ir.actions.act_window',
                            'name': 'Penyelesaian',
                            'res_model': 'penyelesaian.wizard',
                            'view_mode': 'form',
                            'target': 'new',
                            'context':{'default_penyelesaian_id':self.id,"default_type":'receipt','default_sisa_penyelesaian':self.sisa_penyelesaian,'sisa_penyelesaian':self.sisa_penyelesaian}
                        }
                elif self.sisa_penyelesaian == 0.00 and not self.journal_entry_id:
                    return {
                            'type': 'ir.actions.act_window',
                            'name': 'Penyelesaian',
                            'res_model': 'penyelesaian.wizard',
                            'view_mode': 'form',
                            'target': 'new',
                            'context':{'default_penyelesaian_id':self.id,'default_sisa_penyelesaian':self.sisa_penyelesaian,'sisa_penyelesaian':self.sisa_penyelesaian}
                        }
                elif self.sisa_penyelesaian < 0:
                    if not self.reimburse_id:
                        return {
                            'type': 'ir.actions.act_window',
                            'name': 'Penyelesaian',
                            'res_model': 'penyelesaian.wizard',
                            'view_mode': 'form',
                            'target': 'new',
                            'context':{'default_penyelesaian_id':self.id,'default_sisa_penyelesaian':self.sisa_penyelesaian,'sisa_penyelesaian':self.sisa_penyelesaian}
                        }
                    elif self.reimburse_id and self.reimburse_id.state == 'done':
                        move_line = []
                        for line in self.uudp_ids:
                            move_line += [(0,0,{
                                'account_id'       : line.coa_debit.id,
                                'employee_id'       : self.ajuan_id.employee_id.id, 
                                # 'analytic_tag_ids' : tag_id,
                                'name'             : line.description, 
                                'analytic_account_id': self.ajuan_id.department_id.analytic_account_id.id,
                                'debit'            : line.total, 
                                'date_maturity'    : fields.Date.today()
                            })]
                        move_line += [(0,0,{
                            'account_id'       : self.ajuan_id.coa_debit.id,
                            'employee_id'       : self.ajuan_id.employee_id.id, 
                            # 'analytic_tag_ids' : tag_id,
                            'name'             : self.name, 
                            'analytic_account_id': self.ajuan_id.department_id.analytic_account_id.id,
                            'credit'            : sum(self.uudp_ids.mapped('sub_total')), 
                            'date_maturity'    : fields.Date.today()
                        })]
                    
                        account_move = self.env['account.move'].sudo().create({
                            "journal_id":self.journal_id.id,
                            "uudp_penyelesaian_id":self.id,
                            "ref": self.name + ' - '+ self.ajuan_id.name ,
                            "date":fields.Date.today(),
                            # "narration" : self.notes,
                            "company_id":self.env.company.id,
                            "line_ids":move_line
                        })
                        
                        account_move.action_post()
                        
                        self.ajuan_id.write({'selesai':True})
                        self.write({'state' : 'done','journal_entry_id':account_move.id})
                        if self.ajuan_id.category_id.is_purchase:
                            self.button_reconcile_bill()
                    
                        elif not self.journal_entry_id:
                            return {
                                'type': 'ir.actions.act_window',
                                'name': 'Penyelesaian',
                                'res_model': 'penyelesaian.wizard',
                                'view_mode': 'form',
                                'target': 'new',
                                'context':{'default_penyelesaian_id':self.id,'default_sisa_penyelesaian':self.sisa_penyelesaian,'sisa_penyelesaian':self.sisa_penyelesaian}
                            }
                
    
                
    
    
    
    def action_create_bill(self):
        move_line = []
        if self.picking_ids and not self.bill_id:
            for picking in self.picking_ids:
                if picking.state != 'done':
                    raise UserError('Penerimaan no %s belum di validate'%(picking.name))
                type = picking.picking_type_id.code
                move_type = 'in_invoice'
                journal_id = self.env['account.journal'].search([('type', '=', 'purchase'), ('active', '=', True)], limit=1).id
                po_obj = self.env['purchase.order'].search([('name', '=', picking.origin)])
                price_list = {}
                for a in po_obj.order_line:
                    price_list[a.product_id.id] = a.price_unit

                    for line in picking.move_ids_without_package.filtered(lambda x:x.purchase_line_id):
                        account_id = line.product_id.categ_id.property_stock_account_input_categ_id.id if type == 'incoming' else line.product_id.categ_id.property_stock_account_output_categ_id.id
                        move_line.append((0, 0, {
                            'product_id': line.product_id.id,
                            'name': line.product_id.name,
                            'account_id': account_id,
                            'quantity': line.quantity_done,
                            'product_uom_id': line.product_uom.id,
                            'purchase_line_id': line.purchase_line_id.id,
                            'price_unit': price_list.get(line.product_id.id, 0) if po_obj else line.product_id.standard_price,
                            'tax_ids': [(6, 0, line.purchase_line_id.taxes_id.ids)],
                            
                        }))
                        

                    picking.write({'is_invoiced': True})
                    
                    move = self.env['account.move'].create({
                        'picking_id': picking.id,
                        'partner_id': picking.partner_id.id,
                        'move_type': move_type,
                        'sj_supplier': picking.surat_jalan_supplier,
                        'payment_reference': picking.name,
                        'invoice_date': picking.date_done,
                        'journal_id': journal_id,
                        'invoice_line_ids': move_line
                    })
                    
                    self.bill_id = move.id
                    self.bill_id.action_post()
            
            return self.bill_id
            
    
    def button_reconcile_bill(self):
        if self.order_id:
            if not self.bill_id:
                self.action_create_bill()
            
            ########################################################################
            ### 
            ### buat journal piutang karyawan ke uang muka pembelia
            ### 
            ########################################################################
            account_move = self.journal_entry_id
            account_id = False
            today = fields.Date.today()
            
            if not account_move:
                account_move = self.env['account.move']
                account_move_line = []
                for line in self.uudp_ids:
                    account_id = line.coa_debit
                    account_move_line += [(0,0,{
                        "account_id"    :line.coa_debit.id,
                        "employee_id"   :self.employee_id.id,
                        'name'          : self.name,
                        'credit'        : line.sub_total,
                        'company_id'    : self.company_id.id,
                        'date'          : today,
                        'date_maturity' : today
                        
                    })]
                    
                account_move_line += [(0,0, {
                    "account_id"    :self.ajuan_id.coa_debit.id,
                    "employee_id"   :self.employee_id.id,
                    'name'          : self.name,
                    'debit'        : sum(self.uudp_ids.mapped('sub_total')),
                    'company_id'    : self.company_id.id,
                    'date'          : today,
                    'date_maturity' : today
                })]
                
                account_move = account_move.sudo().create({
                        # "partner_id": self.order_id.partner_id.id,
                        'move_type':'entry',
                        "journal_id": self.ajuan_id.pencairan_id.journal_id.id,
                        "uudp_penyelesaian_id":self.id,
                        "ref": self.ajuan_id.pencairan_id.name,
                        "date": today,
                        # "narration": me_id.notes,
                        "company_id": self.env.company.id,
                        "line_ids": account_move_line,
                    })
                    
                account_move.action_post()
                account_move = account_move
            payment_move = self.env['account.move']
            payment_move_line = []
            if account_move:
                for move_line in account_move.line_ids.filtered(lambda x:x.debit > 0):
                    payment_move_line.append((0,0,{
                        # 'account_id'         : account_id.id,
                        'account_id'         : self.uudp_ids[0].coa_debit.id,
                        # 'partner_id'         :self.order_id.partner_id.id,
                        'employee_id'        : self.ajuan_id.employee_id.id,
                        # 'analytic_account_id': self.department_id.analytic_account_id.id or False,
                        'name'               : self.name,
                        'credit'              : move_line.debit,
                        'company_id'         : self.company_id.id,
                        'date'               : today,
                        'date_maturity'      : today
                    }))
                
                for move_line in self.bill_id.line_ids.filtered(lambda x:x.credit > 0):
                    destination_account_id = move_line.account_id.id
                    payment_move_line.append((0,0,{
                        'account_id'         : move_line.account_id.id,
                        'partner_id'         :self.order_id.partner_id.id,
                        'employee_id'        : self.ajuan_id.employee_id.id,
                        # 'analytic_account_id': self.department_id.analytic_account_id.id or False,
                        'name'               : self.name,
                        'debit'              : move_line.credit,
                        'company_id'         : self.company_id.id,
                        'date'               : today,
                        'date_maturity'      : today
                    }))
                
                payment_move = payment_move.sudo().create({
                    "partner_id": self.order_id.partner_id.id,
                    'move_type':'entry',
                    "uudp_penyelesaian_id":self.id,
                    "journal_id": self.ajuan_id.pencairan_id.journal_id.id,
                    "ref": self.name,
                    "date": today,
                    "company_id": self.env.company.id,
                    "line_ids":payment_move_line
                })
                if payment_move:
                    payment_move.action_post()
                    self.ensure_one()
                    lines = payment_move.line_ids.filtered(lambda x:x.debit > 0)
                    self.bill_id.js_assign_outstanding_line(lines.id)
                    self.is_reconciled = True
                    self.write_state_line('done')
                    self.ajuan_id.write({'selesai':True})
                    self.write({'state':'done'})
                
            
            
            
                
    
    
    def button_validate_po(self):
        if self.order_id and not self.is_reconciled and not self.bill_id:
            self.action_create_bill()
            move_line_ids = []
            dp_acount = self.ajuan_id.uudp_ids.mapped('coa_debit')
            destination_account_id = False
            account_move  = self.env['account.move']
            account_move_line = []
            date = self.ajuan_id.pencairan_id.tgl_pencairan
            if self.sisa_penyelesaian < 0:
                for move in self.ajuan_id.pencairan_id.journal_entry_ids:
                    for move_line in move.line_ids.filtered(lambda x:x.account_id.id == dp_acount.id and x.debit > 0):
                        account_move_line.append(
                            (0,0,{'account_id'         : move_line.account_id.id,
                            #  'partner_id':self.order_id.partner_id.id,
                            'employee_id'         : self.ajuan_id.employee_id.id,
                            # 'analytic_account_id' : self.department_id.analytic_account_id.id or False,
                            'name'                : self.name,
                            'credit'              : move_line.debit,
                            'company_id'          : self.company_id.id,
                            'date'                : date,
                            'date_maturity'       : date})
                        )
                
                if self.reimburse_id:
                    for move in self.reimburse_id.pencairan_id.journal_entry_ids:
                        for move_line in move.line_ids.filtered(lambda x:x.account_id.id == dp_acount.id and x.debit > 0):
                            account_move_line.append(
                                (0,0,{'account_id'         : move_line.account_id.id,
                                #  'partner_id':self.order_id.partner_id.id,
                                'employee_id'         : self.ajuan_id.employee_id.id,
                                # 'analytic_account_id' : self.department_id.analytic_account_id.id or False,
                                'name'                : self.name,
                                'credit'              : move_line.debit,
                                'company_id'          : self.company_id.id,
                                'date'                : date,
                                'date_maturity'       : date})
                            )
                
                account_move_line.append((0,0,{
                'account_id'         : self.ajuan_id.pencairan_id.journal_id.payment_credit_account_id.id,
                # 'partner_id'         :self.order_id.partner_id.id,
                'employee_id'        : self.ajuan_id.employee_id.id,
                # 'analytic_account_id': self.department_id.analytic_account_id.id or False,
                'name'               : self.name,
                'debit'              : self.order_id.amount_total,
                'company_id'         : self.company_id.id,
                'date'               : date,
                'date_maturity'      : date
                }))
                
                
                account_move = account_move.sudo().create({
                    # "partner_id": self.order_id.partner_id.id,
                    'move_type':'entry',
                    "journal_id": self.ajuan_id.pencairan_id.journal_id.id,
                    "ref": self.ajuan_id.pencairan_id.name,
                    "date": date,
                    # "narration": me_id.notes,
                    "company_id": self.env.company.id,
                    "line_ids": account_move_line,
                })
                
                account_move.action_post()
                
                
                
                payment_move = self.env['account.move']
                payment_move_line = []
                
                
                if account_move:
                    for move_line in account_move.line_ids.filtered(lambda x:x.debit > 0):
                        payment_move_line.append((0,0,{
                            'account_id'         : move_line.account_id.id,
                            # 'partner_id'         :self.order_id.partner_id.id,
                            'employee_id'        : self.ajuan_id.employee_id.id,
                            # 'analytic_account_id': self.department_id.analytic_account_id.id or False,
                            'name'               : self.name,
                            'credit'              : move_line.debit,
                            'company_id'         : self.company_id.id,
                            'date'               : date,
                            'date_maturity'      : date
                        }))
                    
                    for move_line in self.bill_id.line_ids.filtered(lambda x:x.credit > 0):
                        destination_account_id = move_line.account_id.id
                        payment_move_line.append((0,0,{
                            'account_id'         : move_line.account_id.id,
                            'partner_id'         :self.order_id.partner_id.id,
                            'employee_id'        : self.ajuan_id.employee_id.id,
                            # 'analytic_account_id': self.department_id.analytic_account_id.id or False,
                            'name'               : self.name,
                            'debit'              : move_line.credit,
                            'company_id'         : self.company_id.id,
                            'date'               : date,
                            'date_maturity'      : date
                        }))
                    
                    payment_move = payment_move.sudo().create({
                    "partner_id": self.order_id.partner_id.id,
                    'move_type':'entry',
                    "journal_id": self.ajuan_id.pencairan_id.journal_id.id,
                    "ref": self.ajuan_id.pencairan_id.name,
                    "date": date,
                    "company_id": self.env.company.id,
                    })
                    if payment_move:
                        payment_id = self.env['account.payment'].create({
                            'payment_type': 'outbound',
                            'partner_type': 'supplier',
                            'partner_id': self.order_id.partner_id.id,
                            'journal_id': self.ajuan_id.pencairan_id.journal_id.id,
                            'destination_account_id' : destination_account_id,
                            'amount': self.order_id.amount_total,
                            'company_id': self.env.company.id,
                            'move_id' : payment_move.id
                            })
                        
                        payment_id.action_post()
                        self.ensure_one()
                        lines = payment_id.move_id.line_ids.filtered(lambda x:x.debit > 0)
                        self.bill_id.js_assign_outstanding_line(lines.id)
                        self.is_reconciled = True
                    
            elif self.sisa_penyelesaian > 0:
                for move in self.ajuan_id.pencairan_id.journal_entry_ids:
                    for move_line in move.line_ids.filtered(lambda x:x.account_id.id == dp_acount.id and x.debit > 0):
                        account_move_line.append(
                            (0,0,{'account_id'         : move_line.account_id.id,
                            #  'partner_id':self.order_id.partner_id.id,
                            'employee_id'         : self.ajuan_id.employee_id.id,
                            # 'analytic_account_id' : self.department_id.analytic_account_id.id or False,
                            'name'                : self.name,
                            'credit'              : move_line.debit,
                            'company_id'          : self.company_id.id,
                            'date'                : date,
                            'date_maturity'       : date})
                        )
            
            
                account_move_line.append((0,0,{
                'account_id'         : self.ajuan_id.pencairan_id.journal_id.payment_debit_account_id.id,
                # 'partner_id'         :self.order_id.partner_id.id,
                'employee_id'        : self.ajuan_id.employee_id.id,
                # 'analytic_account_id': self.department_id.analytic_account_id.id or False,
                'name'               : self.name,
                'debit'              : self.sisa_penyelesaian,
                'company_id'         : self.company_id.id,
                'date'               : date,
                'date_maturity'      : date
                }))
                
                
                account_move = account_move.sudo().create({
                    # "partner_id": self.order_id.partner_id.id,
                    'move_type':'entry',
                    "journal_id": self.ajuan_id.pencairan_id.journal_id.id,
                    "ref": self.ajuan_id.pencairan_id.name,
                    "date": date,
                    # "narration": me_id.notes,
                    "company_id": self.env.company.id,
                    "line_ids": account_move_line,
                })
                
                account_move.action_post()
                
                
                
                payment_move = self.env['account.move']
                payment_move_line = []
                
                
                if account_move:
                    for move_line in account_move.line_ids.filtered(lambda x:x.debit > 0):
                        payment_move_line.append((0,0,{
                            'account_id'         : move_line.account_id.id,
                            # 'partner_id'         :self.order_id.partner_id.id,
                            'employee_id'        : self.ajuan_id.employee_id.id,
                            # 'analytic_account_id': self.department_id.analytic_account_id.id or False,
                            'name'               : self.name,
                            'credit'              : move_line.debit,
                            'company_id'         : self.company_id.id,
                            'date'               : date,
                            'date_maturity'      : date
                        }))
                    
                    for move_line in self.bill_id.line_ids.filtered(lambda x:x.credit > 0):
                        destination_account_id = move_line.account_id.id
                        payment_move_line.append((0,0,{
                            'account_id'         : move_line.account_id.id,
                            'partner_id'         :self.order_id.partner_id.id,
                            'employee_id'        : self.ajuan_id.employee_id.id,
                            # 'analytic_account_id': self.department_id.analytic_account_id.id or False,
                            'name'               : self.name,
                            'debit'              : move_line.credit,
                            'company_id'         : self.company_id.id,
                            'date'               : date,
                            'date_maturity'      : date
                        }))
                    
                    payment_move = payment_move.sudo().create({
                    "partner_id": self.order_id.partner_id.id,
                    'move_type':'entry',
                    "journal_id": self.ajuan_id.pencairan_id.journal_id.id,
                    "ref": self.ajuan_id.pencairan_id.name,
                    "date": date,
                    "company_id": self.env.company.id,
                    })
                    if payment_move:
                        payment_id = self.env['account.payment'].create({
                            'payment_type': 'outbound',
                            'partner_type': 'supplier',
                            'partner_id': self.order_id.partner_id.id,
                            'journal_id': self.ajuan_id.pencairan_id.journal_id.id,
                            'destination_account_id' : destination_account_id,
                            'amount': self.order_id.amount_total,
                            'company_id': self.env.company.id,
                            'move_id' : payment_move.id
                            })
                        
                        payment_id.action_post()
                        self.ensure_one()
                        lines = payment_id.move_id.line_ids.filtered(lambda x:x.debit > 0)
                        self.bill_id.js_assign_outstanding_line(lines.id)
                        self.is_reconciled = True
                    
                
    
    @api.onchange('bop_type')
    def onchange_bop_type(self):
        if self.type == 'pengajuan':
            self.warehouse_ids = False
            self.jalur_ids = False
            if self.bop_type != 'kombinasi':
                self.template_comb_id = False 
            
            
                
    
    def button_reconcile(self):
        
        if self.type == 'penyelesaian' and self.bank_statement_id and self.bank_statement_id.state == 'open' and not self.is_reconciled:
            self.bank_statement_id.button_post()
            if self.bank_statement_id.state == 'posted':
                return {
                        "type": "ir.actions.client",
                        "tag": "bank_statement_reconciliation_view",
                        "context": {
                            "is_uudp": True,
                            "is_penyelesaian": True,
                            'account_id':self.ajuan_id.coa_debit.id,
                            "penyelesaian_id":self.id,
                            "payment_type":'inbound',
                            "statement_line_ids": self.bank_statement_id.line_ids.ids,
                            "company_ids": self.bank_statement_id.mapped("company_id").ids,
                        },
                    }
        elif self.bank_statement_id.state == 'posted':
            return {
                    "type": "ir.actions.client",
                    "tag": "bank_statement_reconciliation_view",
                    "context": {
                        "is_uudp": True,
                        "is_penyelesaian": True,
                        'account_id':self.ajuan_id.coa_debit.id,
                        "penyelesaian_id":self.id,
                        "payment_type":'inbound',
                        "statement_line_ids": self.bank_statement_id.line_ids.ids,
                        "company_ids": self.bank_statement_id.mapped("company_id").ids,
                    },
                }
        
            
    
    
    def button_confirm_knd(self):
        if self.env.user.has_group('vit_uudp.group_manager_uudp_approve_knd') or self.env.user.has_group('base.group_system'):
            self.state = 'confirm_knd'
            self.knd_approved = True
    

    def button_confirm_finance(self):
        if self.need_approve and not self.knd_approved:
            return self.write({'state':'confirm_department2'})
        
        
        if self.uudp_ids:
            account = self.env['account.account'].sudo()
            for s in self.uudp_ids:
                if not s.product_id :
                    raise UserError(_('Product dengan deskripsi %s belum di set!')%(s.description))
                # if self.type == 'penyelesaian' and self.sisa_penyelesaian > 0.0 and not self.difference:
                #     raise UserError(_('Jika ada sisa penyelesaian, difference account harus diisi !'))
                # if self.type == 'penyelesaian' and round(self.sisa_penyelesaian,2) > 0.0 :
                #     raise UserError(_('Selisih harus dimasukan ke piutang uudp !'))
                # elif s.product_id.property_account_expense_id:
                #     uudp_account = account.sudo().search([('code','=',s.product_id.property_account_expense_id.code),
                #                                             ('company_id','=',self.company_id.id)],limit=1)
                #     if not uudp_account :
                #         raise UserError(_('Tidak ditemukan kode CoA %s pada company %s !') % (s.product_id.property_account_expense_id.code,self.company_id.name))
                #     self.write({'coa_debit': uudp_account.id})
                ########################################################################
                ### 
                ### property_account_creditor_price_difference_categ tidak ada
                ### 
                ########################################################################
                # elif s.product_id.categ_id.property_account_creditor_price_difference_categ:
                #     uudp_account = account.search([('code','=',s.product_id.categ_id.property_account_creditor_price_difference_categ.code),
                #                                     ('company_id','=',self.company_id.id)],limit=1)
                #     if not uudp_account :
                #         raise UserError(_('Tidak ditemukan kode CoA %s pada company %s !') % (s.product_id.categ_id.property_account_creditor_price_difference_categ.code,self.company_id.name))
                #     self.write({'coa_debit': uudp_account.id})
                else:
                    if not s.coa_debit :
                        raise UserError(_('Account atas deskipsi %s belum di set!')%(s.description))
            self.write_state_line('confirm_finance')
            # self.post_mesages_uudp('Confirmed by Finance')
            # if self.name == _('New'):
            #     self.name = self._get_identifier(self.type)
            return self.write({'state' : 'confirm_finance'})
        raise AccessError(_('Pengajuan masih kosong') )

    def button_confirm_accounting(self):
        if self.uudp_ids:
            if self.type != 'pengajuan' :
                account_debit = self.uudp_ids.filtered(lambda x: not x.coa_debit)
                if account_debit :
                    raise UserError(_('Salah satu account lines belum di set!'))
            self.write_state_line('confirm_accounting')
            # self.post_mesages_uudp('Confirmed by Accounting')
            return self.write({'state' : 'confirm_accounting'})
        raise AccessError(_('Pengajuan masih kosong'))

    def button_validate(self):
        self.ensure_one()
        total_ajuan = 0.0
        now = datetime.datetime.now()
        # partner = self.responsible_id.partner_id.id
        employee = self.employee_id.id
        if self.state != 'confirm_accounting' or not self.pencairan_id:
            raise AccessError(_('Ajuan %s belum confirm accounting atau belum dijadwalkan pencairan!') % (self.name))

        reference =  self.name+ ' - ' + self.pencairan_id.name 
        account_move = self.env['account.move']
        datas_form = {'state' : 'done'}
        # cek jika journal sdh di create
        journal_exist = account_move.sudo().search([('ref','=',reference)])
        if not journal_exist :
            account_move_line = []
            for juan in self.uudp_ids :
                if juan.uudp_id.employee_id:
                    employee = juan.uudp_id.employee_id.id
                tag_id = False
                if juan.store_id and juan.store_id.account_analytic_tag_id :
                    tag_id = [(6, 0, [juan.store_id.account_analytic_tag_id.id])]
                if self.type == 'pengajuan' :
                    debit = self.coa_debit
                    if not debit :
                        raise AccessError(_('Debit acount pada ajuan %s belum diisi !') % (self.name) )
                else :
                    debit = juan.coa_debit
                    if not debit :
                        raise AccessError(_('Debit Account lines pada ajuan %s belum diisi !') % (self.name) )
                #account debit
                if juan.sub_total > 0.0 :
                    account_move_line.append((0, 0 ,{'account_id'       : debit.id,
                                                    # 'partner_id'        : partner,
                                                    'employee_id'        : employee,
                                                    'analytic_account_id' : self.department_id.analytic_account_id.id or False,
                                                    'analytic_tag_ids'  : tag_id,
                                                    'name'              : juan.description,
                                                    'debit'             : juan.sub_total,
                                                    'company_id'        : self.company_id.id,
                                                    'date'              : self.pencairan_id.tgl_pencairan,
                                                    'date_maturity'     : self.pencairan_id.tgl_pencairan}))
                elif juan.sub_total < 0.0 :
                    account_move_line.append((0, 0 ,{'account_id'       : debit.id,
                                                    'employee_id'        : employee,
                                                    # 'partner_id'        : partner,
                                                    'analytic_account_id' : self.department_id.analytic_account_id.id or False,
                                                    'analytic_tag_ids'  : tag_id,
                                                    'name'              : juan.description,
                                                    'credit'            : -juan.sub_total,
                                                    'date'              : self.pencairan_id.tgl_pencairan,
                                                    'company_id'        : self.company_id.id,
                                                    'date_maturity'     : self.pencairan_id.tgl_pencairan}))
                #account credit bank / hutang
                notes = self.notes
                if not notes :
                    notes= self.coa_kredit.name
            account_move_line.append((0, 0 ,{'account_id'       : self.pencairan_id.coa_kredit.id,
                                            'employee_id'        : self.employee_id.id,
                                            # 'partner_id'        : self.responsible_id.partner_id.id,
                                            'analytic_account_id' : self.department_id.analytic_account_id.id or False,
                                            'name'              : notes,
                                            'credit'            : self.total_ajuan,
                                            'company_id'        : self.company_id.id,
                                            'date'              : self.pencairan_id.tgl_pencairan,
                                            'date_maturity'     : self.pencairan_id.tgl_pencairan}))

            data={"journal_id": self.pencairan_id.journal_id.id,
                  "ref": reference,
                  "date": self.pencairan_id.tgl_pencairan,
                  "company_id": self.company_id.id,
                  "narration": self.pencairan_id.notes,
                  "terbilang" : terbilang.terbilang(int(round(self.total_ajuan,0)), "IDR", "id"),
                  "line_ids":account_move_line,}

            journal_entry = account_move.create(data)
            journal_entry.post()
            datas_form.update({'journal_entry_id' : journal_entry.id})

        # self.post_mesages_uudp('Done')
        return self.write(datas_form)

    def button_confirm_hrd(self):
        self.write_state_line('confirm_hrd')
        # self.post_mesages_uudp('Confirmed by HRD')
        return self.write({'state' : 'confirm_hrd'})

    def button_cancel(self):
        self.ensure_one()
        self.write_state_line('cancel')
        if self.pr_ids:
            for pr in self.pr_ids:
                pr.sudo().write({"ajuan_id":False})
        
        if self.type == 'penyelesaian':
            journal_entry_ids = self.env['account.move'].sudo().search([('uudp_penyelesaian_id','=',self.id),("ref",'!=',self.name)])
            for journal in journal_entry_ids:
                    journal.button_draft()
                    journal.with_context(force_delete=True).unlink()
            
            if self.bank_statement_id:
                self.bank_statement_id.button_reopen()
                self.bank_statement_id.unlink()
                
            # if journal_entry_ids and not self.bank_statement_id:
            #     for journal in journal_entry_ids:
            #             journal.button_draft()
            #             journal.with_context(force_delete=True).unlink()
            
            total_realisasi = sum(self.uudp_ids.mapped('sub_total'))
            self.sisa_penyelesaian = self.total_ajuan_penyelesaian - total_realisasi
            # self._get_detail_ajuan()
                
        if self.pencairan_id and self.pencairan_id.state == 'done' and self.type != 'penyelesaian':
            raise UserError('Mohon maaf ajuan sudah di cairkan di %s'%(self.pencairan_id.name))
      
        if self.tgl_pencairan and self.total_pencairan and self.type == 'pengajuan':
            self.total_pencairan = 0
            self.tgl_pencairan = False
            
        if self.selesai_id and self.selesai_id.state == 'done':
            raise UserError('Mohon maaf ajuan sudah di buat penyelesaian di %s'%(self.selesai_id.name))
            
        
                
        # if self.rute_id:
        #     self.rute_id.sudo().write({'ajuan_id':False})
        if self.need_approve:
            self.knd_approved = False
        # self.post_mesages_uudp('Canceled')
        self.write({'state' : 'cancel'})
        if self.type == 'penyelesaian' and self.ajuan_id:
            self.ajuan_id.selesai = False
            self.ajuan_id.tgl_penyelesaian = False
            if self.bank_statement_id:
                self.bank_statement_id.button_reopen()
                self.bank_statement_id.unlink()
            self.journal_entry_id.sudo().button_draft()
            self.journal_entry_id.sudo().with_context(force_delete=True).unlink()
    

    def button_set_to_draft(self):
        self.write_state_line('draft')
        return self.write({'state' : 'draft'})

    def button_refuse(self):
        self.write_state_line('refuse')
        # self.post_mesages_uudp('Refused')
        return self.write({'state' : 'refuse'})

    def button_refuse_finance(self):
        self.write_state_line('refuse')
        # self.post_mesages_uudp('Refused')
        return self.write({'state' : 'refuse'})

    
    
    
    @api.onchange('ajuan_id')
    def _get_detail_ajuan(self):
        ajuan = self.ajuan_id
        if ajuan:
            self.uudp_ids = False
            self.total_ajuan = ajuan.total_pencairan
            self.total_pencairan = ajuan.total_pencairan
            self.employee_id = ajuan.employee_id.id
            self.cara_bayar = ajuan.cara_bayar
            self.bank_id = ajuan.bank_id.id
            self.no_rekening = ajuan.no_rekening
            self.coa_kredit = ajuan.coa_debit.id
            
            if self.type == 'penyelesaian':
                self.category_id = self.ajuan_id.category_id.id
                if self.category_id.name == 'PEMBELIAN':
                    self.order_id = self.ajuan_id.order_id.id if self.ajuan_id.order_id else False
                    
                if self.is_rute_sale:
                    self.vehicle_id = self.ajuan_id.vehicle_id.id
                    self.bop_type = self.ajuan_id.bop_type
                    self.driver_id = self.ajuan_id.driver_id.id
                    self.kasir_id = self.ajuan_id.kasir_id.id
                    self.sales_id = self.ajuan_id.sales_id.id
                    self.vehicle_type = self.ajuan_id.vehicle_type
                    self.helper_id = self.ajuan_id.helper_id.id
                    self.employee_id = self.ajuan_id.employee_id.id
                    self.end_date  = self.ajuan_id.end_date
                    self.warehouse_ids = [(6,0,self.ajuan_id.warehouse_ids.ids)]
                    self.jalur_ids = [(6,0,self.ajuan_id.jalur_ids.ids)]
                uudp_ids = []
                for juan in self.ajuan_id.uudp_ids:
                    if self.state == 'draft':
                        uudp_ids.append([0,0,{
                                            'product_id'    :juan.product_id.id,
                                            'exp_id'        :juan.exp_id.id,
                                            'coa_debit'     : juan.coa_debit.id,
                                            'description'   : juan.description,
                                            'qty'           : juan.qty,
                                            'uom'           : juan.uom,
                                            'unit_price'    : juan.unit_price,
                                            'state'         : 'draft',
                                            }])
                self.uudp_ids = uudp_ids
                self.coa_kredit = self.coa_debit.id
                self.department_id = self.ajuan_id.department_id.id
           

                    

    @api.onchange('employee_id')
    def _get_department(self):
        responsible = self.employee_id.id
        if responsible:
            # department = self.env['hr.employee'].search([('user_id', '=', responsible)], limit=1).department_id.id
            self.department_id = self.employee_id.department_id.id

    def unlink(self):
        for data in self:
            if data.state != 'draft':
                raise UserError(_('Data yang bisa dihapus hanya yang berstatus draft !'))
            else:
                attachment = self.env['ir.attachment'].search([('res_model','=','uudp'),('res_id','=',data.id)])
                if attachment:
                    for a in attachment:
                        a.unlink()
        return super(uudp, self).unlink()

    def print_pencairan(self):
        view_id = self.env.ref('vit_uudp.view_print_pencairan_wizard').id
        return {
            'name': _('Pencairan Details'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.print.pencairan',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': self.env.context}

    def alert_uudp_penyelesaian(self, *args):
        """ fungsi di overide di addons vit_uudp+pencairan"""
        return True


uudp()


class uudpDetail(models.Model):
    _name = "uudp.detail"
    _inherit = ['mail.thread']

    uudp_id = fields.Many2one("uudp", string="Nomor UUDP", track_visibility='onchange',)
    product_id = fields.Many2one("product.product", string="Product", track_visibility='onchange',)
    parent_coa_id = fields.Many2one(related='product_id.parent_coa_id', string='Parent COA ID',store=True,)
    # rute_id           = fields.Many2one('rute.sale', string='Rute Sale')
    do_id               = fields.Many2one('do.head.office', string='DO')
    partner_id = fields.Many2one("res.partner", string="Partner", track_visibility='onchange')
    store_id = fields.Many2one("res.partner", string="Store", track_visibility='onchange')
    description = fields.Char(string="Description", required=True, track_visibility='onchange',)
    qty = fields.Float(string="Qty", required=True, default=1, track_visibility='onchange',)
    uom = fields.Char(string="Satuan", required=True, track_visibility='onchange', default="Pcs")
    unit_price = fields.Float(string="Unit Price", required=True, default=0, track_visibility='onchange',)
    sub_total = fields.Float(string="Sub Total", compute="_calc_sub_total", store=True)
    total = fields.Float(string="Total", track_visibility='onchange',)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting Department'),
                              ('confirm_department', 'Confirmed Department'),
                              ('confirm_department1', 'Waiting HRD'),
                              ('confirm_hrd', 'Confirmed HRD'),
                              ('pending', 'Pending'),
                              ('confirm_finance', 'Confirmed Finance'),
                              ('confirm_accounting', 'Confirmed Accounting'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled'),
                              ('refuse','Refused')], default='draft', required=True, index=True, track_visibility='onchange',)
    coa_debit           = fields.Many2one('account.account', string="Account", track_visibility='onchange')
    # template_id         = fields.Many2one('rute.sale.expense.template', string='Template')
    # template_line_ids   = fields.One2many('Detail',related="template_id.line_ids")
    # template_line_ids   = fields.One2many('Detail',)
    is_different        = fields.Boolean(string='Different ?',compute="_get_differential")
    exp_id              = fields.Many2one('rute.sale.expense', string='Expense')


    
    def _get_differential(self):
        for line in self:
            if line.uudp_id.type == 'penyelesaian':
                ajuan = sum(line.uudp_id.ajuan_id.uudp_ids.filtered(
                    lambda x:line.uudp_id.ajuan_id.id == x.uudp_id.id and 
                    x.sub_total == line.sub_total and 
                    x.product_id.id == line.product_id.id and
                    x.coa_debit == line.coa_debit)
                    .mapped('sub_total'))
                line.is_different =  line.sub_total != ajuan
            else:
                line.is_different = False
    

    @api.onchange('product_id')
    def _get_product_detail(self):
        product = self.product_id
        if product:
            #self.description = p.name
            if not self.uom :
                self.uom = product.uom_id.name
            if self.unit_price == 0.0 :
                self.unit_price = product.lst_price
            # if not self.coa_debit :
            self.coa_debit = product.property_account_expense_id.id


    @api.depends('qty','unit_price')
    def _calc_sub_total(self):
        for i in self:
            qty = i.qty
            price = i.unit_price
            sub_total = qty * price
            i.sub_total = sub_total
            i.total = sub_total

    @api.model
    def create(self, vals):
        #import pdb;pdb.set_trace()
        if vals.get('qty') == 0.0 or vals.get('unit_price') == 0.0:
            raise ValidationError(_("Unit price tidak boleh di isi 0 !"))
        return super(uudpDetail, self).create(vals)

uudpDetail()
