from requests.sessions import default_hooks
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    no_komunikasi           = fields.Char(string="No Komunikasi")
    remarks                 = fields.Char(string='Remarks')
    kode_barang             = fields.Char(string='Kode Barang', related='product_id.default_code')
    qty_released            = fields.Float(string='Released',
    #  compute='_compute_qty_released',
      digits=(12,5))
    f_discount              = fields.Float(string='Discount', store=True,)
    qty_sisa                = fields.Float(string='Qty Sisa', compute='_compute_qty_sisa',)
    box                     = fields.Integer(string='Box')
    cones                   = fields.Integer(string='Cones')
    lot_id                  = fields.Many2one('stock.production.lot', string='Lot',)
    specifications          = fields.Text(string="Specifications", required=True, )
    date_order              = fields.Datetime(string='Date', related='order_id.date_order')
    grade_id                = fields.Many2one('makloon.grade', string='Grade')
    # purchase_request_id     = fields.Many2one('purchase.request', string='Purchase Request', related='purchase_request_lines.request_id')
    image_ids           = fields.One2many('insert.image', 'purchase_line_id', string='Image')
    is_receipt_done      = fields.Boolean(string='Is Receipt Done',compute='_compute_receipt')

    
    def _compute_receipt(self):
        for order in self:
            order.is_receipt_done = sum(order.mapped('qty_received')) >= sum(order.mapped('product_qty'))
            if order.is_receipt_done:
                order.purchase_request_id.sudo().button_done()
                
            
    
    
    @api.onchange('lot_id')
    def onchange_product(self):
        self.product_id = self.lot_id.product_id.id
        
    @api.onchange('product_id')
    def ganti_lot(self):
        if self.product_id:
            self.lot_id = False
            return {
                'domain': {'lot_id': [('product_id', '=', self.product_id.id)]},
                }
    
    

    def _prepare_account_move_line(self):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line()
        data = []
        for rec in self.order_id.picking_ids.filtered(lambda x: x.state == 'done' and x.is_invoiced != True):
            for rec2 in rec.move_ids_without_package:
                for rec3 in rec2.image_ids:
                    if res.get('product_id') == rec2.product_id.id:
                        data.append((0, 0, {
                            'filename' : '%s%s' % (rec3.id, rec3.format_file),
                            'image_desc' : rec3.image_desc,
                        }))
            rec.write({'is_invoiced' : True})
        res['image_ids'] = data
        return res

    def _compute_qty_sisa(self):
        for rec in self:
            rec.qty_sisa = rec.product_qty - rec.qty_received

    def _compute_qty_released(self):
        for a in self:
            picking_obj = self.env['stock.picking'].search([('purchase_id_2', '=', a.order_id.id), ('state', '=', 'done')]).move_line_ids_without_package.filtered(lambda x:x.product_id.id == a.product_id.id).mapped('qty_done')
            a.qty_released = sum(picking_obj)

    def action_show_image(self):
        action = self.env.ref('inherit_purchase_order.purchase_order_action').read()[0]
        action['res_id'] = self.id
        action['name'] = "Images of %s" % (self.product_id.name)
        return action