from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    
    
    surat_jalan_id = fields.Many2one('pull.cron.sj', string='Surat Jalan')
    om_lama = fields.Boolean('OM Lama', default=False, copy=False)
    order_polos = fields.Boolean('Order Polos', default=False, copy=False)
    
    def open_print_inv_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Print Invoice',
            'res_model': 'print.invoice.wizard',
            'context': {'default_move_id':self.id,'default_print_type':'yard'},
            'view_mode': 'form',
            'target': 'new',
        }
        
        
    
    
    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.surat_jalan_id:
            self.surat_jalan_id.sudo().write({"is_invoiced":True})
        return res
    
    
    @api.onchange('surat_jalan_id')
    def onchange_sj(self):
        self.invoice_line_ids = False
        self.line_ids = False
        line_ids = []
        for loop_sj in self.surat_jalan_id:
            self.invoice_date   = loop_sj.tanggal
            self.date   = loop_sj.tanggal
            self.x_pro_no_sj    = loop_sj.name
        for idx,line in  enumerate(self.surat_jalan_id.line_ids):
            if idx == 0:
                greige_id = self.env['product.product'].search([('default_code','=',line.kd_brg)],limit=1)
                if not greige_id:
                    greige_id = self.env['product.product'].create({
                        "name":line.nama_barang,
                        "default_code":line.kd_brg,
                        "type":"product",
                        "categ_id":44,
                        "uom_id":46,
                        "uom_po_id":46,
                        "tracking":"lot",
                        "sale_ok":True,
                    })
                    
                customers = self.env['res.partner'].sudo().search([('ref','=',line.kd_plg)],limit=1)
                if customers:
                    self.partner_id = customers.id
                elif not customers and line.kd_plg and line.nama_pelanggan:
                    customers = self.env['res.partner'].sudo().create({
                        "name":line.nama_pelanggan,
                        "ref": line.kd_plg,
                        "property_stock_customer": 5,
                        "property_stock_supplier": 4,
                        "property_account_receivable_id": 10659,
                        "property_account_payable_id": 10821,
                        "property_product_pricelist": 1,
                        "lang":"en_US",
                        "company_type":"company",
                        "street":line.alamat,
                    })
                    
                    self.partner_id = customers.id
            
            # if self.partner_id and not self.partner_id.over_credit and self.partner_id.total_overdue > 0:            
                # raise UserError('Customer has invoices that are overdue')
            product = self.env['product.product'].search([('name','=',line.ket_om)],limit=1)
            if not product:
                product = self.env['product.product'].create({
                    "name":line.ket_om,
                    "type":"product",
                    "categ_id":45,
                    "uom_id":46,
                    "uom_po_id":46,
                    "gramasi_greige":line.gramasi_greige,
                    "lebar_greige":line.lebar_greige,
                    "gramasi_finish":line.gramasi_finish,
                    "lebar":line.lebar_finish,
                    "tracking":"lot",
                    "sale_ok":True,
                })
            else:
                product.sudo().write({
                    "gramasi_greige":line.gramasi_greige,
                    "lebar_greige":line.lebar_greige,
                    "gramasi_finish":line.gramasi_finish,
                    "lebar":line.lebar_finish,
                })
            # product = self.env['product.product'].search([('default_code','=',line.kd_brg)],limit=1)
            grade_id = self.env['makloon.grade'].sudo().search([('name','=',line.grade)],limit=1)

            uom_id = product.uom_id.id
            if product:
                if line.satuan:
                    if line.satuan.upper() == 'YARD':
                        uom_id = 46 # YARD 
                    elif line.satuan.upper() == 'MTR' or line.satuan.upper() == 'METER':
                        uom_id = 96 # METER
                    elif line.satuan.upper() == 'KG':
                        uom_id = 305 # kg

                # nomor_om = self.env['pull.cron.om'].sudo().search([('name','=',line.om)],limit=1)
                # if datetime.strptime(str(nomor_om.tanggal) +' 00:00:00', '%Y-%m-%d %H:%M:%S') >= datetime.strptime('2022-04-01 00:00:00', '%Y-%m-%d %H:%M:%S'):
                if self.move_id.om_lama == True:
                    harga_dpp = line.harga * 1.11 / 1.1
                else:
                    harga_dpp = line.harga
                
                line_ids.append((0,0,{
                    "product_id":product.id,
                    "name":product.name,
                    "greige_id":greige_id.id,
                    "quantity":line.quantity,
                    "product_uom_id":uom_id,
                    # "price_unit":line.harga,
                    "price_unit"    : round(harga_dpp, 2),
                    "harga_om"      : line.harga,
                    "warna":line.no_warna,
                    "total_roll":line.cone,
                    "recompute_tax_line":True,
                    "currency_id":self.env.company.currency_id.id,
                    # "tax_ids":[(6,0,[9])],
                    "tax_ids":[(6,0,[18])] if self.order_polos == False else [],
                    "account_id": grade_id.account_input_id.id if grade_id.account_input_id else product.categ_id.property_account_income_categ_id.id,
                    "grade_id":grade_id.id or False,
                    "date": line.pull_id.tanggal
                }))
    

        self.invoice_line_ids = line_ids
        if self.invoice_line_ids:
            self.invoice_line_ids._onchange_price_subtotal()
            self.invoice_line_ids._onchange_amount_currency()
            self.invoice_line_ids._compute_tax_line_id()
            self.invoice_line_ids._onchange_mark_recompute_taxes()
            self._recompute_dynamic_lines()
            self._synchronize_business_models({'line_ids'})
            self._recompute_tax_lines()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    
    warna           = fields.Char(string='Warna')
    grade_id        = fields.Many2one('makloon.grade', string='Grade')
    total_roll      = fields.Integer(string='Pcs')
    greige_id       = fields.Many2one('product.product', string='Greige')
    qty_kg          = fields.Float(compute='compute_conversion', string='On Kg', store=False)
    qty_meter       = fields.Float(compute='compute_conversion', string='On Meter', store=False)
    qty_yard        = fields.Float(compute='compute_conversion', string='On Yard', store=False)
    harga_om        = fields.Float(string='Harga OM')
    
    @api.depends('quantity')
    def compute_conversion(self):
        for line in self:
            if line.product_uom_id:
                if line.product_uom_id.name.lower() == 'yard' \
                    and (line.product_id.categ_id.name == 'KAIN' \
                    or line.product_id.categ_id.name == 'Finish Good'):
                    line.qty_kg = (line.product_id.gramasi_greige / 1000) *  line.quantity if line.product_id.gramasi_greige else 0
                    line.qty_meter = line.quantity * 0.9144
                    line.qty_yard = line.quantity
                elif (line.product_uom_id.name.lower() == 'meter' or line.product_uom_id.name.lower() == 'mtr') \
                    and (line.product_id.categ_id.name == 'KAIN' \
                    or line.product_id.categ_id.name == 'Finish Good'):
                    line.qty_meter = line.quantity
                    line.qty_yard = line.quantity / 0.9144
                    line.qty_kg = ((line.quantity / 0.9144 )* line.product_id.gramasi_greige) / 1000 if line.product_id.gramasi_greige else 0
                elif line.product_uom_id.name.lower() == 'kg':
                    line.qty_meter = (line.quantity * 1000 / line.product_id.gramasi_greige) * 0.9144 if line.product_id.gramasi_greige else 0
                    line.qty_yard = line.quantity * 1000 / line.product_id.gramasi_greige if line.product_id.gramasi_greige else 0
                    line.qty_kg = line.quantity
                else:
                    line.qty_kg = 0
                    line.qty_meter = 0
                    line.qty_yard = 0
            else:
                line.qty_kg = 0
                line.qty_meter = 0
                line.qty_yard = 0
    
    