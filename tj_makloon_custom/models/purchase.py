# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    type_id = fields.Selection([('umum', 'Umum'),('beligreige', 'BeliGreige'),('belikain', 'BeliKain'),('benang', 'Benang'),('rajut', 'Rajut'), ('celup', 'Celup'),('# printing', '# printing'),],string="Operation Type",)
    makloon_plan_id = fields.Many2one('makloon.planning', string="Makloon Plan")
    contact_id = fields.Many2one('res.partner', 'Contact',
                                 domain="[('parent_id','=',partner_id)]")
    partner_contact = fields.Many2one('res.partner.contact.list', 'Contact Person')

    attn_id = fields.Many2one('attn', string='Contact Person')
    alamat  = fields.Text(string='Alamat', related='attn_id.alamat')
    kota    = fields.Char(string='Kota', related='attn_id.kota')
    phone   = fields.Char(string='Phone', related='attn_id.phone')

    attn_ids = fields.Many2many('attn', string='Contact Person', compute='compute_attn_ids')

    categ_id = fields.Many2one('product.category')

    @api.depends('partner_id')
    def compute_attn_ids(self):
        for rec in self:
            if rec.partner_id:
                rec.attn_ids = [(6, 0, rec.partner_id.attn_ids.ids)]
            else:
                rec.attn_ids = False

    @api.model
    def create(self, vals):
        #res = super(PurchaseOrder, self).create(vals)
        #sequence = vals.get('name')
        ## print 'replace=>', sequence,',',vals.get('type_id')
        #if vals.get('type_id') == 'benang':
        #    sequence = sequence.replace('PO', 'POI-')
        #elif vals.get('type_id') == 'rajut':
        #    sequence = sequence.replace('PO', 'POII-')
        #elif vals.get('type_id') == 'celup':
        #    sequence = sequence.replace('PO', 'POIII-')
        #elif vals.get('type_id') == '# printing':
        #    sequence = sequence.replace('PO', 'POIV-')
        #res.write({'name': sequence,})
        #return res

        #sequence = vals.get('name')
        ## print 'replace=>', sequence,',',vals.get('type_id')
        if vals.get('type_id') == 'benang':
            seq_id = self.env.ref('tj_makloon_custom.seq_purchase_benang')
        elif vals.get('type_id') == 'rajut':
            seq_id = self.env.ref('tj_makloon_custom.seq_purchase_rajut')
        elif vals.get('type_id') == 'celup':
            seq_id = self.env.ref('tj_makloon_custom.seq_purchase_celup')
        elif vals.get('type_id') == '# printing':
            seq_id = self.env.ref('tj_makloon_custom.seq_purchase_# printing')
        elif vals.get('type_id') == 'umum':
            seq_id = self.env.ref('tj_makloon_custom.seq_purchase_umum')
        elif vals.get('type_id') == 'beligreige':
            seq_id = self.env.ref('tj_makloon_custom.seq_purchase_beligreige')
        else :
            seq_id = self.env.ref('tj_makloon_custom.seq_purchase_belikain')            
        vals['name'] = seq_id.next_by_id()
        return super(PurchaseOrder, self).create(vals)


    # @api.model
    #def create(self, vals):
    #    if vals.get('supplier',False):
    #        seq_id = self.env.ref('tj_base.seq_res_partner_supp')
    #    else :
    #        seq_id = self.env.ref('tj_base.seq_res_partner_cust')
    #    vals['ref'] = seq_id.next_by_id()
    #    return super(ResPartner, self).create(vals)    

    # @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        # makloon_order_obj = self.env['makloon.order'].search([('id','=',self.makloon_id)])
        makloon_result_obj = self.env['makloon.order.result'].search([('order_id', '=', self.makloon_id.id)])
        for rec in self:
            for line in rec.order_line:
                for line2 in makloon_result_obj:
                    # print line2.product_id.name, line.name
                    if line2.product_id.name == line.name:
                        line2.price_unit = line.price_unit
                        #line2.price_subtotal = line.price_subtotal
                        line2.price_subtotal = line2.product_uom_qty * line.price_unit
                    # print "1=>",line.product_id.id, line.price_unit, line.price_subtotal
        return res

    # # @api.multi
    # def write(self, vals):
    #     sequence = self.name
    #     # print self.name
    #     if self.type_id == 'benang':
    #         sequence = sequence.replace('PO', 'POI-').replace('POI-', 'POI-').replace('POII-', 'POI-').replace('POIII-', 'POI-')
    #     elif self.type_id == 'rajut':
    #         sequence = sequence.replace('PO', 'POII-').replace('POI-', 'POII-').replace('POII-', 'POII-').replace('POIII-', 'POII-')
    #         # print 'POII-', sequence
    #     elif self.type_id == 'celup':
    #         sequence = sequence.replace('PO', 'POIII-').replace('POI-', 'POIII-').replace('POII-', 'POIII-').replace('POIII-', 'POIII-')
    #     # print sequence
    #     self.name = sequence
    #     res = super(PurchaseOrder, self).write(vals)
    #     return res

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_type_line = fields.Selection([('umum', 'Umum'),('beligreige', 'BeliGreige'),('belikain', 'BeliKain'),('benang', 'Benang'), ('rajut', 'Rajut'), ('celup', 'Celup'),('# printing', '# printing')], string="Type", compute='_onchange_uom')
    product_merk_id = fields.Many2one('makloon.merk', 'Merk')
    product_setting_id = fields.Many2one('makloon.setting', 'Setting Jadi')
    product_gramasi_id = fields.Many2one('makloon.gramasi', 'Gramasi Matang')
    product_corak_id = fields.Many2one('makloon.corak', 'Corak')
    product_kg = fields.Float('KG',compute='_onchange_uom')
    product_resep_warna_id = fields.Many2one('makloon.resep.warna', 'Resep Warna')
    product_warna_id = fields.Many2one('makloon.warna', 'Warna')
    product_category_warna_id = fields.Many2one('makloon.category.warna', 'Category Warna')
    product_roll = fields.Integer(string='Roll', )
    roll_kg_id = fields.Many2one('makloon.roll', '@Kg', )
    price_include = fields.Float(string='Inc Price', )

    categ_id = fields.Many2one('product.category')
    
    # product_body_kg = fields.Integer(string='Body KG', )
    # product_kerah_roll = fields.Integer(string='Kerah Roll', )
    # product_kerah_kg = fields.Integer(string='Kerah KG', )
    # product_rib_roll = fields.Integer(string='Rib Roll', )
    # product_rib_kg = fields.Integer(string='Rib KG', )
    # product_manset_roll = fields.Integer(string='Manset Roll', )
    # product_manset_kg = fields.Integer(string='Manset KG', )

    @api.onchange('price_include')
    def onchange_price(self):
        for rec in self:
            if rec.price_include or rec.price_include > 0.0:
                rec.price_unit = (rec.price_include/1.1)
                # print "price=>",rec.price_unit, rec.price_include

    @api.onchange('product_resep_warna_id')
    def _onchange_resepwarna(self):
        for rec in self:
            if rec.product_resep_warna_id:
                if rec.product_resep_warna_id.warna_id:
                    rec.product_warna_id = rec.product_resep_warna_id.warna_id.id
                if rec.product_resep_warna_id.category_warna_id:
                    rec.product_category_warna_id = rec.product_resep_warna_id.category_warna_id.id
                # print rec.product_resep_warna_id.warna_id, rec.product_resep_warna_id.category_warna_id

    @api.onchange('product_qty', 'product_uom', 'order_id.type_id')
    @api.depends('product_qty', 'product_uom', 'order_id.type_id')
    def _onchange_uom(self):
        for rec in self:
            if rec.order_id.type_id:
                rec.product_type_line = rec.order_id.type_id
                if rec.product_uom:
                    if rec.product_uom.name.lower() in ['bal','bale'] and rec.order_id.type_id:
                        rec.product_kg = (rec.product_qty * 181.44)
                    elif rec.product_uom.name.lower() in ['kg','Kg','KG'] and rec.order_id.type_id:
                        rec.product_kg = (rec.product_qty * 1)
                    else:
                        rec.product_kg = 0
            else:
                rec.product_type_line = False

    # @api.onchange('order_id.operation_id','operation_name','product_id')
    # def _getCategory(self):
    #     for rec in self:
    #         if rec.order_id.operation_id:
    #             ids = []
    #             for child_id in rec.order_id.operation_id.order_line.child_ids:
    #                 ids.append(child_id.id)
    #                 # print child_id
    #                 # print ids
    #             domain = {'product_id': [('categ_id.id', 'in', ids),('textile_product','=',True)]}
    #         else:
    #             domain = {'product_id': [('categ_id.id', 'in', []),('textile_product','=',True)]}
    #         # print domain
    #         return {'domain': domain}