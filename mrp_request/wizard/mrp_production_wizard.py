from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from odoo.tools.float_utils import float_round, float_is_zero
_logger = logging.getLogger(__name__)




class MrpGenerateProductionWizard(models.TransientModel):
    _name = 'mrp.generate.production.wizard'
    _description = 'Generate Manufacture Order Based on Estimated'


    mrp_request_id     = fields.Many2one('mrp.request',string='Mrp Request')
    estimated_id       = fields.Many2one('mrp.production.estimated', string='Estimated')
    mo_outstanding_qty = fields.Float(string='Outstanding Qty')
    product_id         = fields.Many2one(related='estimated_id.product_id', string='Product')
    production_qty     = fields.Float(related='estimated_id.production_qty', string='Quantity Request')
    product_uom_qty    = fields.Float(related='estimated_id.product_uom_qty', string='Quantity Conversi')
    satuan_id          = fields.Many2one(related='estimated_id.satuan_id', string='Satuan Produksi')
    product_uom_id     = fields.Many2one(related='estimated_id.product_uom_id', string='Satuan')
    mo_count           = fields.Integer(string='Jumlah Kartu',default=1)
    mo_qty             = fields.Float(string='Quantity MO')
    konversi_butir     = fields.Float(related='product_id.konversi_butir', string='Butir')
    konversi_bungkus   = fields.Float(related='product_id.konversi_bungkus', string='Bungkus')
    product_qty_conv   = fields.Float(string='Hasil Conv')
    
    
    @api.onchange('mo_qty')
    def get_conv_quantit(self):
        self.product_qty_conv = self.mo_qty * self.konversi_butir if self.mo_qty > 0 and self.konversi_butir > 0  else 0 

   
    
    @api.depends('mo_count','mo_qty')
    def _get_conv_quantity(self):
            # line.product_uom_qty = sum(line.request_id.order_lines.filtered(lambda l: l.product_id.id == line.product_id.id).mapped('quantity'))
        self.product_qty_conv = self._origin.mo_qty / self._origin.konversi_butir if self._origin.mo_qty > 0 and self._origin.konversi_butir > 0  else 0 
    
    # est_production_qty = fields.Float(compute='_compute_outstanding', string='Estimasi Sisa', store=False)
    
    # @api.depends('mo_count','mo_qty')
    # def _compute_outstanding(self):
    #     for order_doc in self:
    #         amount_total = sum(order_doc.line_ids.mapped('price_total'))
    #         order_doc.amount_total = amount_total
    
    
    
    @api.model
    def default_get(self,fields):
        res = super(MrpGenerateProductionWizard,self).default_get(fields)
        context = self._context
        active_id = context.get('active_id')
        if active_id and context.get('active_model') == 'mrp.production.estimated':
            estimated_id = self.env['mrp.production.estimated'].browse(active_id)
            res['estimated_id'] = estimated_id.id
            res['mrp_request_id'] = estimated_id.request_id.id
            res['mo_outstanding_qty'] = estimated_id.production_outstanding_qty
        return res
    
    
    def do_generate(self):
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        if float_is_zero(self.mo_qty,precision_digits=precision_digits):
            raise UserError('Mohon maaf pastikan mo quantity tidak nol')
        for mo in range(self.mo_count):
            picking_type_id = None  if not self.estimated_id.type_id else self.estimated_id.type_id.picking_type_id.id if self.estimated_id.type_id.picking_type_id else None
            product_categ_id = self.product_id.categ_id
            if product_categ_id.id == 35:
                picking_type_id =   248
            elif product_categ_id.id == 40:
                picking_type_id =   256
            
            bom_id          = self.env['mrp.bom'].search([('product_tmpl_id','=',self.product_id.product_tmpl_id.id)],limit=1)
            picking_type_id = self.env['stock.picking.type'].sudo().browse(picking_type_id)
            production_id = self.env['mrp.production'].create({
                    'product_id':self.product_id.id,
                    'type_id':self.estimated_id.type_id.id,
                    'product_uom_id':self.product_id.uom_id.id,
                    'mrp_qty_produksi':self.mo_qty,
                    'bom_id': bom_id.id if bom_id else False,
                    'satuan_id':self.satuan_id.id,
                    'picking_type_id': picking_type_id.id,
                    'origin':self.mrp_request_id.name,
                    'location_src_id': picking_type_id.default_location_src_id.id,
                    'location_dest_id':picking_type_id.default_location_dest_id.id,
                    'date_planned_start':self.estimated_id.production_date,
                    'request_id':self.mrp_request_id.id,
                    'product_qty':self.product_qty_conv
                })
            
            self.estimated_id.sudo().write({
                "production_ids":[(4,production_id.id)]
            })
            
            
            
            
    
    
    
    
    