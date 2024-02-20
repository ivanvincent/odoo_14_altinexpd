from odoo import fields, models, api, _

class SendProductionWizard(models.TransientModel):
    _name = 'send.production.wizard'
    
    line_ids = fields.One2many('detail.specification.mo', 'wizard_id', string='Detail')


    def create_mo(self):
        # data = []
        # print("===========================", mo_id)
        for l in self.line_ids.filtered(lambda x:x.create_mo == True):
            product = self.env['product.product'].search([('name','=',l.name)],limit=1)
            if not product :
                product = self.env['product.product'].create({
                    "name":l.name,
                    "type":"product",
                    # "product_tmpl_id":line.name,
                    "categ_id": 27, #category : Finished Goods
                })

            mo_id = self.env['mrp.production'].create({       
                # 'name'          : self.name.replace("Q","SO"),
                'dqups_id'      : l.qrf_id.id,    
                # 'type_id'       : 2,                
                'product_id'    : product.id,
                'product_qty'   : l.quantity,
                'mrp_qty_produksi'  : l.quantity,
                'billing_address'   : l.qrf_id.billing_address,
                'shipping_address'  : l.qrf_id.shipping_address.id,
                'product_uom_id': 1,
                'partner_id': l.qrf_id.partner_id.id, 
                'ref_so_id' : l.qrf_id.so_id.id  
            })

            qrf_line_id = self.env['quotation.request.form.line'].search([()])write({
                'mo_id' : mo_id.id
            })
            print("===========================", l.qrf_id.id)

class DetailSpecificationMo(models.TransientModel):
    _name = 'detail.specification.mo'

    wizard_id = fields.Many2one('send.production.wizard', string="wizard")
    qrf_id = fields.Many2one('quotation.request.form', string='QRF')
    jenis_id = fields.Many2one('master.jenis', string='Jenis')
    # line_spec_ids = fields.One2many('quotation.request.form.line.specification', 'qrf_line_id', 'Line Spec')
    name = fields.Char(string='Description')
    quantity = fields.Integer(string='Quantity')
    mo_id = fields.Many2one('mrp.production', string="MO")
    mo_count = fields.Integer(string='MO Count')
    create_mo = fields.Boolean(string="Create MO", default=False)
    qrf_line_id = fields.Many2one('quotation.request.form.line', string="QRF Line")